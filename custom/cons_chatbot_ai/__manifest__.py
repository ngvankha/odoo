{
    'name': 'Chatbot AI Integration',
    'version': '1.0',
    'category': 'Website/Live Chat',
    'summary': 'AI Chat integration for Odoo Chatbot',
    'description': """
        This module extends the Odoo chatbot functionality with AI chat capabilities.
        It integrates with external AI services through webhooks to provide intelligent
        conversational responses.
    """,
    'depends': ['im_livechat'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_parameter_data.xml',
        'views/chatbot_script_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'cons_chatbot_ai/static/src/public_models/chatbot_step_patch.js',
            'cons_chatbot_ai/static/src/public_models/livechat_button_view_patch.js',
            'cons_chatbot_ai/static/src/public_models/livechat_window_patch.js', 
            'cons_chatbot_ai/static/src/public_models/chatbot_ai_extension.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}