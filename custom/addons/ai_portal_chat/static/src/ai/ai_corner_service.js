











const aiCornerService = {
    dependencies: ["overlay", "ai_chat"],
    start(env, services) {
        const subEnv = reactive({});
        const root = services.ai_chat.root;

        const deactivate = () => {
            subEnv.isActive = false;
        };

        function openAiCorner(props, options = {}) {
            const close = () => {
                remove();
            };
            subEnv.close = close;
            deactivate(); 

            const remove = services.overlay.add({
                SubComponent: AiCorner,
                props: markRaw({ ...props,
                    close
                }),
                subEnv, 
                onRemove: () => {
                    deactivate();
                    options.onClose?.();
                },
                rootId: root.id,
            });

            return remove;
        }

        function closeAiCorner() {
            subEnv.close();
        }

        return {
            openAiCorner,
            closeAiCorner
        };
    },
};

registry.category("services").add("ai_corner", aiCornerService);