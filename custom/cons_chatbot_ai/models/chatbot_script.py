from odoo import fields, models, api

class ChatbotScript(models.Model):
    _inherit = 'chatbot.script'
    
    # AI Configuration fields
    webhook_url = fields.Char(
        string='AI Webhook URL',
        help='URL endpoint for AI service integration (e.g., n8n webhook)',
        default='https://n8n.bitech.vn/webhook/234fba59-05b4-47cb-9881-cbf39bbb6d05'
    )
    ai_timeout = fields.Integer(
        string='AI Timeout (seconds)',
        help='Timeout for AI service requests in seconds',
        default=120
    )
    ai_enabled = fields.Boolean(
        string='Enable AI Integration',
        help='Enable AI chat functionality for this chatbot',
        default=True
    )
    ai_error_message = fields.Text(
        string='AI Error Message',
        help='Message to display when AI service is unavailable',
        default='I\'m having trouble connecting to my AI brain. Please try again later.',
        translate=True
    )
    ai_session_field = fields.Selection([
        ('channel_uuid', 'Channel UUID'),
        ('session_id', 'Custom Session ID'),
    ], string='Session ID Field', default='channel_uuid',
       help='Field to use as session identifier for AI service')
    
    @api.model
    def get_ai_config(self, script_id):
        """Get AI configuration for a specific script"""
        script = self.browse(script_id)
        if not script.exists():
            return {}
            
        return {
            'webhook_url': script.webhook_url,
            'timeout': script.ai_timeout,
            'enabled': script.ai_enabled,
            'error_message': script.ai_error_message,
            'session_field': script.ai_session_field,
        }