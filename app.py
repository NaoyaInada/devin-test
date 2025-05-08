import os
from flask import Flask, request, jsonify
from slack_sdk import WebClient

app = Flask(__name__)

# 環境変数からトークンを読み込み
slack_token = os.environ.get("SLACK_BOT_TOKEN")
client = WebClient(token=slack_token)

@app.route('/slack-events', methods=['POST'])
def slack_events():
    data = request.get_json()

    # URL検証用のchallenge応答
    if data.get('challenge'):
        return jsonify({'challenge': data['challenge']})

    # イベント情報を取り出し
    event = data.get('event', {})
    channel_id = event.get('channel')
    user = event.get('user')
    text = event.get('text')

    # Bot 自身のメッセージには反応しない
    if user and not event.get('bot_id'):
        # 例: "Hello" と来たら "Hello, @ユーザーさん!" と返す
        reply = f"Received your message: \"{text}\""
        client.chat_postMessage(channel=channel_id, text=reply)

    # 常に 200 OK を返して ACK
    return '', 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
