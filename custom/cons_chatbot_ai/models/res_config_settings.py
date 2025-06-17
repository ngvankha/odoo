from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    chatbot_ai_webhook_url = fields.Char(
        string='Default AI Webhook URL',
        config_parameter='cons_chatbot_ai.webhook_url',
        help='Default webhook URL for AI service integration'
    )
    
    chatbot_ai_enabled_by_default = fields.Boolean(
        string='Enable AI by Default',
        config_parameter='cons_chatbot_ai.enabled_by_default',
        help='Enable AI integration by default for new chatbots'
    )