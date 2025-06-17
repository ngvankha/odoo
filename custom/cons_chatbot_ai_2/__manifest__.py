{
    'name': 'Chatbot AI Extension',
    'version': '1.0.0',
    'category': 'Website/Live Chat',
    'summary': 'AI Chat functionality for Odoo Live Chat',
    'description': """
        This module extends the im_livechat module with AI chat capabilities.
        It allows integration with external AI services via webhooks.
    """,
    'author': 'Your Company',
    'depends': ['im_livechat'],
    'data': [
        'security/ir.model.access.csv',
        'views/chatbot_script_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'cons_chatbot_ai/static/src/public_models/chatbot_ai.js',
            'cons_chatbot_ai/static/src/public_models/livechat_button_view_patch.js',
            'cons_chatbot_ai/static/src/public_models/public_livechat_window_patch.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}