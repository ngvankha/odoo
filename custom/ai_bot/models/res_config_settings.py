# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ai_bot_n8n_webhook_url = fields.Char(
        'N8N Webhook URL',
        config_parameter='ai_bot.n8n_webhook_url',
        help='URL của n8n webhook để xử lý AI chat'
    )
