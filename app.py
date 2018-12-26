from __future__ import unicode_literals
import pandas as pd
import numpy as np
import errno
import os
import sys
import tempfile
from argparse import ArgumentParser
from flask import Flask, request, abort
import random
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)



def rest_selector(reply_text): #待改進：如果某類型沒有餐廳就不要輸出
    # import the restaurant data
    all_restaurant = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vRR3IygA5p4RzvLnqct1YS_5PngAP9ANKdcK0fhTuWEI6zA52YrqFyS-dBex3b6lcqt5WM4kQE0r3Oh/pub?output=csv',header=0)
    res_loc, res_type = reply_text.split('_')
    potential_150_low = all_restaurant['restaurant'][(all_restaurant.type2 == res_type) & (all_restaurant.loc_type == res_loc) & (all_restaurant.price <= 150)].tolist()
    potential_150_up = all_restaurant['restaurant'][(all_restaurant.type2 == res_type) & (all_restaurant.loc_type == res_loc) & (all_restaurant.price > 150)].tolist()
    if len(potential_150_low) >=3:
        potential_150_low = [potential_150_low[i] for i in np.random.choice(len(potential_150_low),3,replace=False).tolist()]
    if len(potential_150_up) >=3:
        potential_150_up = [potential_150_up[i] for i in np.random.choice(len(potential_150_up),3,replace=False).tolist()] 
    
    # create actions for below $150 restaurant
    action_150_low = []
    if not potential_150_low:
        action_150_low.append(MessageAction(label='試試別的',text='吃吃'))
    else:
        for i in potential_150_low:
            action_150_low.append(MessageAction(label=i,text='吃@'+i))
    if len(action_150_low) < 3:
        n = 3 - len(action_150_low)
        action_150_low.extend([MessageAction(label='--',text='吃吃')] * n)
    # create actions for above $150 restaurant
    action_150_up = []
    if not potential_150_up:
        action_150_up.append(MessageAction(label='試試別的',text='吃吃'))
    else:
        for j in potential_150_up:
            action_150_up.append(MessageAction(label=j,text='吃@'+j))
    if len(action_150_up) < 3:
        n = 3 - len(action_150_up)
        action_150_up.extend([MessageAction(label='--',text='吃吃')] * n)
    
    carousel_template = CarouselTemplate(columns=[
                CarouselColumn(text='甲粗飽',thumbnail_image_url='https://i.imgur.com/fIKfTIi.jpg', actions=action_150_low),
                CarouselColumn(text='大吃爆',thumbnail_image_url='https://i.imgur.com/fIKfTIi.jpg', actions=action_150_up),
            ])
    template_message = TemplateSendMessage(
        alt_text='Carousel alt text', template=carousel_template)

    return template_message
	
def rest_con(reply_text):
    all_restaurant = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vRR3IygA5p4RzvLnqct1YS_5PngAP9ANKdcK0fhTuWEI6zA52YrqFyS-dBex3b6lcqt5WM4kQE0r3Oh/pub?output=csv',header=0)
    res_eat, res_name = reply_text.split('@')
    res_location = all_restaurant['location'][all_restaurant.restaurant == res_name].tolist()
    res_menu = 	all_restaurant['menu pic'][all_restaurant.restaurant == res_name].tolist()
    res_open = all_restaurant['open hour'][all_restaurant.restaurant == res_name].tolist()
    res_food_pic = all_restaurant['food pic'][all_restaurant.restaurant == res_name].tolist()
    location_txt = '' ; menu_txt = '' ; open_txt = ''

    bubble = BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                url=res_food_pic[0],
                size='full',
                aspect_ratio='20:13',
                aspect_mode='cover',
                action=URIAction(uri='http://example.com', label='label')
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    # title
                    TextComponent(text=res_name, weight='bold', size='xl'),
                    # review
                    # info
                    BoxComponent(
                        layout='vertical',
                        margin='lg',
                        spacing='sm',
                        contents=[
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='Place',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        text=res_location[0],
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5
                                    )
                                ],
                            ),
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='Time',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        text=res_open[0],
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5,
                                    ),
                                ],
                            ),
                        ],
                    )
                ],
            ),
            footer=BoxComponent(
                layout='vertical',
                spacing='sm',
                contents=[
                    # callAction, separator, websiteAction
                    SpacerComponent(size='sm'),
                    # callAction
                    ButtonComponent(
                        style='link',
                        height='sm',
                        action=URIAction(label='CALL', uri='tel:000000'),
                    ),
                    # separator
                    SeparatorComponent(),
                    # websiteAction
                    ButtonComponent(
                        style='link',
                        height='sm',
                        action=URIAction(label='Menu', uri=res_menu[0])
                    )
                ]
            ),
        )
    message = FlexSendMessage(alt_text="hello", contents=bubble)
    return message


# Channel Access Token
line_bot_api = LineBotApi('03lCKiHH72CQak6lrU9vdhwyu5HUDEeihF4bQIxokPtct6L03QXfkHhvoFZI579Z95i9hdkX6eRbOWDOB+t0XwJMv/D70W7/x3wBX4+wCldtj4WpF7QC2yqClPExW/nrOUZMZJakON6zJsgAuR8N5wdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('fff9aae6226c58c93a7c5a8001e836f6')

# 監聽所有來自 /callback 的 Post Request
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


@handler.add(MessageEvent, message=TextMessage) # 處理文字訊息（message = TextMessage）
def handle_message(event):
    text = event.message.text # 使用者傳的訊息存成變數 text

    if  text == '發票':
        buttons_template = ButtonsTemplate(
            thumbnail_image_url='https://i.imgur.com/fIKfTIi.jpg',title='My buttons sample', text='哈', actions=[
                URIAction(label='Go to line.me', uri='https://line.me'),
                PostbackAction(label='ping', data='ping'),
                PostbackAction(label='ping with text', data='ping', text='ping'),
                MessageAction(label='Translate Rice', text='米') #Messageaction: 替使用者傳訊息，label為選項的文字，text為要傳的訊息
            ])
        template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message) # 送出訊息，訊息內容為'template_message'
    # 回覆吃吃的回傳訊息
    elif '_' in text:
        message = rest_selector(text)
        line_bot_api.reply_message(event.reply_token, message)
    elif '@' in text:
        message = rest_con(text)
        line_bot_api.reply_message(event.reply_token, message)
    elif text == '吃吃':
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text='大門',thumbnail_image_url='https://i.imgur.com/fIKfTIi.jpg', actions=[
                MessageAction(label='飯', text='大門_飯'),
                MessageAction(label='麵', text='大門_麵'),
                MessageAction(label='其他', text='大門_其他')
            ]),
            CarouselColumn(text='公館',thumbnail_image_url='https://i.imgur.com/fIKfTIi.jpg', actions=[
                MessageAction(label='飯', text='公館_飯'),
                MessageAction(label='麵', text='公館_麵'),
                MessageAction(label='其他', text='公館_其他')
            ]),
            CarouselColumn(text='溫州街',thumbnail_image_url='https://i.imgur.com/fIKfTIi.jpg', actions=[
                MessageAction(label='飯', text='溫州街_飯'),
                MessageAction(label='麵', text='溫州街_麵'),
                MessageAction(label='其他', text='溫州街_其他')
            ]),
            CarouselColumn(text='118巷',thumbnail_image_url='https://i.imgur.com/fIKfTIi.jpg', actions=[
                MessageAction(label='飯', text='118巷_飯'),
                MessageAction(label='麵', text='118巷_麵'),
                MessageAction(label='其他', text='118巷_其他')
            ]),
            CarouselColumn(text='校內',thumbnail_image_url='https://i.imgur.com/fIKfTIi.jpg', actions=[
                MessageAction(label='飯', text='校內_飯'),
                MessageAction(label='麵', text='校內_麵'),
                MessageAction(label='其他', text='校內_其他')
            ]),
        ])
        template_message = TemplateSendMessage(
            alt_text='Carousel alt text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'image_carousel':
        image_carousel_template = ImageCarouselTemplate(columns=[
            ImageCarouselColumn(image_url='https://i.imgur.com/NrFOHGo.jpg',
                                action=DatetimePickerAction(label='datetime',
                                                            data='datetime_postback',
                                                            mode='datetime')),
            ImageCarouselColumn(image_url='https://via.placeholder.com/1024x1024',
                                action=DatetimePickerAction(label='date',
                                                            data='date_postback',
                                                            mode='date'))
        ])
        template_message = TemplateSendMessage(
            alt_text='ImageCarousel alt text', template=image_carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'flex' or text == '推薦':
        bubble = BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                url='https://i.imgur.com/wT9Rjq7.jpg',
                size='full',
                aspect_ratio='20:13',
                aspect_mode='cover',
                action=URIAction(uri='http://example.com', label='label')
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    # title
                    TextComponent(text='Brown Cafe', weight='bold', size='xl'),
                    # review
                    BoxComponent(
                        layout='baseline',
                        margin='md',
                        contents=[
                            IconComponent(size='sm', url='https://example.com/gold_star.png'),
                            IconComponent(size='sm', url='https://example.com/grey_star.png'),
                            IconComponent(size='sm', url='https://example.com/gold_star.png'),
                            IconComponent(size='sm', url='https://example.com/gold_star.png'),
                            IconComponent(size='sm', url='https://example.com/grey_star.png'),
                            TextComponent(text='4.0', size='sm', color='#999999', margin='md',
                                          flex=0)
                        ]
                    ),
                    # info
                    BoxComponent(
                        layout='vertical',
                        margin='lg',
                        spacing='sm',
                        contents=[
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='Place',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        text='Shinjuku, Tokyo',
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5
                                    )
                                ],
                            ),
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='Time',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        text="10:00 - 23:00",
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5,
                                    ),
                                ],
                            ),
                        ],
                    )
                ],
            ),
            footer=BoxComponent(
                layout='vertical',
                spacing='sm',
                contents=[
                    # callAction, separator, websiteAction
                    SpacerComponent(size='sm'),
                    # callAction
                    ButtonComponent(
                        style='link',
                        height='sm',
                        action=URIAction(label='CALL', uri='tel:000000'),
                    ),
                    # separator
                    SeparatorComponent(),
                    # websiteAction
                    ButtonComponent(
                        style='link',
                        height='sm',
                        action=URIAction(label='WEBSITE', uri="https://example.com")
                    )
                ]
            ),
        )
        message = FlexSendMessage(alt_text="hello", contents=bubble)
        line_bot_api.reply_message(event.reply_token,message)
    else:
        message = TextSendMessage(text=event.message.text)
        line_bot_api.reply_message(event.reply_token, message)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
