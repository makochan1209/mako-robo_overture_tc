import tkinter as tk

import time

import datetime
# import subprocess

import serial
import struct
import threading
import random
import sys
import glob

import serial.tools.list_ports

# 動作モード（シリアル通信を実際に行うか）
SERIAL_MODE = False

# グリッドの大きさ
GRID_WIDTH = 40
GRID_HEIGHT = 10

ROBOT_NUM = 6    # ロボットの台数（1台から6台に対応、2台と6台のみ動作確認）

tweAddr = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06]  # 各機のTWELITEのアドレス（TWELITE交換に対応）

pos = [0xf1, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6] # ロボットの位置
destPos = [0xf1, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6] # ロボットの行き先
act = [0xf1, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6] # ロボットの作業内容
ballCaught = [False, False, False, False, False, False] # ボール保持状況
recvCom = [0xf1, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6] # ロボットの受信通信コマンド
transCom = [0xf1, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6] # ロボットの送信通信コマンド
connectStatus = [False, False, False, False, False, False]  # 接続できているか

# [0xA5, 0x5A, 0x80, "Length", "Data", "CD", 0x04]の形式で受信
# "Data": 0x0*（送信元）, Command, Data
serStrDebug = [[0xA5, 0x5A, 0x80, 0x03, 0x01, 0x02, 0x01, 0x02, 0x04], [0xA5, 0x5A, 0x80, 0x03, 0x01, 0x02, 0x04, 0x07, 0x04], [0xA5, 0x5A, 0x80, 0x03, 0x01, 0x21, 0x01, 0x21, 0x04]]
# ボール探索開始, ボールシュート完了, LiDAR露光許可要求

def serial_ports_detect():
    """ Lists serial port names
 
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')
 
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result
    """
    
    result = []
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if p.vid == 0x0403 and p.pid == 0x6001:
            result.append(p.device)
            print(p.device)
            print(p.serial_number)
    return result

# 送信、toIDは0x78のときは全台
def sendTWE(toID, command, data):
    sendPacket = [0xA5, 0x5A, 0x80, 0x03, tweAddr[toID] if toID != 0x78 else 0x78, command]

    if type(data) is complex:
        sendPacket[3] = 0x02 + len(data)
        sendPacket.extend(data)
        sendPacket.extend(["CD"])

    else:
        sendPacket.extend([data, "CD"])


    cdBuff = 0
    for i in range(0, len(sendPacket)):
        if (i >= 4 and i < len(sendPacket) - 1):
            cdBuff = cdBuff ^ sendPacket[i]
        elif (i == len(sendPacket) - 1):
            sendPacket[i] = cdBuff
        
        # if SERIAL_MODE:    
            # ser.write(sendPacket[i].to_bytes(1, 'big'))
        #     ser.write(struct.pack("<B", sendPacket[i]))
        # else:
            # print(sendPacket[i].to_bytes(1, 'big'))
        #     print(struct.pack("<B", sendPacket[i]))
    if SERIAL_MODE:    
        ser.write(b''.join([struct.pack("<B", val) for val in sendPacket]))
    else:
        print(b''.join([struct.pack("<B", val) for val in sendPacket]))

# 1パケット受信（データは複数バイト可能の仕様）
def recvTWE():
    # 値の初期化
    cdBuff = 0
    serBuffStr = []
    
    # データ受信
    if not SERIAL_MODE:
        serStrDebugNum = random.randint(0, len(serStrDebug) - 1)   # どのデバッグコードを持ってくるか
    
    
    while (not SERIAL_MODE) or ser.in_waiting > 0: # データが来ているか・またはデバッグモードのとき。このループは1バイトごと、パケット受信完了でbreak
        if SERIAL_MODE:
            # buff = int.from_bytes(ser.read(), 'big')   # read関数は1byteずつ読み込む、多分文字が来るまで待つはず
            buff = struct.unpack("<B", ser.read())[0]
        
        else:   # デバッグモード、擬似的に受信
            buff = serStrDebug[serStrDebugNum][len(serBuffStr)] # 今取るべきバイトを取ってくる
            if len(serBuffStr) == 5:    # 送信元データを受信した時
                serBuffStr[4] = tweAddr[random.randint(0, ROBOT_NUM - 1)]    # 送信元をランダムにする
            elif len(serBuffStr) >= 5 and len(serBuffStr) == 4 + serBuffStr[3] + 2 and serBuffStr[4] != 0x01:  # EOT => 2台目以降はCD修正（>=5はその後の条件式を通すため）
                serBuffStr[len(serBuffStr) - 2] = cdBuff
                
        serBuffStr.append(buff)
        if len(serBuffStr) > 4:    # データの範囲
            if len(serBuffStr) <= 4 + serBuffStr[3]:    # データ終了まで
                cdBuff = cdBuff ^ buff   # CD計算
            elif len(serBuffStr) == 4 + serBuffStr[3] + 2:    # EOTまで終了
                print("Packet Received")
                if serBuffStr[len(serBuffStr) - 1] == 0x04: # EOTチェック
                    print("EOT OK")
                    if cdBuff == serBuffStr[len(serBuffStr) - 2]:
                        print("CD OK")
                    else:
                        print("CD NG, Expected: " + hex(cdBuff) + ", Received: " + hex(serBuffStr[len(serBuffStr) - 2]))
                else:
                    print("EOT NG")
                break
    if serBuffStr != [] and len(serBuffStr) < 8:    # パケットが短すぎる場合は破棄
        serBuffStr = []
        print("Packet too short")
    if serBuffStr != [] and serBuffStr[4] == 0xdb:   # 応答メッセージなので省略
        serBuffStr = []
        print("Response Message")
    return serBuffStr

# 管制・受信
def TCDaemon():
    while True: # このループは1回の受信パケット＋データ解析ごと
        # 1パケット受信
        serBuffStr = recvTWE()
        
        # データ解析
        if serBuffStr != []:    # パケットが受信できたとき
            fromID = tweAddr.index(serBuffStr[4])  # 通信相手（n台目→n-1）
            recvCom[fromID] = serBuffStr[5]
            print(str(fromID + 1) + "台目: ")
            if serBuffStr[5] == 0x00:   # 探索結果報告
                print("探索結果報告")
            elif serBuffStr[5] == 0x01: # 位置到達報告
                print("位置到達報告")
                pos[fromID] = serBuffStr[6]
            elif serBuffStr[5] == 0x02: # 行動報告
                print("行動報告")
                act[fromID] = serBuffStr[6]
                print("行動内容: " + hex(act[fromID]))
            elif serBuffStr[5] == 0x03: # ボール有無報告
                print("ボール有無報告")
                ballCaught[fromID] = True if serBuffStr[6] == 0x01 else False
            elif serBuffStr[5] == 0x20: # 行動指示要求
                print("行動指示要求")
            elif serBuffStr[5] == 0x21: # 許可要求
                print("許可要求")
            elif serBuffStr[5] == 0x30: # 通信成立報告
                print("通信成立報告")
            print("")
            
        if SERIAL_MODE:
            time.sleep(0.001)
        else:
            time.sleep(0.5) # デバッグモードは実際に読んでいないので待機時間挟む


# ボタン操作からの管制への反映
def compStart():
    print("start")

def compEmgStop():
    print("emgStop")

# ウィンドウ制御（上の情報を表示する）
def windowDaemon():
    labelTime.configure(text=datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))

    configureTextBuf = ""
    for i in range(ROBOT_NUM):
        actTextBuf = ""
        if (act[i] == 0x00):
            actTextBuf = "待機中"
        elif (act[i] == 0x01):
            actTextBuf = "走行中"
        elif (act[i] == 0x02):
            actTextBuf = "ボール探索中"
        elif (act[i] == 0x03):
            actTextBuf = "ボール発見、キャッチ中"
        elif (act[i] == 0x04):
            actTextBuf = "ボールシュート中"
        else:
            actTextBuf = "不明"

        if (recvCom[i] == 0x00):
            recvCommandBuf = "探索結果報告："
        elif (recvCom[i] == 0x01):
            recvCommandBuf = "位置到達報告："
        elif (recvCom[i] == 0x02):
            recvCommandBuf = "ボールシュート報告"
        elif (recvCom[i] == 0x20):
            recvCommandBuf = "行動指示要求"
        elif (recvCom[i] == 0x21):
            recvCommandBuf = "許可要求"
        elif (recvCom[i] == 0x30):
            recvCommandBuf = "通信成立報告"
        else:
            recvCommandBuf = "なし"

        if (transCom[i] == 0x50):
            transCommandBuf = "移動許可：" + destPos[i]
        elif (transCom[i] == 0x51):
            transCommandBuf = "行動許可："
        else:
            transCommandBuf = "なし"

        if connectStatus[i]:
            configureTextBuf = str(i + 1) + "号機\n\n" + "接続状態: " + "接続済（TWELITEアドレス: " + hex(tweAddr[i]) + "）\n\n場所: " + hex(pos[i]) + "\n状態: " + actTextBuf + "\n最終通信内容（受信）: " + recvCommandBuf + "\n最終通信内容（送信）: " + transCommandBuf
        else:
            configureTextBuf = str(i + 1) + "号機\n\n" + "接続状態: " + "未接続"

        if (i == 0):
            labelR1.configure(text=configureTextBuf)
        elif (i == 1):
            labelR2.configure(text=configureTextBuf)
        elif (i == 2):
            labelR3.configure(text=configureTextBuf)
        elif (i == 3):
            labelR4.configure(text=configureTextBuf)
        elif (i == 4):
            labelR5.configure(text=configureTextBuf)
        elif (i == 5):
            labelR6.configure(text=configureTextBuf)

    mainWindow.after(50, windowDaemon)

# ロボット本体との接続
def connect():
    buttonConnect.grid_forget()
    
    if SERIAL_MODE: # シリアル通信のとき
        for i in range(ROBOT_NUM):  # 1台ずつ接続
            if not connectStatus[i]:    # 未接続のとき
                print("Connecting: " + str(i + 1))
                sendTWE(0x78, 0x70, i + 1)
                c = 0
                while True:
                    serBuffStr = recvTWE()
                    # データ解析をするようにする
                    if serBuffStr != []:    # パケットが受信できたとき
                        if serBuffStr[5] == 0x30: # 通信成立報告
                            if serBuffStr[6] == i + 1:
                                print("Connected: " + str(i + 1))
                                print("TWELITE address: " + hex(serBuffStr[4]))
                                print()
                                connectStatus[i] = True
                                tweAddr[i] = serBuffStr[4]
                                break
                            else:
                                print("Failed: " + str(i + 1) + "Received: " + str(serBuffStr[6]))
                                print()
                                break
                    time.sleep(0.01)
                    c += 1
                    if c > 100:
                        print("No Connection: " + str(i + 1))
                        print()
                        break
    
    else:
        for i in range(ROBOT_NUM):
            connectStatus[i] = True
            sendTWE(0x78, 0x70, i + 1)
            
    buttonStart.grid(row=6,column=0,columnspan=2)
    
    if threadTC.is_alive() == False:    # 通信スレッドが動いていないとき（初回）
        threadTC.start()

def exitTCApp():
    if SERIAL_MODE:
        ser.close()
    mainWindow.destroy()

def keyPress(event):
    # Enterのとき
    if event.keycode == 13:
        compStart()
    # Numkey 1のとき
    elif event.keycode == 97:
        connect()
    # Numkey 2のとき
    elif event.keycode == 98:
        compEmgStop()
    # Numkey 9のとき
    elif event.keycode == 105:
        exitTCApp()

# 以下メインルーチン

# 初期化

# シリアル通信（TWE-Lite）
if SERIAL_MODE:
    """
    port_result = serial_ports_detect()
    if port_result == []:   # ポートが見つからないとき
        print("No port found")
        exit()
    elif port_result.count('/dev/ttyAMA0') > 0:   # Linuxのとき
        use_port = '/dev/ttyAMA0'
    else:   # Windowsのとき
        if len(port_result) == 1:
            use_port = port_result[0]
        else:
            for port in port_result:
                print(port)
                print("Enter the port number you want to use")
                use_port = input()
    """
    port_result = serial_ports_detect()
    if port_result == []:   # ポートが見つからないとき
        print("No port found")
        exit()
    else:
        if len(port_result) == 1:
            use_port = port_result[0]
        else:
            for port in port_result:
                print(port)
                print("Enter the port number you want to use")
                use_port = input()
                
    print("Port " + use_port + " is used")

    ser = serial.Serial(use_port)
    ser.baudrate = 115200
    ser.parity = serial.PARITY_NONE
    ser.bytesize = serial.EIGHTBITS
    ser.stopbits = serial.STOPBITS_ONE
    ser.timeout = None

# ウィンドウの定義
mainWindow = tk.Tk()
mainWindow.title ('Main Window')
mainWindow.geometry('800x800')

# グリッドの定義
mainFrame = tk.Frame(mainWindow)
mainFrame.grid(column=0, row=0)

# タイトル
labelTitle = tk.Label(mainWindow, text='Ascella by Team mako-robo\n管制ウィンドウ')
labelTitle.grid(row=0,column=0,columnspan=2)
labelTime = tk.Label(mainWindow, text='')
labelTime.grid(row=1,column=0,columnspan=2)

labelR1 = tk.Label(mainWindow, text='1号機', anchor=tk.N, width=GRID_WIDTH, height=GRID_HEIGHT)
labelR1.grid(row=2,column=0)
if ROBOT_NUM >= 2:
    labelR2 = tk.Label(mainWindow, text='2号機', anchor=tk.N, width=GRID_WIDTH, height=GRID_HEIGHT)
    labelR2.grid(row=2,column=1)
if ROBOT_NUM >= 3:
    labelR3 = tk.Label(mainWindow, text='3号機', anchor=tk.N, width=GRID_WIDTH, height=GRID_HEIGHT)
    labelR3.grid(row=3,column=0)
if ROBOT_NUM >= 4:
    labelR4 = tk.Label(mainWindow, text='4号機', anchor=tk.N, width=GRID_WIDTH, height=GRID_HEIGHT)
    labelR4.grid(row=3,column=1)
if ROBOT_NUM >= 5:
    labelR5 = tk.Label(mainWindow, text='5号機', anchor=tk.N, width=GRID_WIDTH, height=GRID_HEIGHT)
    labelR5.grid(row=4,column=0)
if ROBOT_NUM >= 6:
    labelR6 = tk.Label(mainWindow, text='6号機', anchor=tk.N, width=GRID_WIDTH, height=GRID_HEIGHT)
    labelR6.grid(row=4,column=1)

buttonConnect = tk.Button(mainWindow, text = "通信接続 (Num 1)", command = connect)
buttonConnect.grid(row=5,column=0,columnspan=2)

buttonStart = tk.Button(mainWindow, text = "競技開始 (Enter)", command = compStart)
buttonEmgStop = tk.Button(mainWindow, text = "全ロボット緊急停止 (Num 2)", command = compEmgStop)

buttonExit = tk.Button(mainWindow, text = "プログラム終了 (Num 9)", command = exitTCApp)
buttonExit.grid(row=10,column=0,columnspan=2)

mainWindow.bind("<KeyPress>", keyPress)

threadWindow = threading.Thread(target=windowDaemon, daemon=True)
threadTC = threading.Thread(target=TCDaemon, daemon=True)
threadWindow.start()
i = 0
mainWindow.mainloop()