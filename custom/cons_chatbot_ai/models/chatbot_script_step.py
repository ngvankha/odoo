from odoo import models, fields, api
from odoo.tools import plaintext2html

class ChatbotScriptStep(models.Model):
    _inherit = 'chatbot.script.step'
    
    # Extend selection với ai_chat option
    step_type = fields.Selection(
        selection_add=[('ai_chat', 'AI Chat')]
    )
    
    def _process_step(self, mail_channel):
        """Override to handle AI chat steps"""
        if self.step_type == 'ai_chat':
            return self._process_step_ai_chat(mail_channel)
        return super()._process_step(mail_channel)
    
    # ✅ Thêm method xử lý AI Chat step
    def _process_step_ai_chat(self, mail_channel):
        """ Special type of step that enables AI chat functionality.
        Posts the initial message and waits for user input to process via AI. """
        
        posted_message = False
        if self.message:
            posted_message = mail_channel._chatbot_post_message(
                self.chatbot_script_id, 
                plaintext2html(self.message)
            )
        
        return posted_message
    