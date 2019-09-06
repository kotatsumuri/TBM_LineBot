from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FollowEvent
)
import os

import firebase

app = Flask(__name__)
firebase = firebase.Firebase()

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(FollowEvent)
def handle_follow(event):
    firebase.insert_user_data(event.source.user_id)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    '''
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))
    '''
    uid = event.source.user_id
    state = firebase.line_user_data[uid]['state']
    location = firebase.line_user_data[uid]['location']
    if state == 100:
        if event.message.text == 'すべてのゴミ箱を表示':
            firebase.line_user_data[uid]['state'] = 200
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text = '200')
            )
        elif event.message.text == '一番近いゴミ箱を検索':
            firebase.line_user_data[uid]['state'] = 300
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text = '300')
            )
        elif event.message.text == '捨てられるものでゴミ箱を検索':
            firebase.line_user_data[uid]['state'] = 400
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text = '400')
            )
        
        

if __name__ == "__main__":

    port = int(os.getenv("PORT", 5000))
    app.run(host="localhost", port=port)