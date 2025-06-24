/* @odoo-module */

import { Composer } from "@mail/core/common/composer";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

patch(Composer.prototype, {
    setup() {
        super.setup();
        this.aiBotService = useService("ai.bot");
    },
    
    async _sendMessage(value, postData) {
        console.log("Composer _sendMessage called:", { value, postData });
        
        // Gọi parent method trước
        const result = await super._sendMessage(value, postData);
        
        // Sau đó trigger AI bot
        const thread = this.props.composer.thread;
        console.log("Thread info:", { 
            id: thread.id, 
            model: thread.model, 
            type: thread.type,
            displayName: thread.displayName 
        });
        
        if (thread && value) {
            await this.aiBotService.query(thread, value);
        }
        
        return result;
    }
});
