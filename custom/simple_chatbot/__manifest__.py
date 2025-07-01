# -*- coding: utf-8 -*-
{
    'name': 'Simple Chatbot',
    'version': '1.0.0',
    'category': 'Productivity',
    'summary': 'Hiển thị chatbot đơn giản trong backend Odoo',
    'description': """
Simple Chatbot Module
=====================
Module đơn giản hiển thị chatbot trong giao diện backend Odoo 16
    """,
    'depends': ['base', 'web'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'simple_chatbot/static/src/js/chatbot_widget.js',
            'simple_chatbot/static/src/css/chatbot.css',
            'simple_chatbot/static/src/xml/chatbot_template.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
