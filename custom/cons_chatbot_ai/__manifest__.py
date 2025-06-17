{
    'name': 'Chatbot AI Integration',
    'version': '16.0.1.0.0',
    'category': 'Website/Live Chat',
    'summary': 'AI Chat integration for Odoo Chatbot',
    'description': """
        This module extends the Odoo chatbot functionality with AI chat capabilities.
    """,
    'depends': ['im_livechat'],
    'data': [
        'views/chatbot_script_views.xml',
        'views/res_config_settings_views.xml',
        'security/ir.model.access.csv',
        'data/ir_config_parameter_data.xml', 
    ],
    'assets': {
        'im_livechat.assets_public_livechat': [
            ('prepend', 'cons_chatbot_ai/static/src/public_models/chatbot.js'),
            ('prepend', 'cons_chatbot_ai/static/src/public_models/livechat_button_view.js'),
            ('prepend', 'cons_chatbot_ai/static/src/public_models/public_livechat_window.js'),
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}