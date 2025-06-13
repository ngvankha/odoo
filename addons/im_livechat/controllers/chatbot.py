# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.tools import get_lang, is_html_empty, plaintext2html
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class LivechatChatbotScriptController(http.Controller):
    @http.route('/chatbot/restart', type="json", auth="public", cors="*")
    def chatbot_restart(self, channel_uuid, chatbot_script_id):
        chatbot_language = self._get_chatbot_language()
        mail_channel = request.env['mail.channel'].sudo().with_context(lang=chatbot_language).search([('uuid', '=', channel_uuid)], limit=1)
        chatbot = request.env['chatbot.script'].browse(chatbot_script_id)
        if not mail_channel or not chatbot.exists():
            return None

        return mail_channel._chatbot_restart(chatbot).message_format()[0]

    @http.route('/chatbot/post_welcome_steps', type="json", auth="public", cors="*")
    def chatbot_post_welcome_steps(self, channel_uuid, chatbot_script_id):
        mail_channel = request.env['mail.channel'].sudo().search([('uuid', '=', channel_uuid)], limit=1)
        chatbot_language = self._get_chatbot_language()
        chatbot = request.env['chatbot.script'].sudo().with_context(lang=chatbot_language).browse(chatbot_script_id)
        if not mail_channel or not chatbot.exists():
            return None

        return chatbot._post_welcome_steps(mail_channel).message_format()

    @http.route('/chatbot/answer/save', type="json", auth="public", cors="*")
    def chatbot_save_answer(self, channel_uuid, message_id, selected_answer_id):
        mail_channel = request.env['mail.channel'].sudo().search([('uuid', '=', channel_uuid)], limit=1)
        chatbot_message = request.env['chatbot.message'].sudo().search([
            ('mail_message_id', '=', message_id),
            ('mail_channel_id', '=', mail_channel.id),
        ], limit=1)
        selected_answer = request.env['chatbot.script.answer'].sudo().browse(selected_answer_id)

        if not mail_channel or not chatbot_message or not selected_answer.exists():
            return

        if selected_answer in chatbot_message.script_step_id.answer_ids:
            chatbot_message.write({'user_script_answer_id': selected_answer_id})

    @http.route('/chatbot/step/trigger', type="json", auth="public", cors="*")
    def chatbot_trigger_step(self, channel_uuid, chatbot_script_id=None):
        chatbot_language = self._get_chatbot_language()
        mail_channel = request.env['mail.channel'].sudo().with_context(lang=chatbot_language).search([('uuid', '=', channel_uuid)], limit=1)
        if not mail_channel:
            return None

        next_step = False
        if mail_channel.chatbot_current_step_id:
            chatbot = mail_channel.chatbot_current_step_id.chatbot_script_id
            user_messages = mail_channel.message_ids.filtered(
                lambda message: message.author_id != chatbot.operator_partner_id
            )
            user_answer = request.env['mail.message'].sudo()
            if user_messages:
                user_answer = user_messages.sorted(lambda message: message.id)[-1]
            next_step = mail_channel.chatbot_current_step_id._process_answer(mail_channel, user_answer.body)
        elif chatbot_script_id:  # when restarting, we don't have a "current step" -> set "next" as first step of the script
            chatbot = request.env['chatbot.script'].sudo().with_context(lang=chatbot_language).browse(chatbot_script_id)
            if chatbot.exists():
                next_step = chatbot.script_step_ids[:1]

        if not next_step:
            return None

        posted_message = next_step._process_step(mail_channel)
        return {
            'chatbot_posted_message': posted_message.message_format()[0] if posted_message else None,
            'chatbot_step': {
                'chatbot_operator_found': next_step.step_type == 'forward_operator' and len(
                    mail_channel.channel_member_ids) > 2,
                'chatbot_script_step_id': next_step.id,
                'chatbot_step_answers': [{
                    'id': answer.id,
                    'label': answer.name,
                    'redirect_link': answer.redirect_link,
                } for answer in next_step.answer_ids],
                'chatbot_step_is_last': next_step._is_last_step(mail_channel),
                'chatbot_step_message': plaintext2html(next_step.message) if not is_html_empty(next_step.message) else False,
                'chatbot_step_type': next_step.step_type,
            }
        }

    @http.route('/chatbot/step/validate_email', type="json", auth="public", cors="*")
    def chatbot_validate_email(self, channel_uuid):
        mail_channel = request.env['mail.channel'].sudo().search([('uuid', '=', channel_uuid)], limit=1)
        if not mail_channel or not mail_channel.chatbot_current_step_id:
            return None

        chatbot = mail_channel.chatbot_current_step_id.chatbot_script_id
        user_messages = mail_channel.message_ids.filtered(
            lambda message: message.author_id != chatbot.operator_partner_id
        )

        if user_messages:
            user_answer = user_messages.sorted(lambda message: message.id)[-1]
            result = chatbot._validate_email(user_answer.body, mail_channel)

            if result['posted_message']:
                result['posted_message'] = result['posted_message'].message_format()[0]

        return result



    @http.route("/chatbot/step/ai_chat", type="json", auth="public", cors="*")
    def chatbot_ai_chat_process(self, channel_uuid, user_message=None):
        """
        Process AI chat step by sending user input to n8n webhook
        and returning the AI response.
        """
        mail_channel = request.env['mail.channel'].sudo().search([
            ('uuid', '=', channel_uuid)
        ], limit=1)
        
        if not mail_channel or not mail_channel.chatbot_current_step_id:
            return {'success': False, 'error': 'Invalid channel or step'}
        
        chatbot = mail_channel.chatbot_current_step_id.chatbot_script_id
        
        # ✅ Lấy tin nhắn mới nhất của user
        user_messages = mail_channel.message_ids.filtered(
            lambda message: message.author_id != chatbot.operator_partner_id
        )
        
        if not user_messages:
            return {'success': False, 'error': 'No user message found'}
        
        # Lấy message mới nhất
        latest_user_message = user_messages.sorted(lambda msg: msg.id)[-1]
        user_text = latest_user_message.body
        
        # Remove HTML tags if present
        from odoo.tools import html2plaintext
        user_text = html2plaintext(user_text) if user_text else ""
        
        if not user_text.strip():
            return {'success': False, 'error': 'Empty user message'}
        
        try:
            # ✅ Gửi đến n8n webhook
            webhook_url = "https://n8n.bitech.vn/webhook/234fba59-05b4-47cb-9881-cbf39bbb6d05"
            
            payload = {
                "chatInput": user_text,
                "sessionId": channel_uuid,
                "userId": mail_channel.anonymous_name or "Anonymous"
            }
            
            _logger.info(f"Sending to n8n: {payload}")
            
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=20,
                headers={'Content-Type': 'application/json'}
            )
            
            response.raise_for_status()
            ai_response_data = response.json()
            
            # ✅ Xử lý response từ n8n
            ai_response_text = ""
            if isinstance(ai_response_data, dict):
                # Thử các key có thể có từ n8n
                ai_response_text = (
                    ai_response_data.get('response') or 
                    ai_response_data.get('answer') or 
                    ai_response_data.get('output') or 
                    ai_response_data.get('text') or
                    str(ai_response_data)
                )
            else:
                ai_response_text = str(ai_response_data)
            
            if not ai_response_text.strip():
                ai_response_text = "I'm sorry, I couldn't generate a response. Please try again."
            
            # ✅ Post bot reply
            from odoo.tools import plaintext2html
            posted_message = mail_channel._chatbot_post_message(
                chatbot,
                plaintext2html(ai_response_text)
            )
            
            _logger.info(f"AI Response posted: {ai_response_text}")
            
            return {
                'success': True,
                'ai_response': ai_response_text,
                'posted_message': posted_message.message_format()[0] if posted_message else None
            }
            
        except requests.RequestException as e:
            _logger.error(f"N8N API Error: {str(e)}")
            error_message = "I'm having trouble connecting to my AI brain. Please try again later."
            
            # Post error message
            posted_message = mail_channel._chatbot_post_message(
                chatbot,
                plaintext2html(error_message)
            )
            
            return {
                'success': False,
                'error': str(e),
                'posted_message': posted_message.message_format()[0] if posted_message else None
            }
        
        except Exception as e:
            _logger.error(f"Unexpected error in AI chat: {str(e)}")
            return {'success': False, 'error': 'Unexpected error occurred'}
    
    def _get_chatbot_language(self):
        return request.httprequest.cookies.get('frontend_lang', request.env.user.lang or get_lang(request.env).code)
