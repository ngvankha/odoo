

import { patch } from '@web/core/utils/patch';
import { registerModel } from '@mail/model/model_core';

patch(registerModel({name: 'PublicLivechatWindow'}), 'cons_chatbot_ai.PublicLivechatWindow', {
    recordMethods: {
        enableInput() {
            const $composerTextField = this.widget.$('.o_composer_text_field');
            $composerTextField
                .prop('disabled', false)
                .removeClass('text-center fst-italic bg-200')
                .val('')
                .focus();

            $composerTextField.off('keydown', this.messaging.publicLivechatGlobal.chatbot.onKeydownInput);
            // ✅ Enable cho AI Chat
            if (this.messaging.publicLivechatGlobal.chatbot.currentStep.data.chatbot_step_type === 'free_input_multi' ||
                this.messaging.publicLivechatGlobal.chatbot.currentStep.data.chatbot_step_type === 'ai_chat') { 
                $composerTextField.on('keydown', this.messaging.publicLivechatGlobal.chatbot.onKeydownInput);
            }
        },
    },
});