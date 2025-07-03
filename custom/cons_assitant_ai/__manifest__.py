# -*- coding: utf-8 -*-
{
    'name': 'Chatbot Assistant AI',
    'version': '1.0.0',
    'category': 'Uncategorized',
    'summary': 'AI chatbot assistant in Odoo backend',
    'description': """
            Cons Assistant AI Module
            ========================
            Module AI chatbot assistant in Odoo backend
    """,
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'cons_assitant_ai/static/src/js/chatbot_widget.js',
            'cons_assitant_ai/static/src/css/chatbot.css',
            'cons_assitant_ai/static/src/xml/chatbot_template.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
