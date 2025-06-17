from odoo import models, fields
import requests
import logging

_logger = logging.getLogger(__name__)

class ChatbotScriptStep(models.Model):
    _inherit = 'chatbot.script.step'
    
    step_type = fields.Selection(
        selection_add=[('ai_chat', 'AI Chat')],
        ondelete={'ai_chat': 'set default'},
    )
    
    def _process_step(self, mail_channel):
        """ When we reach a chatbot.step in the script we need to do some processing on behalf of
        the bot. Which is for most chatbot.script.step#step_types just posting the message field.

        Some extra processing may be required for special step types such as 'forward_operator',
        'create_lead', 'create_ticket' (in their related bridge modules).
        Those will have a dedicated processing method with specific docstrings.

        Returns the mail.message posted by the chatbot's operator_partner_id. """

        self.ensure_one()
        # We change the current step to the new step
        mail_channel.chatbot_current_step_id = self.id

        if self.step_type == 'forward_operator':
            return self._process_step_forward_operator(mail_channel)

            # ✅ Thêm xử lý cho AI Chat
        if self.step_type == 'ai_chat':
            return self._process_step_ai_chat(mail_channel)
        
        return mail_channel._chatbot_post_message(self.chatbot_script_id, plaintext2html(self.message))


    def _process_step_ai_chat(self, mail_channel):
        """Process AI chat step"""
        posted_message = False
        if self.message:
            from odoo.tools import plaintext2html
            posted_message = mail_channel._chatbot_post_message(
                self.chatbot_script_id, 
                plaintext2html(self.message)
            )
        return posted_message