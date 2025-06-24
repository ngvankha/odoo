# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
import requests
import logging
import json

_logger = logging.getLogger(__name__)

class AiBotController(http.Controller):
    
    @http.route('/ai_bot/query', type='json', auth='user')
    def query(self, thread_id, thread_model, thread_type, author_id, query):
        """
        Hoàn toàn dựa vào n8n webhook để xử lý AI
        """
        _logger.info(f"=== AI Bot Controller START ===")
        _logger.info(f"Params: thread_id={thread_id}, model={thread_model}, type={thread_type}, author={author_id}")
        _logger.info(f"Query: '{query}'")
        
        try:
            # Kiểm tra xem có nên phản hồi không
            ai_bot_model = request.env['mail.bot.ai']
            should_respond = ai_bot_model.query(thread_id, thread_model, thread_type, author_id, query)
            
            if not should_respond:
                _logger.info("AI Bot should not respond to this message")
                return {'success': False, 'message': 'No response needed'}
            
            # Lấy webhook URL từ system parameters
            webhook_url = request.env['ir.config_parameter'].sudo().get_param('ai_bot.n8n_webhook_url')
            
            if not webhook_url:
                _logger.error("N8N webhook URL not configured")
                return {'error': 'AI service not configured. Please contact administrator.'}

            # Chuẩn bị context cho n8n
            thread = request.env[thread_model].browse(thread_id)
            user = request.env['res.users'].browse(request.uid)
            
            payload = {
                'chatInput': query,
                'sessionId': f"{thread_model}-{thread_id}",
                'userId': author_id,
                'userName': user.name,
                'threadType': thread_type,
                'threadName': thread.display_name if thread else 'Unknown',
                'timestamp': str(request.env.cr.now()),
                'context': {
                    'company_id': request.env.company.id,
                    'company_name': request.env.company.name,
                    'lang': request.env.user.lang or 'en_US'
                }
            }
            
            _logger.info(f"Sending to N8N: {webhook_url}")
            
            # Gọi n8n webhook
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=30,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Odoo-AI-Bot/1.0'
                }
            )
            
            if response.status_code == 200:
                try:
                    ai_response = response.json()
                    ai_output = ai_response.get('output') or ai_response.get('text') or str(ai_response)
                    
                    if ai_output:
                        # Post AI response vào thread
                        ai_bot_partner = request.env.ref("ai_bot.partner_ai_bot")
                        ai_bot_user = request.env.ref("ai_bot.user_ai_bot")
                        
                        thread.with_user(ai_bot_user).message_post(
                            body=ai_output,
                            author_id=ai_bot_partner.id,
                            message_type='comment',
                            subtype_id=request.env['ir.model.data']._xmlid_to_res_id('mail.mt_comment')
                        )
                        
                        _logger.info("AI Bot response posted successfully")
                        return {'success': True, 'response': ai_output}
                    else:
                        return {'error': 'Empty response from AI service'}
                        
                except json.JSONDecodeError:
                    _logger.error(f"Invalid JSON response from N8N: {response.text}")
                    return {'error': 'Invalid response format from AI service'}
                    
            else:
                _logger.error(f"N8N webhook error: {response.status_code} - {response.text}")
                return {'error': f'AI service error: {response.status_code}'}
                
        except Exception as e:
            _logger.error(f"Unexpected error in AI Bot Controller: {str(e)}")
            return {'error': 'Unexpected error occurred. Please try again.'}

    @http.route('/ai_bot/test', type='http', auth='user', methods=['GET'])
    def test_webhook(self):
        """Test endpoint để kiểm tra kết nối n8n"""
        webhook_url = request.env['ir.config_parameter'].sudo().get_param('ai_bot.n8n_webhook_url')
        
        if not webhook_url:
            return "❌ N8N webhook URL not configured"
            
        try:
            test_payload = {
                'chatInput': 'Test connection from Odoo',
                'sessionId': 'test-session',
                'userId': request.uid,
                'threadType': 'test'
            }
            
            response = requests.post(webhook_url, json=test_payload, timeout=10)
            
            if response.status_code == 200:
                return f"✅ N8N connection successful!<br>Response: {response.text}"
            else:
                return f"❌ N8N error: {response.status_code}<br>{response.text}"
                
        except Exception as e:
            return f"❌ Connection failed: {str(e)}"