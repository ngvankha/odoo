# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.mail.models.discuss.mail_guest import add_guest_to_context
from odoo.addons.mail.tools.discuss import Store
from odoo.tools import email_normalize, html2plaintext, plaintext2html
import requests


class LivechatChatbotScriptController(http.Controller):
    @http.route("/chatbot/restart", type="json", auth="public")
    @add_guest_to_context
    def chatbot_restart(self, channel_id, chatbot_script_id):
        discuss_channel = request.env["discuss.channel"].search([("id", "=", channel_id)])
        chatbot = request.env['chatbot.script'].browse(chatbot_script_id)
        if not discuss_channel or not chatbot.exists():
            return None
        chatbot_language = self._get_chatbot_language()
        message = discuss_channel.with_context(lang=chatbot_language)._chatbot_restart(chatbot)
        return Store(message, for_current_user=True).get_result()

    @http.route("/chatbot/answer/save", type="json", auth="public")
    @add_guest_to_context
    def chatbot_save_answer(self, channel_id, message_id, selected_answer_id):
        discuss_channel = request.env["discuss.channel"].search([("id", "=", channel_id)])
        chatbot_message = request.env['chatbot.message'].sudo().search([
            ('mail_message_id', '=', message_id),
            ('discuss_channel_id', '=', discuss_channel.id),
        ], limit=1)
        selected_answer = request.env['chatbot.script.answer'].sudo().browse(selected_answer_id)

        if not discuss_channel or not chatbot_message or not selected_answer.exists():
            return

        if selected_answer in chatbot_message.script_step_id.answer_ids:
            chatbot_message.write({'user_script_answer_id': selected_answer_id})

    @http.route("/chatbot/step/trigger", type="json", auth="public")
    @add_guest_to_context
    def chatbot_trigger_step(self, channel_id, chatbot_script_id=None):
        chatbot_language = self._get_chatbot_language()
        discuss_channel = request.env["discuss.channel"].with_context(lang=chatbot_language).search([("id", "=", channel_id)])
        if not discuss_channel:
            return None

        next_step = False
        # sudo: chatbot.script.step - visitor can access current step of the script
        if current_step := discuss_channel.sudo().chatbot_current_step_id:
            chatbot = current_step.chatbot_script_id
            user_messages = discuss_channel.message_ids.filtered(
                lambda message: message.author_id != chatbot.operator_partner_id
            )
            user_answer = request.env['mail.message'].sudo()
            if user_messages:
                user_answer = user_messages.sorted(lambda message: message.id)[-1]
            next_step = current_step._process_answer(discuss_channel, user_answer.body)
        elif chatbot_script_id:  # when restarting, we don't have a "current step" -> set "next" as first step of the script
            chatbot = request.env['chatbot.script'].sudo().browse(chatbot_script_id).with_context(lang=chatbot_language)
            if chatbot.exists():
                next_step = chatbot.script_step_ids[:1]

        if not next_step:
            # sudo: visitor cannot write on channel otherwise. Just writing a
            # boolean is safe
            discuss_channel.sudo().livechat_active = False
            return None

        posted_message = next_step._process_step(discuss_channel)
        store = Store(posted_message, for_current_user=True)
        store.add(next_step)
        store.add(
            "ChatbotStep",
            {
                "id": (next_step.id, posted_message.id),
                "isLast": next_step._is_last_step(discuss_channel),
                "message": Store.one(posted_message, only_id=True),
                "operatorFound": next_step.step_type == "forward_operator"
                and len(discuss_channel.channel_member_ids) > 2,
                "scriptStep": Store.one(next_step, only_id=True),
            },
        )
        store.add(
            "Chatbot",
            {
                "currentStep": {
                    "id": (next_step.id, discuss_channel.id),
                    "scriptStep": next_step.id,
                    "message": posted_message.id,
                },
                "id": (chatbot.id, discuss_channel.id),
                "script": Store.one(chatbot, only_id=True),
                "thread": Store.one(discuss_channel, only_id=True),
            },
        )
        return store.get_result()

    @http.route("/chatbot/step/validate_email", type="json", auth="public")
    @add_guest_to_context
    def chatbot_validate_email(self, channel_id):
        discuss_channel = request.env["discuss.channel"].search(
            [("id", "=", channel_id)]
        ).with_context(lang=self._get_chatbot_language())
        if not discuss_channel:
            return {"error": "Channel not found"}

        # Lấy tin nhắn mới nhất của user
        last_user_message = (
            discuss_channel.message_ids.filtered(
                lambda m: m.author_id != discuss_channel.chatbot_current_step_id.chatbot_script_id.operator_partner_id
            )
            .sorted(lambda m: m.id)[-1]
            if discuss_channel.message_ids
            else None
        )

        if not last_user_message:
            return {"error": "No user message found"}

        user_text = html2plaintext(last_user_message.body)

        # Gửi đến webhook n8n
        try:
            response = requests.post(
                "https://n8n.bitech.vn/webhook/234fba59-05b4-47cb-9881-cbf39bbb6d05",
                json={"chatInput": user_text, "sessionId": channel_id},
                timeout=120,
            )

            # Debug: log response details
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {response.headers}")
            print(f"Response text: '{response.text}'")
            print(f"Response text length: {len(response.text)}")

            if response.status_code == 200:
                if not response.text.strip():
                    bot_reply = "Webhook trả về phản hồi trống"
                else:
                    content_type = response.headers.get("Content-Type", "")
                    if "application/json" in content_type:
                        try:
                            reply_data = response.json()
                            print(f"Parsed JSON: {reply_data}")
                            
                            if isinstance(reply_data, list) and reply_data:
                                bot_reply = reply_data[0].get("output", "Tôi chưa có phản hồi 1")
                            elif isinstance(reply_data, dict):
                                bot_reply = reply_data.get("output", "Tôi chưa có phản hồi 2")
                            else:
                                bot_reply = f"Định dạng JSON không mong đợi: {reply_data}"
                        except (ValueError, TypeError) as e:
                            bot_reply = f"Lỗi phân tích JSON: {str(e)}. Nội dung phản hồi: '{response.text}'"
                    else:
                        bot_reply = f"Webhook không trả về JSON. Content-Type: {content_type}. Nội dung: '{response.text}'"
            else:
                bot_reply = f"Lỗi HTTP {response.status_code}: {response.text}"

        except requests.exceptions.RequestException as e:
            bot_reply = f"Lỗi kết nối HTTP: {str(e)}"
        except Exception as e:
            bot_reply = f"Đã có lỗi kết nối với hệ thống xử lý: {str(e)}"


        # Gửi tin nhắn bot trả lời vào channel
        discuss_channel._chatbot_post_message(
            discuss_channel.chatbot_current_step_id.chatbot_script_id,
            plaintext2html(bot_reply)
        )

        return {"success": True, "bot_reply": bot_reply}

    @http.route("/chatbot/step/ai_chat", type="json", auth="public")
    @add_guest_to_context
    def chatbot_ai_chat_process(self, channel_id):
        """Xử lý AI Chat step"""
        discuss_channel = request.env["discuss.channel"].search(
            [("id", "=", channel_id)]
        ).with_context(lang=self._get_chatbot_language())
        
        if not discuss_channel:
            return {"error": "Channel not found"}

        # Lấy tin nhắn mới nhất của user
        current_step = discuss_channel.sudo().chatbot_current_step_id
        if not current_step or current_step.step_type != 'ai_chat':
            return {"error": "Invalid step type"}
            
        last_user_message = (
            discuss_channel.message_ids.filtered(
                lambda m: m.author_id != current_step.chatbot_script_id.operator_partner_id
            )
            .sorted(lambda m: m.id)[-1]
            if discuss_channel.message_ids
            else None
        )

        if not last_user_message:
            return {"error": "No user message found"}

        user_text = html2plaintext(last_user_message.body)

        # Gửi đến webhook n8n
        try:
            response = requests.post(
                "https://n8n.bitech.vn/webhook/234fba59-05b4-47cb-9881-cbf39bbb6d05",
                json={"chatInput": user_text, "sessionId": channel_id},
                timeout=20,
            )

            if response.status_code == 200:
                if not response.text.strip():
                    bot_reply = "Tôi chưa có phản hồi cho câu hỏi này."
                else:
                    content_type = response.headers.get("Content-Type", "")
                    if "application/json" in content_type:
                        try:
                            reply_data = response.json()
                            if isinstance(reply_data, list) and reply_data:
                                bot_reply = reply_data[0].get("output", "Tôi chưa có phản hồi.")
                            elif isinstance(reply_data, dict):
                                bot_reply = reply_data.get("output", "Tôi chưa có phản hồi.")
                            else:
                                bot_reply = f"Định dạng phản hồi không hợp lệ: {reply_data}"
                        except (ValueError, TypeError) as e:
                            bot_reply = f"Lỗi xử lý phản hồi: {str(e)}"
                    else:
                        bot_reply = response.text
            else:
                bot_reply = f"Lỗi kết nối: {response.status_code}"

        except requests.exceptions.RequestException as e:
            bot_reply = f"Không thể kết nối đến hệ thống AI: {str(e)}"
        except Exception as e:
            bot_reply = f"Đã có lỗi xảy ra: {str(e)}"

        # Gửi tin nhắn bot trả lời vào channel
        posted_message = discuss_channel._chatbot_post_message(
            current_step.chatbot_script_id,
            plaintext2html(bot_reply)
        )

        # Trả về đúng format Store để frontend nhận dạng
        store = Store(posted_message, for_current_user=True)

        return {
            "success": True, 
            "bot_reply": bot_reply,
            **store.get_result()
        }

    def _get_chatbot_language(self):
        return request.env["chatbot.script"]._get_chatbot_language()
