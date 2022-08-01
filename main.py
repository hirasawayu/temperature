#! /usr/bin/env python

from email.message import Message
from flask import Flask, request, abort
import paho.mqtt.publish as publish
import os
import json
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import logging

LOGFILE_NAME = "DEBUG.log"

app = Flask(__name__)

app.logger.setLevel(logging.DEBUG)
log_handler = logging.FileHandler(LOGFILE_NAME)
log_handler.setLevel(logging.DEBUG)
app.logger.addHandler(log_handler)

# LINE API関係の設定値取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ['YOUR_CHANNEL_ACCESS_TOKEN']
YOUR_CHANNEL_SECRET = os.environ['YOUR_CHANNEL_SECRET']

# Beebotte関係の設定値取得
YOUR_BEEBOTTE_TOKEN = os.environ['YOUR_BEEBOTTE_TOKEN']

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

# 動作を起こすメッセージのリスト
show_msg = [s.encode('utf-8') for s in ['show', '気温表示']]
change_msg = [s.encode('utf-8') for s in ['change', '計測場所変更']]


# LINEに通知メッセージを送る
def broadcast_line_msg(msg):
    app.logger.debug('line-send')
    line_bot_api.broadcast(TextSendMessage(text=msg))

# エアコン制御用のMQTTをパブリッシュする
def publish_aircon_control_msg(msg):
    publish.single('hirasawayu/show_temperature', \
                    msg, \
                    hostname='mqtt.beebotte.com', \
                    port=8883, \
                    auth = {'username':'token:{}'.format(YOUR_BEEBOTTE_TOKEN)}, \
                    tls={'ca_certs':'mqtt.beebotte.com.pem'})


@app.route('/callback', methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info('Request body: ' + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


#def change_place():
#    broadcast_line_msg('場所を選択してください\n1: 平澤　2:本郷')
#    def switch_place(event):
#        place = event.message.text.enocde

#    if place == 1:
#       YOUR_BEEBOTTE_TOKEN = os.environ['YOUR_BEEBOTTE_TOKEN']
#
#    elif place == 2:
#        YOUR_BEEBOTTE_TOKEN = 'token_CdVWquhY2oiFcwHc'



@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text.encode('utf-8')

    if msg in show_msg:
        publish_aircon_control_msg('show')

    #elif msg in change_msg:
    #   change_place()
    else:
        broadcast_line_msg('\n'.join(['気温表示：', \
                                     *['['+s.decode('utf-8')+']' for s in show_msg], \
                                     '\n測定場所変更：', \
                                     *['['+s.decode('utf-8')+']' for s in change_msg] , \
                                     ]))

if __name__ == '__main__':
    port = int(os.getenv('PORT'))
    app.run(host='0.0.0.0', port=port)