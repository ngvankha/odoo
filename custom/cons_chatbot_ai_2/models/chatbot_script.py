from odoo import models, fields, api

class ChatbotScript(models.Model):
    _inherit = 'chatbot.script'

    webhook_url = fields.Char(string='Webhook URL', help='URL for the AI service webhook.')

    @api.model
    def send_to_ai_service(self, user_input):
        """Send user input to the AI service and return the response."""
        if not self.webhook_url:
            return {'success': False, 'error': 'Webhook URL not configured.'}

        import requests
        try:
            response = requests.post(self.webhook_url, json={'input': user_input})
            response.raise_for_status()
            return {'success': True, 'data': response.json()}
        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}