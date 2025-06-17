# cons_chatbot_ai

This module extends the functionality of the existing `im_livechat` module by introducing AI chat capabilities. It allows for seamless integration with an AI service to enhance user interactions within the live chat environment.

## Features

- **AI Chat Integration**: Provides a step in the chatbot script that allows for AI-driven responses based on user inputs.
- **Webhook Configuration**: Allows users to configure the webhook URL for the AI service directly from the chatbot script views.
- **Modular Design**: Built as a separate module that can be easily maintained and updated without affecting the core live chat functionality.

## Installation

1. Place the `cons_chatbot_ai` directory in your Odoo addons path.
2. Update the app list in Odoo.
3. Install the `cons_chatbot_ai` module from the Odoo apps interface.

## Usage

Once installed, you can configure the AI chat step within your existing chatbot scripts. Navigate to the chatbot script configuration and set the webhook URL for the AI service. The AI chat step will now be available for use in your chatbot flows.

## Development

This module is designed to be easily extendable. Developers can add new features or modify existing ones by editing the models, controllers, and views as needed.

## License

This module is licensed under the Odoo Community Association (OCA) license. Please refer to the LICENSE file for more details.