import os
import requests
from flask import Flask, request, jsonify
from slack_sdk import WebClient

app = Flask(__name__)

slack_token = os.environ["SLACK_BOT_TOKEN"]
client = WebClient(token=slack_token)

# 既存の /slack-events は省略…

@app.route('/company-info', methods=['POST'])
def company_info():
    data = request.get_json()
    name = data.get("name")
    if not name:
        return jsonify({"error": "name field is required"}), 400

    # OpenCorporates API を叩く
    url = f"https://api.opencorporates.com/v0.4/companies/search"
    params = {"q": name}
    resp = requests.get(url, params=params)
    js = resp.json()

    # 結果を抽出
    companies = js.get("results", {}).get("companies", [])
    if not companies:
        return jsonify({"error": "no company found"}), 200

    top = companies[0]["company"]
    result = {
        "company_name": top.get("name"),
        "jurisdiction_code": top.get("jurisdiction_code"),
        "incorporation_date": top.get("incorporation_date"),
        "current_status": top.get("current_status")
    }

    # Slack にも投稿したい場合（オプション）
    channel = data.get("channel_id")
    if channel:
        text = (
            f"*{result['company_name']}* の情報:\n"
            f"• Jurisdiction: {result['jurisdiction_code']}\n"
            f"• Incorporated: {result['incorporation_date']}\n"
            f"• Status: {result['current_status']}"
        )
        client.chat_postMessage(channel=channel, text=text)

    return jsonify(result), 200

