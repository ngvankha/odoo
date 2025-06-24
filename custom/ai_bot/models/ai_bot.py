# -*- coding: utf-8 -*-

import logging
_logger = logging.getLogger(__name__)

from odoo import models, api
from werkzeug.exceptions import NotFound

class AiBot(models.AbstractModel):
    _name = 'mail.bot.ai'
    _description = 'AI Bot with N8N Integration'

    @api.model
    def query(self, thread_id, thread_model, thread_type, author_id, query):
        """
        Simplified query method - all AI processing is handled by controller via n8n
        """
        _logger.info(f"AI Bot query called: thread_id={thread_id}, model={thread_model}, type={thread_type}, author={author_id}")
        
        thread = self.env[thread_model].browse(thread_id)
        if not thread:
            _logger.error(f"Thread not found: {thread_model}[{thread_id}]")
            raise NotFound()

        try:
            ai_bot_channel = self.env.ref('ai_bot.channel_ai_bot')
            ai_bot_user = self.env.ref("ai_bot.user_ai_bot")
            ai_bot_partner = self.env.ref("ai_bot.partner_ai_bot")
        except ValueError as e:
            _logger.error(f"AI Bot data not found: {e}")
            return False

        _logger.info(f"AI Bot Partner ID: {ai_bot_partner.id}, Author ID: {author_id}")
        _logger.info(f"Thread display name: '{thread.display_name}', Type: {thread_type}")
        _logger.info(f"Query content: '{query}'")

        # Kiểm tra điều kiện trigger bot
        should_respond = False
        
        # Case 1: Chat riêng với AI Bot
        if (author_id != ai_bot_partner.id and 
            thread_type == 'chat' and 
            ai_bot_partner.name.lower() in thread.display_name.lower()):
            should_respond = True
            _logger.info("AI Bot triggered: Private chat with AI Bot")
            
        # Case 2: Mention trong channel AIBot
        elif (author_id != ai_bot_partner.id and 
              thread_type == 'channel' and 
              ai_bot_channel.display_name.lower() == thread.display_name.lower()):
            should_respond = True
            _logger.info("AI Bot triggered: Message in AI Bot channel")
            
        # Case 3: Mention @AI Bot trong bất kỳ channel nào
        elif (author_id != ai_bot_partner.id and 
              ('@' + ai_bot_partner.name.lower()) in query.lower()):
            should_respond = True
            _logger.info("AI Bot triggered: @mention in any channel")

        _logger.info(f"Should respond: {should_respond}")
        
        if should_respond:
            _logger.info("AI Bot triggered for N8N processing: %s", query)
            return True
        
        return False