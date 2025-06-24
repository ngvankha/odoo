/** @odoo-module */

import { registry } from "@web/core/registry";
export class AiBotService {
    constructor(env, services) {
        this.setup(env, services);
    }
    setup(env, services){
        this.env = env;
        this.rpc = services.rpc;
        this.notificationService = services.notification;
        this.user = services.user;
    }
    async _query(thread, query_text){
        try {
            const result = await this.rpc("/ai_bot/query", {
                thread_id: thread.id,
                thread_model: thread.model,
                thread_type: thread.type,
                author_id: this.user.partnerId,
                query: query_text,
            });
            
            // Hiển thị error nếu có
            if (result.error) {
                this.notificationService.add(result.error, { type: 'danger' }); // ✅ Đúng
            }

            return result;
        } catch (error) {
            console.error("AI Bot error:", error);
            this.notification.add("Failed to process AI request", { type: 'danger' });
            return { error: error.message }; // ✅ Thêm return
        }
    }
    
    async query(thread, query_text) {
        console.log("AI Bot query called:", { thread, query_text });
        setTimeout(async () => {
            const result = await this._query(thread, query_text); // ✅ Store result
            console.log("AI Bot result:", result); // ✅ Debug log
        }, 250);
    }
}

const aiBotService = {
    dependencies: [
        "rpc",
        "user",
        "notification",
    ],
    start(env, services) {
        return new AiBotService(env, services);
    },
};

registry.category("services").add("ai.bot", aiBotService);
