/** @odoo-module **/

import { patch } from '@web/core/utils/patch';
import { registerModel } from '@mail/model/model_core';

patch(registerModel({name: 'LivechatButtonView'}), 'cons_chatbot_ai.LivechatButtonView', {
    recordMethods: {
        /**
         * @private
         */
        _sendMessageChatbotAfter() {
            if (this.messaging.publicLivechatGlobal.chatbot.isRedirecting) {
                return;
            }
            if (
                this.messaging.publicLivechatGlobal.chatbot.isActive &&
                this.messaging.publicLivechatGlobal.chatbot.currentStep &&
                this.messaging.publicLivechatGlobal.chatbot.currentStep.data
            ) {
                if (
                    this.messaging.publicLivechatGlobal.chatbot.currentStep.data.chatbot_step_type === 'forward_operator' &&
                    this.messaging.publicLivechatGlobal.chatbot.currentStep.data.chatbot_operator_found
                ) {
                    return; // operator has taken over the conversation, let them speak
                } else if (this.messaging.publicLivechatGlobal.chatbot.currentStep.data.chatbot_step_type === 'free_input_multi') {
                    this.messaging.publicLivechatGlobal.chatbot.debouncedAwaitUserInput();
                } 
                // ✅ Thêm xử lý cho AI Chat
                else if (this.messaging.publicLivechatGlobal.chatbot.currentStep.data.chatbot_step_type === 'ai_chat') {
                    // Cho AI Chat, chúng ta process ngay lập tức và giữ input enabled
                    this.messaging.publicLivechatGlobal.chatbot.setIsTyping();
                    this.messaging.publicLivechatGlobal.chatbot.processAiChatStep().then(() => {
                        // Sau khi AI trả lời, enable input để user có thể tiếp tục chat
                        this.messaging.publicLivechatGlobal.chatWindow.enableInput();
                    });
                }

                else if (!this.messaging.publicLivechatGlobal.chatbot.shouldEndScript) {
                    this.messaging.publicLivechatGlobal.chatbot.setIsTyping();
                    this.messaging.publicLivechatGlobal.chatbot.update({
                        nextStepTimeout: setTimeout(
                            this.messaging.publicLivechatGlobal.chatbot.triggerNextStep,
                            this.messaging.publicLivechatGlobal.chatbot.messageDelay,
                        ),
                    });
                } else {
                    this.messaging.publicLivechatGlobal.chatbot.endScript();
                }
                this.messaging.publicLivechatGlobal.chatbot.saveSession();
            }
        },
    },
});