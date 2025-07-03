from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)

class ChatbotScript(models.Model):
    _inherit = 'chatbot.script'
    
    # AI Configuration fields
    webhook_url = fields.Char(
        string='n8n Webhook URL',
        help='URL endpoint for AI service integration n8n webhook',
    )
    ai_enabled = fields.Boolean(
        string='Enable n8n Agent',
        help='Enable AI chat functionality for this chatbot',
        default=lambda self: self._get_default_ai_enabled()
    )

    def _get_default_ai_enabled(self):
        """Get default AI enabled from system parameter"""
        return self.env['ir.config_parameter'].sudo().get_param(
            'cons_chatbot_ai.enabled_by_default', 'True'
        ) == 'True'

    def get_webhook_url(self):
        """Get webhook URL with proper fallback logic"""
        self.ensure_one()
        
        # 1.  Ưu tiên webhook_url riêng của chatbot (nếu có)
        if self.webhook_url and self.webhook_url.strip():
            _logger.info(f"🔍 Using chatbot-specific webhook URL: {self.webhook_url}")
            return self.webhook_url.strip()
            
        # 2.  Fallback to system parameter  
        system_url = self.env['ir.config_parameter'].sudo().get_param(
            'cons_chatbot_ai.webhook_url'
        )
        if system_url and system_url.strip():
            _logger.info(f"🔍 Using system default webhook URL: {system_url}")
            return system_url.strip()
            
        # Log warning nếu không có URL nào
        _logger.warning(f" No webhook URL configured for chatbot '{self.title}' (ID: {self.id})")
        return False
    
    def validate_webhook_url(self):
        """Validate if webhook URL is properly configured"""
        self.ensure_one()
        webhook_url = self.get_webhook_url()
        if not webhook_url:
            return False, "No webhook URL configured"
        
        # Basic URL validation
        if not webhook_url.startswith(('http://', 'https://')):
            return False, "Invalid URL format"
            
        return True, "URL is valid"
    
    @api.model
    def get_ai_config(self, script_id):
        """Get AI configuration for a specific script"""
        script = self.browse(script_id)
        if not script.exists():
            return {}
            
        return {
            'webhook_url': script.get_webhook_url(), 
            'enabled': script.ai_enabled,
            'valid_url': script.validate_webhook_url()[0],
        }
    
    @api.depends('script_step_ids.step_type')
    def _compute_first_step_warning(self):
        for script in self:
            allowed_first_step_types = [
                'question_selection',
                'question_email',
                'question_phone',
                'free_input_single',
                'free_input_multi',
                'ai_chat',  # AI Chat
            ]
            welcome_steps = script.script_step_ids and script._get_welcome_steps()
            if welcome_steps and welcome_steps[-1].step_type == 'forward_operator':
                script.first_step_warning = 'first_step_operator'
            elif welcome_steps and welcome_steps[-1].step_type not in allowed_first_step_types:
                script.first_step_warning = 'first_step_invalid'
            else:
                script.first_step_warning = False
    