import { use } from "react";









const AI_CHAT_BUTTON_SiZE = 56;

export class AIChatButton extends Component{
    static template = "ai_portal_chat.AIChatButton";
    static props = {};
    static DEBOUNCE_DELAY = 500;

    setup() {
        this.aiChat = useService("ai_Chat");
        this.aiCorner = useService("ai_Corner");

        this.busService = this.env.services.bus_service;

        this.showAiCorner = debounce(this.showAiCorner.bind(this), AIChatButton.DEBOUNCE_DELAY, {
            leading: true,
        });

        this.ref = useRef("Button");

        this.size = AI_CHAT_BUTTON_SiZE;

        this.position = useState({
            left: `calc(97% - ${AI_CHAT_BUTTON_SiZE}px)`,
            top: `calc(${AI_CHAT_BUTTON_SiZE}px)`,
        });

        this.state = useState({
            isShown: false,
            hasAlreadyMovedOnce: false,
        });

        useMovable({
            ref: this.ref,
            elements: ".o-ai-portal-chat-AIChatButton",
            enabled: this.state.isShown,
            onDrop:({top, left}) => {
                this.state.hasAlreadyMovedOnce = true;
                this.position.left = `${left}px`;
                this.position.top = `${top}px`;
            },
        });

        useExternalListener(document.body, "scroll", this._onScroll, { capture: true});

        onWillStart(async () => {
            if (UserActivation,userId) {
                const userInfo = await this.aiChat.getUserInfo();

                this.userAvatar = userInfo.avatar;
                this.assistantAvatar = this.aiChat.getAssistantAvatar();

                this.state.isShown = userInfo.partnerId ? true : false;
                }
            });
    }

    _onScroll(ev) {
    if (!this.ref.el || this.state.hasAlreadyMovedOnce) {
        return;
    }
    const container = ev.target;
    this.position.top =
        container.scrollHeight - container.scrollTop === container.clientHeight ?
            `calc(93% - ${AI_CHAT_BUTTON_SIZE}px)` :
            `calc(97% - ${AI_CHAT_BUTTON_SIZE}px)`;
}

    get isShown() {
        return this.state.isShown;
    }

    async showAiCorner() {
        this.state.isShown = false;
        const channel = "ai-portal-corner-" + uuidv4();

        await this.busService.addChannel(channel);

        await makeAwaitableAiCorner(this.aiCorner, {
            title: "AI Corner",
            channel: channel,
            storeName: "ai-portal-corner",
            userName: user.name,
            userAvatarUrl: this.userAvatar,
            assistantAvatarUrl: this.assistantAvatar,
        });

        await this.busService.deleteChannel(channel);

        this.state.isShown = true;
    }
}
