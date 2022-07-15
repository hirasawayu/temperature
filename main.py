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

app = Flask(__name__)

# LINE API�֌W�̐ݒ�l�擾
YOUR_CHANNEL_ACCESS_TOKEN = os.environ['YOUR_CHANNEL_ACCESS_TOKEN']
YOUR_CHANNEL_SECRET = os.environ['YOUR_CHANNEL_SECRET']

# Beebotte�֌W�̐ݒ�l�擾
YOUR_BEEBOTTE_TOKEN = os.environ['YOUR_BEEBOTTE_TOKEN']

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

# ������N�������b�Z�[�W�̃��X�g
show_msg = [s.encode('utf-8') for s in ['show', '�C���\��']]
change_msg = [s.encode('utf-8') for s in ['change', '�v���ꏊ�ύX']]

# LINE�ɒʒm���b�Z�[�W�𑗂�
def broadcast_line_msg(msg):
    line_bot_api.broadcast(TextSendMessage(text=msg))

# �G�A�R������p��MQTT���p�u���b�V������
def publish_aircon_control_msg(msg):
    publish.single('temperature-show-app', \
                    msg, \
                    hostname='mqtt.beebotte.com', \
                    port=8883, \
                    auth = {'hirasawayu':'token:{}'.format(YOUR_BEEBOTTE_TOKEN)}, \
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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text.encode('utf-8')

    if msg in show_msg:
        publish_aircon_control_msg('show')
    elif msg in change_msg:
        publish_aircon_control_msg('change')
    else:
        broadcast_line_msg('\n'.join(['�C���\���F', \
                                     *['['+s.decode('utf-8')+']' for s in show_msg], \
                                     '\n����ꏊ�ύX�F', \
                                     *['['+s.decode('utf-8')+']' for s in change_msg] , \
                                     ]))

if __name__ == '__main__':
    port = int(os.getenv('PORT'))
    app.run(host='0.0.0.0', port=port)