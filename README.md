# Slack ChatGPT Bot

A Slack bot that uses OpenAI's GPT-4o model to respond to messages in Slack channels.

## Features

- Receives messages via Slack webhook
- Processes messages using OpenAI's GPT-4o model
- Posts AI-generated responses back to the Slack channel
- Includes proper request verification for security

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   npm install
   ```
3. Create a `.env` file with the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   SLACK_BOT_TOKEN=your_slack_bot_token
   SLACK_SIGNING_SECRET=your_slack_signing_secret
   ```
4. Start the server:
   ```
   npm start
   ```

## Slack App Configuration

1. Create a new Slack app at https://api.slack.com/apps
2. Enable Event Subscriptions and point to your server's `/slack-events` endpoint
3. Subscribe to the `message.channels` event
4. Install the app to your workspace
5. Copy the Bot Token and Signing Secret to your `.env` file

## Webhook Usage

The bot can also be triggered via a webhook at the `/webhook` endpoint. Send a POST request with the following JSON structure:

```json
{
  "channel_id": "C12345",
  "text": "Your message here"
}
```

## Security

- All requests from Slack are verified using the signing secret
- API keys are stored in environment variables, not in the code
- Request timestamp verification prevents replay attacks

## License

ISC
