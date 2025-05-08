import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ─── Slack Events エンドポイント (必須) ───────────────────────────────
@app.route('/slack-events', methods=['POST'])
def slack_events():
    data = request.get_json()

    # URL 検証の challenge に応答
    if 'challenge' in data:
        return jsonify({'challenge': data['challenge']})

    # それ以外のイベントは無視して 200 OK を返す
    return '', 200

# ─── Slash Command 用エンドポイント (/company-info) ─────────────────────
@app.route('/company-info', methods=['POST'])
def company_info_slash():
    # Slack の Slash Command は form データで送られてくる
    company_name = request.form.get('text', '').strip()
    if not company_name:
        return jsonify({
            'response_type': 'ephemeral',
            'text': '使い方: `/company‐info 会社名` で企業情報を検索します'
        }), 200

    # OpenCorporates API を呼び出して会社を検索
    resp = requests.get(
        'https://api.opencorporates.com/v0.4/companies/search',
        params={'q': company_name}
    )
    data = resp.json()
    companies = data.get('results', {}).get('companies', [])

    # 結果を組み立て
    if not companies:
        text = f'企業「{company_name}」は見つかりませんでした。'
    else:
        top = companies[0]['company']
        text = (
            f"*{top['name']}* の情報:\n"
            f"• Jurisdiction: {top.get('jurisdiction_code', 'N/A')}\n"
            f"• Incorporated: {top.get('incorporation_date', 'N/A')}\n"
            f"• Status: {top.get('current_status', 'N/A')}"
        )

    # チャンネル全体に見える形で返信
    return jsonify({
        'response_type': 'in_channel',
        'text': text
    }), 200

# ─── アプリ起動 ───────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Render.com をはじめ多くの PaaS は PORT 環境変数を使います
    app.run(host='0.0.0.0', port=port)




