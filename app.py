from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    return 'App is running!', 200

@app.route('/slack-events', methods=['POST'])
def slack_events():
    data = request.json
    print("Received from Slack:", data)
    return 'Received!', 200
