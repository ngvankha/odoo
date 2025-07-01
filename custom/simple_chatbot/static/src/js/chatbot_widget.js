/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class SimpleChatbot extends Component {
    setup() {
        this.state = useState({
            isOpen: false,
            messages: [
                { text: "Xin chào! Tôi là chatbot của bạn. Tôi có thể giúp gì cho bạn?", isBot: true }
            ],
            currentMessage: ""
        });
    }

    toggleChatbot() {
        this.state.isOpen = !this.state.isOpen;
    }

    sendMessage() {
        if (this.state.currentMessage.trim()) {
            // Thêm tin nhắn của người dùng
            this.state.messages.push({
                text: this.state.currentMessage,
                isBot: false
            });

            // Phản hồi tự động từ bot
            setTimeout(() => {
                const responses = [
                    "Cảm ơn bạn đã nhắn tin!",
                    "Tôi hiểu rồi. Bạn cần hỗ trợ gì thêm không?",
                    "Đó là một câu hỏi hay. Để tôi kiểm tra giúp bạn.",
                    "Tôi sẽ ghi nhận yêu cầu của bạn."
                ];
                const randomResponse = responses[Math.floor(Math.random() * responses.length)];
                this.state.messages.push({
                    text: randomResponse,
                    isBot: true
                });
            }, 1000);

            this.state.currentMessage = "";
        }
    }

    onKeyPress(ev) {
        if (ev.key === 'Enter') {
            this.sendMessage();
        }
    }

    clearChat() {
        this.state.messages = [
            { text: "Xin chào! Tôi là chatbot của bạn. Tôi có thể giúp gì cho bạn?", isBot: true }
        ];
    }
}

SimpleChatbot.template = "simple_chatbot.ChatbotWidget";

// Đăng ký component như một systray item
registry.category("systray").add("SimpleChatbot", {
    Component: SimpleChatbot,
});

export default SimpleChatbot;
