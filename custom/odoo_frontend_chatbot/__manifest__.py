# -*- coding: utf-8 -*-
{
    'name': 'Odoo Frontend Chatbot',
    'version': '16.0.1.0.0',
    'category': 'Productivity/Discuss',
    'summary': 'Floating chatbot in Odoo frontend (similar to im_livechat but for internal use)',
    'description': """
        This module adds a floating chatbot widget in Odoo frontend interface,
        similar to website livechat but integrated with OdooBot for internal users.
        
        Features:
        - Floating chat button in bottom right corner
        - Chat window with OdooBot integration
        - AI-powered responses (if ai_bot module is installed)
        - Persistent chat sessions
        - Modern UI similar to im_livechat
    """,
    'depends': [
        'web', 
        'mail', 
        'mail_bot'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'data/ir_config_parameter_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'odoo_frontend_chatbot/static/src/scss/chatbot.scss',
            'odoo_frontend_chatbot/static/src/js/services/chatbot_service.js',
            'odoo_frontend_chatbot/static/src/js/components/chatbot_button.js',
            'odoo_frontend_chatbot/static/src/js/components/chatbot_window.js',
            'odoo_frontend_chatbot/static/src/js/main.js',
            'odoo_frontend_chatbot/static/src/xml/chatbot_templates.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
