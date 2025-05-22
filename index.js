require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const crypto = require('crypto');

const app = express();
const PORT = process.env.PORT || 3000;

app.use((req, res, next) => {
  if (req.path === '/slack-events') {
    bodyParser.json({
      verify: (req, res, buf) => {
        req.rawBody = buf;
      }
    })(req, res, next);
  } else {
    bodyParser.json()(req, res, next);
  }
});

const verifySlackRequest = (req, res, next) => {
  if (!process.env.SLACK_SIGNING_SECRET || process.env.SLACK_SIGNING_SECRET === 'your_slack_signing_secret') {
    console.warn('Warning: Slack request verification is disabled. Set SLACK_SIGNING_SECRET for production use.');
    return next();
  }

  const slackSignature = req.headers['x-slack-signature'];
  const timestamp = req.headers['x-slack-request-timestamp'];
  
  const currentTime = Math.floor(Date.now() / 1000);
  if (Math.abs(currentTime - timestamp) > 300) {
    return res.status(400).send('Verification failed: Request is too old');
  }
  
  const sigBasestring = `v0:${timestamp}:${req.rawBody}`;
  const mySignature = 'v0=' + 
    crypto.createHmac('sha256', process.env.SLACK_SIGNING_SECRET)
      .update(sigBasestring, 'utf8')
      .digest('hex');
  
  if (crypto.timingSafeEqual(
    Buffer.from(mySignature, 'utf8'),
    Buffer.from(slackSignature, 'utf8')
  )) {
    next();
  } else {
    return res.status(400).send('Verification failed: Invalid signature');
  }
};

app.post('/slack-events', (req, res) => {
  if (req.body.type === 'url_verification') {
    return res.json({ challenge: req.body.challenge });
  }
  
  handleSlackEvent(req.body)
    .then(() => res.status(200).send())
    .catch(error => {
      console.error('Error processing Slack event:', error);
      res.status(500).send('Error processing event');
    });
});

async function handleSlackEvent(payload) {
  try {
    const event = payload.event || {};
    const channelId = event.channel || payload.channel_id;
    const text = event.text || payload.text || payload.trigger?.text;
    
    if (!text || !channelId) {
      console.warn('Missing text or channel ID in payload:', payload);
      return;
    }
    
    if (event.bot_id) {
      return;
    }
    
    const chatGptResponse = await callChatGPT(text);
    
    await postToSlack(channelId, chatGptResponse);
    
  } catch (error) {
    console.error('Error in handleSlackEvent:', error);
    throw error;
  }
}

async function callChatGPT(text) {
  try {
    const response = await axios.post(
      'https://api.openai.com/v1/chat/completions',
      {
        model: 'gpt-4o',
        messages: [
          {
            role: 'system',
            content: 'あなたはSlackで使われるAIです。質問には簡潔で、わかりやすく、時にはユーモアを交えて答えてください。'
          },
          {
            role: 'user',
            content: text
          }
        ],
        temperature: 0.7
      },
      {
        headers: {
          'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    return response.data.choices[0].message.content;
  } catch (error) {
    console.error('Error calling OpenAI API:', error.response?.data || error.message);
    return 'Sorry, I encountered an error while processing your request.';
  }
}

async function postToSlack(channelId, text) {
  try {
    await axios.post(
      'https://slack.com/api/chat.postMessage',
      {
        channel: channelId,
        text: text
      },
      {
        headers: {
          'Authorization': `Bearer ${process.env.SLACK_BOT_TOKEN}`,
          'Content-Type': 'application/json'
        }
      }
    );
  } catch (error) {
    console.error('Error posting to Slack:', error.response?.data || error.message);
    throw error;
  }
}

app.post('/webhook', (req, res) => {
  handleSlackEvent(req.body)
    .then(() => res.status(200).send('Webhook processed successfully'))
    .catch(error => {
      console.error('Error processing webhook:', error);
      res.status(500).send('Error processing webhook');
    });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
