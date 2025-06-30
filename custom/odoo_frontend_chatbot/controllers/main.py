# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class FrontendChatbotController(http.Controller):

    @http.route('/frontend_chatbot/config', type='json', auth='user')
    def get_config(self):
        """Get chatbot configuration for frontend"""
        try:
            config = {
                'enabled': request.env['ir.config_parameter'].sudo().get_param('odoo_frontend_chatbot.enabled', 'False') == 'True',
                'welcome_message': request.env['ir.config_parameter'].sudo().get_param('odoo_frontend_chatbot.welcome_message', 'Hello! I\'m your Odoo assistant. How can I help you today? 👋'),
                'position': request.env['ir.config_parameter'].sudo().get_param('odoo_frontend_chatbot.position', 'bottom-right'),
                'user_id': request.env.user.id,
                'user_name': request.env.user.name,
                'odoobot_id': request.env.ref('base.partner_root').id,
            }
            return config
        except Exception as e:
            _logger.error(f"Error getting chatbot config: {str(e)}")
            return {'enabled': False, 'error': str(e)}

    @http.route('/frontend_chatbot/create_channel', type='json', auth='user')
    def create_or_get_channel(self):
        """Create or get existing chatbot channel for current user"""
        try:
            user = request.env.user
            odoobot_partner = request.env.ref('base.partner_root')
            
            # Tìm channel hiện tại giữa user và odoobot
            existing_channel = request.env['mail.channel'].search([
                ('channel_member_ids.partner_id', 'in', [user.partner_id.id, odoobot_partner.id]),
                ('channel_type', '=', 'chat'),
                ('name', 'ilike', 'OdooBot')
            ], limit=1)
            
            if existing_channel:
                channel = existing_channel
            else:
                # Tạo channel mới
                channel = request.env['mail.channel'].create({
                    'name': f'OdooBot & {user.name}',
                    'channel_type': 'chat',
                    'channel_member_ids': [
                        (0, 0, {'partner_id': user.partner_id.id}),
                        (0, 0, {'partner_id': odoobot_partner.id}),
                    ]
                })
                
                # Gửi welcome message
                welcome_message = request.env['ir.config_parameter'].sudo().get_param(
                    'odoo_frontend_chatbot.welcome_message', 
                    'Hello! I\'m your Odoo assistant. How can I help you today? 👋'
                )
                
                channel.message_post(
                    body=welcome_message,
                    author_id=odoobot_partner.id,
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment'
                )
            
            return {
                'channel_id': channel.id,
                'channel_uuid': channel.uuid,
                'channel_name': channel.name,
            }
            
        except Exception as e:
            _logger.error(f"Error creating/getting chatbot channel: {str(e)}")
            return {'error': str(e)}

    @http.route('/frontend_chatbot/send_message', type='json', auth='user')
    def send_message(self, channel_id, message):
        """Send message to chatbot channel"""
        try:
            channel = request.env['mail.channel'].browse(channel_id)
            if not channel.exists():
                return {'error': 'Channel not found'}
            
            # Gửi message của user
            user_message = channel.message_post(
                body=message,
                author_id=request.env.user.partner_id.id,
                message_type='comment',
                subtype_xmlid='mail.mt_comment'
            )
            
            # Trigger OdooBot response
            odoobot_partner = request.env.ref('base.partner_root')
            
            # Kiểm tra xem có ai_bot module không
            ai_bot_available = 'ai_bot' in request.env.registry._init_modules
            
            if ai_bot_available:
                # Sử dụng AI bot nếu có
                try:
                    ai_bot_model = request.env['mail.bot.ai']
                    ai_bot_model.query(channel.id, 'mail.channel', 'chat', request.env.user.partner_id.id, message)
                except Exception as ai_error:
                    _logger.warning(f"AI bot error, falling back to OdooBot: {str(ai_error)}")
                    # Fallback to OdooBot
                    mail_bot = request.env['mail.bot']
                    mail_bot._apply_logic(channel, {
                        'body': message,
                        'author_id': request.env.user.partner_id.id,
                        'message_type': 'comment'
                    })
            else:
                # Sử dụng OdooBot thông thường
                mail_bot = request.env['mail.bot']
                mail_bot._apply_logic(channel, {
                    'body': message,
                    'author_id': request.env.user.partner_id.id,
                    'message_type': 'comment'
                })
            
            return {'success': True, 'message_id': user_message.id}
            
        except Exception as e:
            _logger.error(f"Error sending message to chatbot: {str(e)}")
            return {'error': str(e)}

    @http.route('/frontend_chatbot/get_messages', type='json', auth='user')
    def get_messages(self, channel_id, last_message_id=None):
        """Get messages from chatbot channel"""
        try:
            channel = request.env['mail.channel'].browse(channel_id)
            if not channel.exists():
                return {'error': 'Channel not found'}
            
            domain = [('model', '=', 'mail.channel'), ('res_id', '=', channel_id)]
            
            if last_message_id:
                domain.append(('id', '>', last_message_id))
            
            messages = request.env['mail.message'].search(domain, order='create_date asc')
            
            message_list = []
            for msg in messages:
                message_list.append({
                    'id': msg.id,
                    'body': msg.body,
                    'author_id': msg.author_id.id,
                    'author_name': msg.author_id.name,
                    'date': msg.create_date.isoformat(),
                    'is_bot': msg.author_id.id == request.env.ref('base.partner_root').id
                })
            
            return {'messages': message_list}
            
        except Exception as e:
            _logger.error(f"Error getting messages from chatbot: {str(e)}")
            return {'error': str(e)}
