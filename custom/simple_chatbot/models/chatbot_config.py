# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class ChatbotConfig(models.Model):
    _name = 'simple.chatbot.config'
    _description = 'Simple Chatbot Configuration'
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
            'webhook_url': IrConfigParameter.get_param('simple_chatbot.webhook_url', ''),
            'enabled': IrConfigParameter.get_param('simple_chatbot.enabled', 'True').lower() == 'true',
            'timeout': int(IrConfigParameter.get_param('simple_chatbot.timeout', '10')),
            'welcome_message': IrConfigParameter.get_param('simple_chatbot.welcome_message', 
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
            # Chuẩn bị dữ liệu gửi đến n8n
            payload = {
                'message': message,
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
                    return {
                        'success': True,
                        'message': response_data.get('message', 'Phản hồi từ n8n'),
                        'data': response_data
                    }
                except json.JSONDecodeError:
                    return {
                        'success': True,
                        'message': response.text or 'Đã nhận phản hồi từ n8n'
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
