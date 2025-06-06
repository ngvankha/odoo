{
    "name": "AI Portal Chatbot",
    "summary": "Tích hợp Chatbot AI vào giao diện Portal Odoo",
    "version": "1.0",
    "category": "Website/Portal",
    "author": "Your Company",
    "depends": ["portal", "ai_chat"],
    "data": [
        "views/assets.xml",
        "views/portal_chatbot.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "ai_portal_chatbot/static/src/js/portal_chatbot.js",
        ],
    },
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}