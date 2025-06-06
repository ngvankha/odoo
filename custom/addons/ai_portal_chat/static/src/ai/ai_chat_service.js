














const aiChatService = {
    dependencies: ["orm", "localization"],

    getTarget() {
        return document.body;
    },

    initialize(env) {
        const target = this.getTarget();
        const root = makeRoot(target);

        makeShadow(root).then((shadow) => {
            new App(AIChatRoot, {
                env,
                getTemplate,
                translatableAttributes: ["data-tooltip"],
                translateFn: _t,
                dev: env.debug,
            }).mount(shadow);
        });

        return root
    },

    start(env, services) {
    const root = this.initialize(env);
    
    async function chat(channel, message, history, { context = {}, streaming = false } = {}) {
        const res = await rpc("/ai_portal_chat/chat", {
            "channel": channel,
            "message": message,
            "history": history,
            "context": context,
            "streaming": streaming,
        });
        return res;
    

    }
}
}