# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Cons Assistant AI Settings
    cons_assitant_ai_webhook_url = fields.Char(
        string='Cons Assistant AI n8n Webhook URL',
        config_parameter='cons_assitant_ai.webhook_url',
        help="URL webhook của n8n để gửi tin nhắn từ Cons Assistant AI"
    )
    
    cons_assitant_ai_enabled = fields.Boolean(
        string='Enable Cons Assistant AI',
        config_parameter='cons_assitant_ai.enabled',
        default=True,
        help="Bật/tắt Cons Assistant AI trong systray"
    )
    
    cons_assitant_ai_timeout = fields.Integer(
        string='Cons Assistant AI Timeout (seconds)',
        config_parameter='cons_assitant_ai.timeout',
        default=10,
        help="Thời gian chờ phản hồi từ n8n (giây)"
    )
    
    cons_assitant_ai_welcome_message = fields.Char(
        string='Welcome Message',
        config_parameter='cons_assitant_ai.welcome_message',
        default="Xin chào! Tôi là AI Assistant của bạn. Tôi có thể giúp gì cho bạn?",
        help="Tin nhắn chào mừng khi mở AI Assistant"
    )
