from odoo import models, fields, api
import requests

class AIChatbot(models.Model):
    _name = 'ai.chatbot'
    _description = 'AI Chatbot'

    name = fields.Char(string="Question", required=True)
    response = fields.Text(string="Response", readonly=True)

    @api.model
    def get_ai_response(self, question):
        api_url = "https://api.lmstudio.ai/v1/chatbot"
        api_key = "your_api_key_here"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        }
        payload = {
            'input': question
        }
        response = requests.post(api_url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get('output', 'No response')
        else:
            return f"Error: {response.status_code}"