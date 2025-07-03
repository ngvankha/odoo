# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class ConsAssistantAIController(http.Controller):
    
    @http.route('/cons_assitant_ai/send_message', type='json', auth='user', methods=['POST'])
    def send_message(self, message, **kwargs):
        """API endpoint để gửi tin nhắn đến n8n"""
        try:
            # Lấy model cấu hình
            ChatbotConfig = request.env['cons.assitant.ai.config']
            
            # Gửi tin nhắn đến n8n
            result = ChatbotConfig.send_message_to_n8n(
                message=message,
                user_context=kwargs
            )
            
            return {
                'success': result['success'],
                'response': result['message'],
                'data': result.get('data', {})
            }
            
        except Exception as e:
            _logger.error("Error in send_message controller: %s", str(e))
            return {
                'success': False,
                'response': f'Lỗi server: {str(e)}'
            }
    
    @http.route('/cons_assitant_ai/get_config', type='json', auth='user', methods=['POST'])
    def get_config(self):
        """Lấy thông tin cấu hình hiện tại"""
        try:
            ChatbotConfig = request.env['cons.assitant.ai.config']
            config = ChatbotConfig.get_active_config()
            
            return {
                'success': True,
                'config': {
                    'enabled': config['enabled'],
                    'has_webhook': bool(config['webhook_url']),
                    'webhook_configured': bool(config['webhook_url'].strip()),
                    'timeout': config['timeout'],
                    'welcome_message': config['welcome_message']
                }
            }
        except Exception as e:
            _logger.error("Error in get_config controller: %s", str(e))
            return {
                'success': False,
                'config': {
                    'enabled': True,
                    'has_webhook': False,
                    'webhook_configured': False,
                    'timeout': 10,
                    'welcome_message': 'Xin chào! Tôi là chatbot AI của bạn. Tôi có thể giúp gì cho bạn?'
                }
            }
