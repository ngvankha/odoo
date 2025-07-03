# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class ConsAssistantAIConfig(models.Model):
    _name = 'cons.assitant.ai.config'
    _description = 'Cons Assistant AI Configuration'
    _rec_name = 'name'

    name = fields.Char('Configuration Name', required=True, default="Default Config")
    n8n_webhook_url = fields.Char('N8N Webhook URL', required=True, 
                                  help="URL webhook của n8n để gửi tin nhắn")
    is_active = fields.Boolean('Active', default=True)
    timeout = fields.Integer('Timeout (seconds)', default=10, 
                            help="Thời gian chờ phản hồi từ n8n")
    
    @api.model
    def get_active_config(self):
        """Lấy cấu hình từ system parameters"""
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        
        return {
            'webhook_url': IrConfigParameter.get_param('cons_assitant_ai.webhook_url', ''),
            'enabled': IrConfigParameter.get_param('cons_assitant_ai.enabled', 'True').lower() == 'true',
            'timeout': int(IrConfigParameter.get_param('cons_assitant_ai.timeout', '10')),
            'welcome_message': IrConfigParameter.get_param('cons_assitant_ai.welcome_message', 
                'Xin chào! Tôi là chatbot AI của bạn. Tôi có thể giúp gì cho bạn?')
        }
    
    @api.model
    def send_message_to_n8n(self, message, user_context=None):
        """Gửi tin nhắn đến n8n và nhận phản hồi"""
        config = self.get_active_config()
        if not config['enabled']:
            return {
                'success': False,
                'message': 'Simple Chatbot đã bị tắt trong cấu hình'
            }
            
        if not config['webhook_url']:
            return {
                'success': False,
                'message': 'Chưa cấu hình webhook URL cho n8n trong Settings → General Settings'
            }
        
        try:
            # Tạo session ID duy nhất cho user
            session_id = f"session_{self.env.user.id}_{fields.Datetime.now().strftime('%Y%m%d')}"
            
            # Chuẩn bị dữ liệu gửi đến n8n
            payload = {
                'chatInput': message,
                'sessionId': session_id,
                'user_id': self.env.user.id,
                'user_name': self.env.user.name,
                'timestamp': fields.Datetime.now().isoformat(),
                'context': user_context or {}
            }
              # Gửi request đến n8n
            response = requests.post(
                config['webhook_url'],
                json=payload,
                timeout=config['timeout'],
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    
                    # Xử lý response từ n8n với nhiều format khác nhau
                    ai_response_text = self._extract_response_text(response_data)
                    
                    return {
                        'success': True,
                        'message': ai_response_text,
                        'data': response_data,
                        'raw_response': response_data
                    }
                except json.JSONDecodeError:
                    # Nếu không parse được JSON, trả về text response
                    response_text = response.text or 'Đã nhận phản hồi từ n8n'
                    return {
                        'success': True,
                        'message': response_text,
                        'data': {'text': response_text}
                    }
            else:
                return {
                    'success': False,
                    'message': f'Lỗi từ n8n (HTTP {response.status_code}): {response.text}'
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'message': f'Timeout sau {config["timeout"]} giây'
            }
        except requests.exceptions.RequestException as e:
            _logger.error("Error sending message to n8n: %s", str(e))
            return {
                'success': False,
                'message': f'Lỗi kết nối: {str(e)}'
            }
        except Exception as e:
            _logger.error("Unexpected error in send_message_to_n8n: %s", str(e))
            return {
                'success': False,
                'message': f'Lỗi không xác định: {str(e)}'
            }
    
    def _extract_response_text(self, response_data):
        """
        Trích xuất text response từ n8n với nhiều format khác nhau
        """
        if isinstance(response_data, str):
            return response_data
        
        if isinstance(response_data, dict):
            # Thử các key phổ biến cho response
            for key in ['response', 'answer', 'output', 'text', 'message', 'result', 'content']:
                if key in response_data and response_data[key]:
                    value = response_data[key]
                    if isinstance(value, str):
                        return value
                    elif isinstance(value, dict) and 'text' in value:
                        return value['text']
        
        # Nếu không tìm thấy format chuẩn, convert về string
        return str(response_data) if response_data else 'Đã nhận phản hồi từ n8n'
    
    def _format_response_for_display(self, text):
        """
        Format response text for better display (convert Markdown to HTML)
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
