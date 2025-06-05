// THIS FILE IS A PART OF PUBLIC REPOSITORY https://github.com/yonitjio/exploring-odoo
// 
// This software is released under the MIT License.
// https://opensource.org/licenses/MIT
// 
// THIS SOFTWARE IS EXPERIMENTAL AND FOR EDUCATIONAL PURPOSE ONLY.
// DO NOT USE IT IN PRODUCTION.

import { Component } from "@odoo/owl";

export class AiMessage extends Component {
    static template = "ai_chat_base.AiMessage";
    static props = {
        name: { type: String },
        role: { validate:  e => ["assistant", "user"].includes(e) },
        message: { type: String },
        avatar: { type: String },
        isProcessing: { type: Boolean }
    }

    get isAssistant() {
        return this.props.role == "assistant" ? true : false;
    }

    setup() {
        super.setup();
    }
}
