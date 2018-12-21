from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

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

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TemplateSendMessage(
    alt_text='ImageCarousel template',
    template=ImageCarouselTemplate(
        columns=[
            ImageCarouselColumn(
                image_url='https://example.com/item1.jpg',
                action=PostbackTemplateAction(
                    label='飯',
                    text='飯',
                    data='action=buy&itemid=1'
                )
            ),
            ImageCarouselColumn(
                image_url='https://example.com/item1.jpg',
                action=PostbackTemplateAction(
                    label='麵',
                    text='麵',
                    data='action=buy&itemid=2'
                )
            ),
            ImageCarouselColumn(
                image_url='https://example.com/item1.jpg',
                action=PostbackTemplateAction(
                    label='鍋',
                    text='鍋',
                    data='action=buy&itemid=1'
                )
            ),
            ImageCarouselColumn(
                image_url='https://example.com/item1.jpg',
                action=PostbackTemplateAction(
                    label='飲料',
                    text='飲料',
                    data='action=buy&itemid=1'
                )
            ),
            ImageCarouselColumn(
                image_url='https://example.com/item1.jpg',
                action=PostbackTemplateAction(
                    label='其他',
                    text='其他',
                    data='action=buy&itemid=1'
                )
            )
        ]
    )
)
    line_bot_api.reply_message(event.reply_token, message)


import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
