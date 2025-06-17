from odoo import models, fields, api
from odoo.tools import plaintext2html

class ChatbotScriptStep(models.Model):
    _inherit = 'chatbot.script.step'
    
    # Extend selection với ai_chat option
    step_type = fields.Selection(
        selection_add=[('ai_chat', 'AI Chat')],
        ondelete={'ai_chat': 'set default'},
    )
    
    def _process_step(self, mail_channel):
        """Override để xử lý AI chat step"""
        self.ensure_one()
        # We change the current step to the new step
        mail_channel.chatbot_current_step_id = self.id

        if self.step_type == 'forward_operator':
            return self._process_step_forward_operator(mail_channel)

        #  Thêm xử lý cho AI Chat
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
    
    #  Thêm method để xử lý user input cho AI chat
    def _process_answer(self, mail_channel, message_body):
        """Override để xử lý AI chat input"""
        if self.step_type == 'ai_chat':
            # AI chat không chuyển step, vẫn ở step hiện tại
            return self
        
        # Gọi method gốc cho các step khác
        return super()._process_answer(mail_channel, message_body)