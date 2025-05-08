from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return 'App is running!', 200

@app.route('/slack-events', methods=['POST'])
def slack_events():
    data = request.get_json()
    
    # Slack verification challenge
    if 'challenge' in data:
        return jsonify({'challenge': data['challenge']})

    # 通常のイベント処理（ここは後で拡張）
    print("Slack Event:", data)
    return 'Received!', 200
