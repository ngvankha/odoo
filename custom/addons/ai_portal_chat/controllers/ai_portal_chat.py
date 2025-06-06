import logging 
_logger = logging.getLogger(__name__)

import json
from urllib.request import urlopen, Request

from odoo import http
from odoo.http import request

from ..ai.ai_bot import AiBot

class AiPortalChatController(http.Controller):
    @http.route('/ai_portal_chat/stream', type='json', auth='user', website=True)
    def ai_chat(self, channel, message, history, context, streaming):
        env = request.env
        bot = AiBot(env, context)
        res = bot.chat(channel, message, history, streaming)
        
        return res

    # region alternative methods to get blog information
    
    @http.route('/ai_portal_chat/assets.<any(css,js):ext>', type='http', auth='public')
    def assets_embed(self, ext, **kwargs):
        if ext not in ('css', 'js'):
            return request.not_found()
        
        bundle = 'ai_portal_chat.assets'
        asset = request.env['ir.qweb']._get_asset_bundle(bundle)
        stream = request.env['ir.binary']._get_stream_from(getattr(asset, ext)())
        return stream.get_response()
    
    @http.route('/ai_portal_chat/font-awesome', type='http', auth='none', cors="*")
    def fontawesome(self, **kwargs):
        return http.Stream.from_path('web/static/src/libs/fontawesome/fonts/fontawesome-webfont.woff2').get_response()

    @http.route('/ai_portal_chat/odoo_ui_icons', type='http', auth='none', cors="*")
    def odoo_ui_icons(self, **kwargs):
        return http.Stream.from_path('web/static/lib/odoo_ui_icons/fonts/odoo-ui-icons.woff2').get_response()