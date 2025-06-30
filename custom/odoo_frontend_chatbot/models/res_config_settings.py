# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    frontend_chatbot_enabled = fields.Boolean(
        string="Enable Frontend Chatbot",
        config_parameter='odoo_frontend_chatbot.enabled',
        help="Enable floating chatbot in Odoo frontend interface"
    )
    
    frontend_chatbot_welcome_message = fields.Text(
        string="Welcome Message",
        config_parameter='odoo_frontend_chatbot.welcome_message',
        help="Message shown when user opens the chatbot"
    )
    
    frontend_chatbot_position = fields.Selection([
        ('bottom-right', 'Bottom Right'),
        ('bottom-left', 'Bottom Left'),
        ('top-right', 'Top Right'),
        ('top-left', 'Top Left'),
    ], string="Position", default='bottom-right',
        config_parameter='odoo_frontend_chatbot.position',
        help="Where to display the chatbot button"
    )
