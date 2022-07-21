import subprocess
import paho.mqtt.client as mqtt     # MQTTのライブラリをインポート
import datetime
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

# LINEでメッセージを送信
def send_line_msg(msg):
    line_bot_api = LineBotApi({KlbAfQfn2l/O+eFOGSvY0cOGOp54iHb/LyiXJi5K48yvnF+7qbx7TM1ny/FGFONZAc5p2RSbOL8rFKD9bUPznCcWyyaCKYM8q62EhkyR2zqhWbNgNCAQjpfMo4PbnvahQoalQpIwhaNPTASf8Pj5ugdB04t89/1O/w1cDnyilFU=})
    line_bot_api.broadcast(TextSendMessage(text=msg))

# ブローカーに接続できたときの処理
def on_connect(client, userdata, flag, rc):
    print('[mqtt_aircon_control.py] Connected with result code ' + str(rc))  # 接続できた旨表示
    client.subscribe('my_home/aircon_control')  # subするトピックを設定 

# ブローカーが切断したときの処理
def on_disconnect(client, userdata, flag, rc):
    if  rc != 0:
        print('[mqtt_aircon_control.py] Unexpected disconnection.')

# メッセージが届いたときの処理
def on_message(client, userdata, msg):
    # エアコンの信号データのパスを指定
    stop_log_path = '/home/pi/ws/send_data/stop.log'
    heater_log_path = '/home/pi/ws/send_data/heater.log'
    cooler_log_path = '/home/pi/ws/send_data/cooler.log'
    # プログラムの実行ファイルのパスを指定
    exec_send_command = '/home/pi/ws/send'
    exec_switching_verify_command = '/home/pi/ws/switching_verify'

    # メッセージ受け取り
    get_msg = msg.payload.decode('utf-8')

    # 現在日時を取得し，送信するデータファイルを決定する
    dt_now = datetime.datetime.now()
    print('[mqtt_aircon_control.py] Get aircon_control topic(msg:{}) [{}]'.format(get_msg, dt_now.strftime('%Y/%m/%d %H:%M:%S')))
    if 11 <= int(dt_now.strftime('%m')) or int(dt_now.strftime('%m')) <= 4:
        send_data_file = heater_log_path
    else:
        send_data_file = cooler_log_path

    # 信号送信処理
    if get_msg == 'show':
        send_line_msg('温度：')
        for i in range(3):
            subprocess.run(['sudo', exec_send_command, send_data_file])
            ret = subprocess.run([exec_switching_verify_command , '10'])
            try:
                if ret.returncode == 0:
                    print('[mqtt_aircon_control.py] Switching successed.')
                    send_line_msg('気温：')
                    break
            except:
                print('[mqtt_aircon_control.py] Switching failed.')
                continue
    elif get_msg == 'off':
        send_line_msg('エアコンの電源を消すよ！')
        subprocess.run(['sudo', exec_send_command, stop_log_path])

# MQTTの接続設定
client = mqtt.Client()                 # クラスのインスタンス(実体)の作成
client.on_connect = on_connect         # 接続時のコールバック関数を登録
client.on_disconnect = on_disconnect   # 切断時のコールバックを登録
client.on_message = on_message         # メッセージ到着時のコールバック

client.username_pw_set("token:{Beebotteのチャネルトークン(token_*の形)}") 
client.tls_set("/home/pi/ws/mqtt.beebotte.com.pem")
client.connect("mqtt.beebotte.com", 8883, 60)

send_line_msg('システムを起動するよ！')

client.loop_forever()                  # 永久ループして待ち続ける
