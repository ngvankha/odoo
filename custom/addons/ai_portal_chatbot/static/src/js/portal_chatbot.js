/** @odoo-module **/

import { mountComponent } from "@web/core/utils/components";
import { whenReady } from "@web/core/utils/when_ready";
// Import AiSidebar component từ ai_chat
import { AiSidebar } from "ai_chat/static/src/webclient/sidebar/ai_sidebar";

whenReady(() => {
    // Đảm bảo chỉ mount khi ở trang Portal
    if (window.location.pathname.startsWith("/my")) {
        const container = document.getElementById("ai_portal_chatbot_sidebar");
        if (container) {
            mountComponent(AiSidebar, {
                target: container,
                props: {
                    title: "AI Chatbot",
                    greetingMessage: "Xin chào! Tôi có thể giúp gì cho bạn?",
                    greetUser: true,
                    channel: "portal_ai_chatbot",
                }
            });
        }
    }
});