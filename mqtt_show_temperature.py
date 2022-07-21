#! /usr/bin/env python


import subprocess
import paho.mqtt.client as mqtt     # MQTTのライブラリをインポート
import datetime
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
import read_temp


#消す
#print('Rasp')

# LINEでメッセージを送信

def send_line_msg(msg):

    line_bot_api = LineBotApi('KlbAfQfn2l/O+eFOGSvY0cOGOp54iHb/LyiXJi5K48yvnF+7qbx7TM1ny/FGFONZAc5p2RSbOL8rFKD9bUPznCcWyyaCKYM8q62EhkyR2zqhWbNgNCAQjpfMo4PbnvahQoalQpIwhaNPTASf8Pj5ugdB04t89/1O/w1cDnyilFU=')
    line_bot_api.broadcast(TextSendMessage(text=msg))

# ブローカーに接続できたときの処理
def on_connect(client, userdata, flag, rc):
    print('[mqtt_show_temperature.py] Connected with result code ' + str(rc))  # 接続できた旨表示
    client.subscribe('hirasawayu/show_temperature')  # subするトピックを設定 

# ブローカーが切断したときの処理
#def on_disconnect(client, userdata, flag, rc):
    #if  rc != 0:
        #print('[mqtt_show_temperature.py] Unexpected disconnection.')

# メッセージが届いたときの処理
def on_message(client, userdata, msg):

   
    # プログラムの実行ファイルのパスを指定
#    exec_showing_temperature_command = '/home/hirasawayu/temperature/dist/read_temp'


    # メッセージ受け取り
    get_msg = msg.payload.decode('utf-8')

    # 現在日時を取得し，送信するデータファイルを決定する
    dt_now = datetime.datetime.now()
    #print('[mqtt_show_temperature.py] Get show_temperature topic(msg:{}) [{}]'.format(get_msg, dt_now.strftime('%Y/%m/%d %H:%M:%S')))

    # 信号送信処理
    if get_msg == 'show':
        #消す
 #       print('Rasp')

        send_line_msg('気温表示')
        send_line_msg(read_temp.read_temp())
  #      for i in range(3):
  #          subprocess.run(['sudo', exec_showing_temperature_command])
  #          ret = subprocess.run([exec_showing_temperature_command , '10'])
  #          try:
  #              if ret.returncode == 0:
  #                  print('[mqtt_show_temperature.py] Switching successed.')
  #                  send_line_msg('気温：', temp_c)
  #                  break
  #          except:
  #              print('[mqtt_show_temperature.py] Switching failed.')
  #              continue
  #  elif get_msg == '':
  #      send_line_msg('エアコンの電源を消すよ！')
  #      subprocess.run(['sudo', exec_send_command, stop_log_path])

    elif get_msg == 'change':

        send_line_msg('計測場所変更')

        

# MQTTの接続設定
client = mqtt.Client()                 # クラスのインスタンス(実体)の作成
client.on_connect = on_connect         # 接続時のコールバック関数を登録
#client.on_disconnect = on_disconnect   # 切断時のコールバックを登録
client.on_message = on_message         # メッセージ到着時のコールバック

client.username_pw_set("token:token_zFbA362yQyPJoCGc") 
client.tls_set("/home/hirasawayu/temperature/mqtt.beebotte.com.pem")
client.connect("mqtt.beebotte.com", 8883, 60)

send_line_msg('システムを起動するよ！')

client.loop_forever()                  # 永久ループして待ち続ける
