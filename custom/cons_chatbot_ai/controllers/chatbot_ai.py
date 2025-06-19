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
        _logger.info(f"🔍 AI Chat API called - channel_uuid: {channel_uuid}")
        
        mail_channel = request.env['mail.channel'].sudo().search([
            ('uuid', '=', channel_uuid)
        ], limit=1)
        
        if not mail_channel:
            _logger.error(f" Channel not found: {channel_uuid}")
            return {'success': False, 'error': 'Channel not found'}
            
        if not mail_channel.chatbot_current_step_id:
            _logger.error(f" No current step for channel: {channel_uuid}")
            return {'success': False, 'error': 'No current step'}
        
        _logger.info(f"🔍 Current step: {mail_channel.chatbot_current_step_id.step_type}")
        
        chatbot = mail_channel.chatbot_current_step_id.chatbot_script_id
        
        # Lấy tin nhắn mới nhất của user
        user_messages = mail_channel.message_ids.filtered(
            lambda message: message.author_id != chatbot.operator_partner_id
        )
        
        if not user_messages:
            _logger.warning(" No user message found")
            return {'success': False, 'error': 'No user message found'}
        
        # Lấy message mới nhất
        latest_user_message = user_messages.sorted(lambda msg: msg.id)[-1]
        user_text = latest_user_message.body
        
        # Remove HTML tags if present
        from odoo.tools import html2plaintext
        user_text = html2plaintext(user_text) if user_text else ""
        
        _logger.info(f" User message: {user_text}")
        
        if not user_text.strip():
            return {'success': False, 'error': 'Empty user message'}
        
        try:
            # Gửi đến n8n webhook
            webhook_url = chatbot.get_webhook_url()
            
            payload = {
                "chatInput": user_text,
                "sessionId": channel_uuid,
                "userId": mail_channel.anonymous_name or "Anonymous"
            }
            
            _logger.info(f" Sending to n8n: {payload}")
            
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=120,
                headers={'Content-Type': 'application/json'}
            )
            
            response.raise_for_status()
            ai_response_data = response.json()
            
            _logger.info(f"🔍 N8N response: {ai_response_data}")
            
            # Xử lý response từ n8n
            ai_response_text = ""
            if isinstance(ai_response_data, dict):
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
            
            # Format the AI response
            formatted_response = self._format_ai_response(ai_response_text)
            
            # Post bot reply
            from odoo.tools import plaintext2html
            posted_message = mail_channel._chatbot_post_message(
                chatbot,
                formatted_response
            )
            
            _logger.info(f" AI Response posted: {formatted_response}")
            
            return {
                'success': True,
                'ai_response': formatted_response,
                'posted_message': posted_message.message_format()[0] if posted_message else None
            }
            
        except requests.RequestException as e:
            _logger.error(f" N8N API Error: {str(e)}")
            error_message = "I'm having trouble connecting to n8n. Please try again later."
            
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
            _logger.error(f" Unexpected error in AI chat: {str(e)}")
            return {'success': False, 'error': 'Unexpected error occurred'}
    
    def _format_ai_response(self, text):
        """
        Convert Markdown to HTML for proper chatbot display with bold formatting
        """
        import re
        
        if not text:
            return ""

        # Escape HTML special characters first
        text = (
            text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
        )

        # Headers: # Title => <strong>Title</strong>
        text = re.sub(r'^#{1,6}\s+(.+)$', r'<strong>\1</strong>', text, flags=re.MULTILINE)

        # Pattern 2: #03, #123 (không có space) => <strong>#03</strong>
        text = re.sub(r'#(\d+)', r'<strong>\1</strong>', text)
        
        # Bold: **text** => <strong>text</strong>
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)

        # Italic: *text* => <em>text</em> (avoid **bold** conflict)
        text = re.sub(r'(?<!\*)\*(?!\*)(.*?)\*(?!\*)', r'<em>\1</em>', text)

        # Convert newlines to <br> for HTML display
        text = text.replace('\n', '<br>')

        # Clean up multiple <br> tags
        text = re.sub(r'(<br>){3,}', '<br><br>', text)

        return text.strip()