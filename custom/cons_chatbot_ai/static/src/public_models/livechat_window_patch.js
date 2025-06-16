/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PublicLivechatWindow } from "@im_livechat/public_models/public_livechat_window";

patch(PublicLivechatWindow.prototype, {
    enableInput() {
        const $composerTextField = this.widget.$('.o_composer_text_field');
        $composerTextField
            .prop('disabled', false)
            .removeClass('text-center fst-italic bg-200')
            .val('')
            .focus();

        // Remove existing keydown handlers
        $composerTextField.off('keydown', this.messaging.publicLivechatGlobal.chatbot.onKeydownInput);
        
        // Check if chatbot is active and has current step
        if (this.messaging.publicLivechatGlobal.chatbot && 
            this.messaging.publicLivechatGlobal.chatbot.currentStep && 
            this.messaging.publicLivechatGlobal.chatbot.currentStep.data) {
            
            const stepType = this.messaging.publicLivechatGlobal.chatbot.currentStep.data.chatbot_step_type;
            
            // Special handling for AI chat steps
            if (stepType === 'ai_chat') {
                // Set placeholder for AI chat
                $composerTextField.attr('placeholder', 'Ask me anything...');
            }
            // Handle free_input_multi normally
            else if (stepType === 'free_input_multi') {
                $composerTextField.on('keydown', this.messaging.publicLivechatGlobal.chatbot.onKeydownInput);
            }
        }
    },

    /**
     * Override disableInput to handle AI chat typing states
     */
    disableInput(disableText) {
        const $composerTextField = this.widget.$('.o_composer_text_field');
        
        // For AI chat, show appropriate typing message if not provided
        if (this.messaging.publicLivechatGlobal.chatbot && 
            this.messaging.publicLivechatGlobal.chatbot.currentStep && 
            this.messaging.publicLivechatGlobal.chatbot.currentStep.data &&
            this.messaging.publicLivechatGlobal.chatbot.currentStep.data.chatbot_step_type === 'ai_chat' &&
            !disableText) {
            disableText = 'AI is thinking...';
        }
        
        // Apply the disable state
        $composerTextField
            .prop('disabled', true)
            .addClass('text-center fst-italic bg-200')
            .val(disableText || '');
    },

    /**
     * Override renderMessages to handle AI chat specific UI
     */
    renderMessages() {
        const shouldScroll = !this.isFolded && this.publicLivechatView.widget.isAtBottom();
        this.widget.render();
        if (shouldScroll) {
            this.publicLivechatView.widget.scrollToBottom();
        }
        const self = this;

        this.widget.$('.o_thread_message:last .o_livechat_chatbot_options li').each(function () {
            $(this).on('click', self.messaging.publicLivechatGlobal.livechatButtonView.widget._onChatbotOptionClicked.bind(self.messaging.publicLivechatGlobal.livechatButtonView.widget));
        });

        this.widget.$('.o_livechat_chatbot_main_restart').on('click', (ev) => {
            ev.stopPropagation();
            this.messaging.publicLivechatGlobal.livechatButtonView.onChatbotRestartScript(ev);
        });

        if (this.messaging.publicLivechatGlobal.messages.length !== 0) {
            const lastMessage = this.messaging.publicLivechatGlobal.lastMessage;
            const stepAnswers = lastMessage.widget.getChatbotStepAnswers();
            if (stepAnswers && stepAnswers.length !== 0 && !lastMessage.widget.getChatbotStepAnswerId()) {
                this.disableInput(this.env._t("Select an option above"));
            }
        }
        
        // Additional handling for AI chat steps
        if (this.messaging.publicLivechatGlobal.chatbot && 
            this.messaging.publicLivechatGlobal.chatbot.currentStep && 
            this.messaging.publicLivechatGlobal.chatbot.currentStep.data &&
            this.messaging.publicLivechatGlobal.chatbot.currentStep.data.chatbot_step_type === 'ai_chat') {
            
            const $composerTextField = this.widget.$('.o_composer_text_field');
            if (!$composerTextField.prop('disabled')) {
                $composerTextField.attr('placeholder', 'Ask me anything...');
            }
            
            // Hide restart button during active AI conversation unless explicitly needed
            const $restartButton = this.widget.$('.o_livechat_chatbot_main_restart');
            if ($restartButton.length && !this.messaging.publicLivechatGlobal.chatbot.hasRestartButton) {
                $restartButton.hide();
            }
        }
    },

    get inputPlaceholder() {
        // Check if we have AI chat step
        if (this.messaging.publicLivechatGlobal.chatbot && 
            this.messaging.publicLivechatGlobal.chatbot.isActive &&
            this.messaging.publicLivechatGlobal.chatbot.currentStep && 
            this.messaging.publicLivechatGlobal.chatbot.currentStep.data &&
            this.messaging.publicLivechatGlobal.chatbot.currentStep.data.chatbot_step_type === 'ai_chat') {
            return 'Ask me anything...';
        }
        
        if (this.messaging.publicLivechatGlobal.livechatButtonView.inputPlaceholder) {
            return this.messaging.publicLivechatGlobal.livechatButtonView.inputPlaceholder;
        }
        return this.env._t("Say something");
    }
});