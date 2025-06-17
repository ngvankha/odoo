from odoo import http
from odoo.http import request
import requests
import logging

_logger = logging.getLogger(__name__)

class ChatbotAIController(http.Controller):
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
        
        # Lấy tin nhắn mới nhất của user
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
            webhook_url = "https://n8n.bitech.vn/webhook/234fba59-05b4-47cb-9881-cbf39bbb6d05"
            
            payload = {
                "chatInput": user_text,
                "sessionId": channel_uuid,
            }
            
            _logger.info(f"Sending to n8n: {payload}")
            
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=120,
                headers={'Content-Type': 'application/json'}
            )
            
            response.raise_for_status()
            ai_response_data = response.json()
            
            # Xử lý response từ n8n
            ai_response_text = ""
            if isinstance(ai_response_data, dict):
                ai_response_text = (
                    ai_response_data.get('output') or 
                    str(ai_response_data)
                )
            else:
                ai_response_text = str(ai_response_data)
            
            if not ai_response_text.strip():
                ai_response_text = "I'm sorry, I couldn't generate a response. Please try again."
            
            # Post bot reply
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
            
        except Exception as e:
            _logger.error(f"Unexpected error in AI chat: {str(e)}")
            return {'success': False, 'error': 'Unexpected error occurred'}