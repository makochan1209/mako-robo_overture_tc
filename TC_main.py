import tkinter as tk

import time
# import subprocess

import serial
import threading

import serial.tools.list_ports
import twelite

# グリッドの大きさ
GRID_WIDTH = 40
GRID_HEIGHT = 10

ROBOT_NUM = 2    # ロボットの台数（1台から6台に対応、2台と6台のみ動作確認）

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

# 管制・受信
def TCDaemon():
    while True: # このループは1回の受信パケット＋データ解析ごと
        # 1パケット受信
        tweResult = twelite.recvTWE(ser)
        
        # データ解析
        if tweResult.address != "":    # パケットが受信できたとき
            fromID = tweAddr.index(tweResult.address)  # 通信相手（n台目→n-1）
            recvCom[fromID] = tweResult.command
            print(str(fromID + 1) + "台目: ")
            if tweResult.command == 0x00:   # 探索結果報告
                print("探索結果報告")
            elif tweResult.command == 0x01: # 位置到達報告
                print("位置到達報告")
                pos[fromID] = tweResult.data[0]
            elif tweResult.command == 0x02: # 行動報告
                print("行動報告")
                act[fromID] = tweResult.data[0]
                print("行動内容: " + hex(act[fromID]))
            elif tweResult.command == 0x03: # ボール有無報告
                print("ボール有無報告")
                ballCaught[fromID] = True if tweResult.data[0] == 0x01 else False
            elif tweResult.command == 0x20: # 行動指示要求
                print("行動指示要求")
            elif tweResult.command == 0x21: # 許可要求
                print("許可要求")
            elif tweResult.command == 0x30: # 通信成立報告
                print("通信成立報告")
            print("")
    
        time.sleep(0.5) # デバッグモードは実際に読んでいないので待機時間挟む


# ボタン操作からの管制への反映
def compStart():
    print("start")
    twelite.sendTWE(ser, tweAddr[0], 0x71, [0x00]) # 1台目に競技開始を通知

def compEmgStop():
    print("emgStop")

# ウィンドウ制御（上の情報を表示する）
def windowDaemon():
    labelTime.configure(text=time.strftime('%Y/%m/%d %H:%M:%S'))

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
    
    for i in range(ROBOT_NUM):  # 1台ずつ接続
        if not connectStatus[i]:    # 未接続のとき
            print("Connecting: " + str(i + 1))
            timeData = time.localtime()
            twelite.sendTWE(ser, 0x78, 0x70, [i + 1, timeData.tm_year - 2000, timeData.tm_mon, timeData.tm_mday, timeData.tm_hour, timeData.tm_min, timeData.tm_sec])
            c = 0
            while True:
                tweResult = twelite.recvTWE(ser)
                # データ解析をするようにする
                if tweResult.address != "":    # パケットが受信できたとき
                    if tweResult.command == 0x30: # 通信成立報告
                        if tweResult.data[0] == i + 1:
                            print("Connected: " + str(i + 1))
                            print("TWELITE address: " + hex(tweResult.address))
                            print()
                            connectStatus[i] = True
                            tweAddr[i] = tweResult.address
                            break
                        else:
                            print("Failed: " + str(i + 1) + "Received: " + str(tweResult.data[0]))
                            print()
                            break
                time.sleep(0.01)
                c += 1
                if c > 100:
                    print("No Connection: " + str(i + 1))
                    print()
                    break

    buttonStart.grid(row=6,column=0,columnspan=2)
    
    if threadTC.is_alive() == False:    # 通信スレッドが動いていないとき（初回）
        threadTC.start()

def exitTCApp():
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
use_port = twelite.twe_serial_ports_detect()

ser = serial.Serial(use_port)
twelite.twe_uart_setting(ser)

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