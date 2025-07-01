# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Simple Chatbot Settings
    simple_chatbot_webhook_url = fields.Char(
        string='Simple Chatbot n8n Webhook URL',
        config_parameter='simple_chatbot.webhook_url',
        help="URL webhook của n8n để gửi tin nhắn từ Simple Chatbot"
    )
    
    simple_chatbot_enabled = fields.Boolean(
        string='Enable Simple Chatbot',
        config_parameter='simple_chatbot.enabled',
        default=True,
        help="Bật/tắt Simple Chatbot trong systray"
    )
    
    simple_chatbot_timeout = fields.Integer(
        string='Simple Chatbot Timeout (seconds)',
        config_parameter='simple_chatbot.timeout',
        default=10,
        help="Thời gian chờ phản hồi từ n8n (giây)"
    )
    
    simple_chatbot_welcome_message = fields.Text(
        string='Welcome Message',
        config_parameter='simple_chatbot.welcome_message',
        default="Xin chào! Tôi là chatbot AI của bạn. Tôi có thể giúp gì cho bạn?",
        help="Tin nhắn chào mừng khi mở chatbot"
    )
