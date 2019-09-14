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
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,
    ImageSendMessage
)

def locationButton():
    return TemplateSendMessage(
                alt_text='Buttons alt text', template=ButtonsTemplate(text='位置情報を送信して下さい', actions=[
                URIAction(label='位置情報を送信', uri='line://nv/location')
            ]))

def thingsListButton(things):
    actions = []

    for thing in things:
        actions.append(PostbackAction(label=thing, data='301,'+thing))

    return TemplateSendMessage(
        alt_text='Buttons alt text', 
        template=ButtonsTemplate(title='選択して下さい',text='捨てられるもの', actions=actions)
        )

def trashbox_info_card(distance = 100, space = 50, things = ['缶','燃えるゴミ'], position = {'lat':35.114514,'lng':135.191981}, carousel = False):
    bubble = BubbleContainer(
        body = BoxComponent(
            layout = 'vertical',
            contents = [
                TextComponent(
                    text = 'ここから' + (str(distance) + 'm' if distance < 1000 else str(distance * 0.001) + 'km'),
                    size = 'xl',
                    weight = 'bold'
                ),
                BoxComponent(
                    layout = 'vertical',
                    margin = 'md',
                    contents = [
                        SpacerComponent(
                            margin = 'md'
                        ),
                        TextComponent(
                            text = '空き容量',
                            size = 'md'
                        ),
                        TextComponent(
                            text = str(space) + '%',
                            size = 'xl',
                            weight = 'bold'
                        )
                    ]
                ),
                BoxComponent(
                    layout = 'vertical',
                    margin = 'md',
                    contents = [
                        SpacerComponent(
                            margin = 'md'
                        ),
                        TextComponent(
                            text = '捨てられるもの',
                            size = 'md'
                        ),
                        TextComponent(
                            text = ','.join(things),
                            size = 'xl',
                            weight = 'bold',
                            wrap = True,
                        )
                    ]
                )
            ]
        ),
        footer = BoxComponent(
            layout = 'vertical',
            contents = [
                ButtonComponent(
                    style = 'primary',
                    color = '#00bfff',
                    action = URIAction(
                        label = '地図で見る',
                        uri = 'https://www.google.com/maps?q=' + str(position['lat']) + ',' + str(position['lng'])
                    )
                )
            ]
        )
    )
    if carousel:
        return bubble
    return FlexSendMessage(alt_text="ゴミ箱情報", contents=bubble)

def all_map_button():
    bubble = BubbleContainer(
        layout = 'vertical',
        footer = BoxComponent(
            layout = 'vertical',
            contents = [
                ButtonComponent(
                    style = 'primary',
                    color = '#00bfff',
                    action = URIAction(
                        label = 'すべて地図で見る,
                        uri = 'https://procon30-tbm.firebaseapp.com/#/liff'
                    )
                )
            ]
        )
    )
    return FlexSendMessage(alt_text='すべて地図で見る', contents = bubble)