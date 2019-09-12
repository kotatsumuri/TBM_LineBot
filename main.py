from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    MemberJoinedEvent, MemberLeftEvent,
    FlexSendMessage, BubbleContainer, CarouselContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,
    ImageSendMessage
)

import os
import time

import firebase
import mTemplate

app = Flask(__name__)
firebase = firebase.Firebase()

#環境変数取得
CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

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

@handler.add(MessageEvent)
def handle_message(event):

    uid = event.source.user_id
    timestamp = firebase.line_user_data[uid]['timestamp']
    state = firebase.line_user_data[uid]['state']
    location = firebase.line_user_data[uid]['location']

    if time.time() - timestamp > 2 * 60:
        firebase.set_state(uid, 100)

    message = []

    if state == 100:
        if event.message.text == 'すべてのゴミ箱を表示':
            firebase.set_state(uid, 101)
            message.append(mTemplate.locationButton())
        elif event.message.text == '一番近いゴミ箱を検索':
            firebase.set_state(uid, 200)
            message.append(mTemplate.locationButton())
        elif event.message.text == '捨てられるものでゴミ箱を検索':
            firebase.set_state(uid, 300)
            message.append(mTemplate.locationButton())
        else:
            message.append(TextMessage(text = '下のメニューをタップしてください'))
    
    elif state == 101:
        firebase.set_state(uid, 100)
        firebase.set_location(uid, event.message.latitude, event.message.longitude)
        contents = []
        for key in firebase.get_trash_box_keys():
            distance = firebase.calc_distance(uid, key)
            trash_box_data = firebase.get_data_list()[key]
            space = trash_box_data['space']
            things = trash_box_data['things']
            position = trash_box_data['position']

            contents.append(mTemplate.trashbox_info_card(distance, space, things, position, True))

        message.append(FlexSendMessage(alt_text = 'ゴミ箱一覧',contents = CarouselContainer(contents = contents)))

    elif state == 200:
        if event.message.type == 'location':
            firebase.set_state(uid, 100)
            firebase.set_location(uid, event.message.latitude, event.message.longitude)
            
            key, distance = firebase.get_nearest_trash_box(uid, firebase.get_trash_box_keys())
            trash_box_data = firebase.get_data_list()[key]
            space = trash_box_data['space']
            things = trash_box_data['things']
            position = trash_box_data['position']
            message.append(mTemplate.trashbox_info_card(distance, space, things, position))
        else:
            message.append(mTemplate.locationButton())

    elif state == 300:
        if event.message.type == 'location':
            firebase.set_state(uid, 301)
            firebase.set_location(uid, event.message.latitude, event.message.longitude)
            message.append(mTemplate.thingsListButton(firebase.get_things_list()))
        else:
            message.append(mTemplate.locationButton())

    if message != []:
        line_bot_api.reply_message(event.reply_token,message)

    firebase.line_user_data[uid]['timestamp'] = time.time()

@handler.add(PostbackEvent)
def handle_postback(event):
    uid = event.source.user_id
    timestamp = firebase.line_user_data[uid]['timestamp']
    state = firebase.line_user_data[uid]['state']
    location = firebase.line_user_data[uid]['location']

    if time.time() - timestamp > 2 * 60:
        firebase.set_state(uid, 100)
    
    message = []

    if state == 301:
        code,thing = event.postback.data.split(',')
        if code == '301':
            
            key, distance = firebase.get_nearest_trash_box(uid, firebase.get_much_thing_keys(thing))
            trash_box_data = firebase.get_data_list()[key]
            space = trash_box_data['space']
            things = trash_box_data['things']
            position = trash_box_data['position']
            message.append(mTemplate.trashbox_info_card(distance, space, things, position))
            firebase.set_state(uid, 100)
        else:
            message.append(mTemplate.thingsListButton(firebase.get_things_list()))

    if message != []:
        line_bot_api.reply_message(event.reply_token,message)

    firebase.line_user_data[uid]['timestamp'] = time.time()

@handler.add(BeaconEvent)
def handle_beacon(event):
    message = []
    if event.beacon.type == 'enter':
        key = ''.join([event.beacon.hwid[i: i+2] for i in range(0, len(event.beacon.hwid), 2)])
        distance = firebase.calc_distance(uid, key)
        trash_box_data = firebase.get_data_list()[key]
        space = trash_box_data['space']
        things = trash_box_data['things']
        position = trash_box_data['position']
        message.append(TextMessage(text = '近くにゴミ箱があります'))
        message.append(mTemplate.trashbox_info_card(distance, space, things, position))
    
    if space < 90:
        line_bot_api.reply_message(event.reply_token,message)

if __name__ == "__main__":

    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)