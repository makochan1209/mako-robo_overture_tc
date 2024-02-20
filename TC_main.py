import tkinter as tk

import time
# import subprocess

import serial
import threading

import serial.tools.list_ports
import twelite

WINDOW_MODE = False  # ウィンドウモードかどうか

# グリッドの大きさ
GRID_WIDTH = 40
GRID_HEIGHT = 10

ROBOT_NUM = 2    # ロボットの台数（1台から6台に対応、2台と6台のみ動作確認）

tweAddr = []  # 各機のTWELITEのアドレス（TWELITE交換に対応）

pos = [] # ロボットの位置
destPos = [] # ロボットの行き先
act = [] # ロボットの作業内容
request = [] # ロボットの直近要求内容
requestDestPos = [] # ロボットの直近要求内容における目的地
permit = [] # ロボットの直近許可内容
ballStatus = [] # ボール取得個数、ロボットごとの配列で、その中の各値は連想配列（r, g, b）で管理
connectStatus = []  # 接続できているか

actText = ["待機中", "走行中", "ボール探索中（未発見、LiDARなし）", "ボール探索中（未発見、LiDARあり）", "ボール探索中（発見済、LiDARなし）", "ボール探索中（発見済、LiDARあり）", "ボールキャッチ", "ボールシュート"]
requestText = ["", "移動許可要求", "", "ボール探索（未発見）LiDAR照射許可要求", "", "ボール探索（発見済）LiDAR照射許可要求", "ボールキャッチ許可要求", "ボールシュート許可要求"]
permitText = ["", "移動許可", "", "ボール探索（未発見）LiDAR照射許可", "", "ボール探索（発見済）LiDAR照射許可", "ボールキャッチ許可", "ボールシュート許可"]

twe = None
ser = None

pauseTC = False # 管制プログラムの一時停止

def init():
    global ser, twe
    # 初期化
    use_port = twelite.twe_serial_ports_detect()

    ser = serial.Serial(use_port)
    twe = twelite.TWELITE(ser)

    for i in range(ROBOT_NUM):
        tweAddr.append(0x01 + i)   # 初期値
        pos.append(0xff)
        destPos.append(0xff)
        act.append(0xff)
        request.append(0xff)
        requestDestPos.append(0xff)
        permit.append(0xff)
        ballStatus.append({"r": 0, "y": 0, "b": 0})
        connectStatus.append(False)

# [0xA5, 0x5A, 0x80, "Length", "Data", "CD", 0x04]の形式で受信
# "Data": 0x0*（送信元）, Command, Data
# ボール探索開始, ボールシュート完了, LiDAR露光許可要求

# 管制・受信（受信したら指示を返信（送信）する形、常に起動している）
def TCDaemon():
    while True: # このループは1回の受信パケット＋データ解析ごと
        if not pauseTC:
            # 1パケット受信
            tweResult = twe.recvTWE(ser)
            
            # データ解析
            if tweResult.address != "":    # パケットが受信できたとき
                fromID = tweAddr.index(tweResult.address)  # 通信相手（n台目→n-1）
                print(str(fromID + 1) + "台目: ")
                if tweResult.command == 0x00:   # 探索結果報告
                    ballStatus[fromID]["r"] = tweResult.data[0]
                    ballStatus[fromID]["y"] = tweResult.data[1]
                    ballStatus[fromID]["b"] = tweResult.data[2]
                    print("探索結果報告：赤" + str(ballStatus[fromID]["r"]) + "個、黄" + str(ballStatus[fromID]["y"]) + "個、青" + str(ballStatus[fromID]["b"]) + "個")
                elif tweResult.command == 0x02: # 行動報告
                    act[fromID] = tweResult.data[0]
                    print("行動報告")
                    print("行動内容: " + hex(act[fromID])) + " (" + actText[act[fromID]] + ")"
                    if act[fromID] == 0x00:
                        pos[fromID] = tweResult.data[1]
                        print("現在地: " + hex(pos[fromID]))
                    elif act[fromID] == 0x01:
                        pos[fromID] = tweResult.data[1]
                        print("現在地: " + hex(pos[fromID]))
                        destPos[fromID] = tweResult.data[2]
                        print("目的地: " + hex(destPos[fromID]))

                elif tweResult.command == 0x20: # 許可要求。ここで管制や許可を行う、管制処理はすべてここ。
                    request[fromID] = tweResult.data[0]
                    print("許可要求")
                    print("要求内容: " + hex(request[fromID]) + " (" + requestText[request[fromID]] + ")")

                    if request[fromID] == 0x01: # 移動許可要求
                        requestDestPos[fromID] = tweResult.data[1]
                        print("移動許可要求の目的地: " + hex(requestDestPos[fromID]))

                        permit[fromID] = 0x01

                        # ここで許可を出すかどうかを判断する（どうやって待機するか…）
                        destPos[fromID] = requestDestPos[fromID]    # ゴールゾーンでどのゴールに行くかが異なる場合はここで仕分ける必要あり
                        requestDestPos[fromID] = 0xff
                        print("移動許可の目的地: " + hex(destPos[fromID]))
                        twe.sendTWE(tweAddr[fromID], 0x50, [permit[fromID], destPos[fromID]]) # 許可を返信
                    elif request[fromID] == 0x03 or request[fromID] == 0x05: # ボール探索LiDAR照射許可要求
                        permit[fromID] = 0x05
                        # ここで許可を出すかどうかを判断する（どうやって待機するか…）
                        twe.sendTWE(tweAddr[fromID], 0x50, [permit[fromID]]) # 許可を返信
                    elif request[fromID] == 0x06:   # ボールキャッチ許可要求
                        permit[fromID] = 0x06
                        # ここで許可を出すかどうかを判断する（どうやって待機するか…）
                        twe.sendTWE(tweAddr[fromID], 0x50, [permit[fromID]])
                    elif request[fromID] == 0x07:   # ボールシュート許可要求
                        permit[fromID] = 0x07
                        # ここで許可を出すかどうかを判断する（どうやって待機するか…）
                        twe.sendTWE(tweAddr[fromID], 0x50, [permit[fromID]])
                    print("許可内容: " + hex(permit[fromID]) + " (" + permitText[permit[fromID]] + ")")
                print("")
        
        time.sleep(0.2)


# ボタン操作からの管制への反映
def compStart():
    print("start")
    twe.sendTWE(tweAddr[0], 0x71, [0x00]) # 1台目に競技開始を通知

def compEmgStop():
    print("emgStop")
    twe.sendTWE(tweAddr[0], 0x71, [0xff])

# 画面制御（上の情報を表示する）
def windowDaemon():
    if WINDOW_MODE:
        labelTime.configure(text=time.strftime('%Y/%m/%d %H:%M:%S'))

    configureTextBuf = ""
    for i in range(ROBOT_NUM):
        if connectStatus[i]:
            configureTextBuf = str(i + 1) + "号機\n\n" + "接続状態: " + "接続済（TWELITEアドレス: " + hex(tweAddr[i]) + "）\n\n現在地: " + hex(pos[i]) + "\n状態: " + actTextBuf + "\n最終通信内容（受信）: " + recvCommandBuf + "\n最終通信内容（送信）: " + transCommandBuf
        else:
            configureTextBuf = str(i + 1) + "号機\n\n" + "接続状態: " + "未接続"

        if WINDOW_MODE:
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
        #else:
        #    print(configureTextBuf)

    if WINDOW_MODE:
        mainWindow.after(50, windowDaemon)
    else:
        time.sleep(1)
        windowDaemon()

# ロボット本体との接続
def connect():
    # buttonConnect.grid_forget()
    global pauseTC
    pauseTC = True  # TCの一時停止
    
    for i in range(ROBOT_NUM):  # 1台ずつ接続
        if not connectStatus[i]:    # 未接続のとき
            print("Connecting: " + str(i + 1))
            timeData = time.localtime()
            twe.sendTWE(0x78, 0x70, [i + 1, timeData.tm_year - 2000, timeData.tm_mon, timeData.tm_mday, timeData.tm_hour, timeData.tm_min, timeData.tm_sec])
            c = 0
            while True:
                tweResult = twe.recvTWE()
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

    # buttonStart.grid(row=6,column=0,columnspan=2)
    pauseTC = False  # TCの再開

def exitTCApp():
    global pauseTC
    pauseTC = True
    ser.close()
    if WINDOW_MODE:
        mainWindow.destroy()
    exit()

# ウィンドウモードでのキー待機
def windowKeyPress(event):
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

def terminalKeyPressWait():
    while True:
        print("1: 通信接続、2: 全ロボット緊急停止、3: 競技開始、9: プログラム終了")
        a = input("機体への送信信号・プログラム終了: ")
        if a == "1":
            connect()
        elif a == "2":
            compEmgStop()
        elif a == "3":
            compStart()
        elif a == "9":
            exitTCApp()
        else:
            print("無効な入力です")
        time.sleep(0.5)

# 以下メインルーチン
init()

mode = input("ウィンドウモードは1を入力してEnter: ")

if mode == 1:
    WINDOW_MODE = True

# 管制プログラムの起動（受信した信号に対して送信するパッシブなものなので常に動かす）
threadTC = threading.Thread(target=TCDaemon, daemon=True)
threadTC.start()
i = 0

# ウィンドウ表示モード
if WINDOW_MODE:
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

    # ウィンドウの構成
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
    buttonConnect.grid(row=6,column=0,columnspan=2)
    buttonEmgStop = tk.Button(mainWindow, text = "全ロボット緊急停止 (Num 2)", command = compEmgStop)
    buttonConnect.grid(row=7,column=0,columnspan=2)

    buttonExit = tk.Button(mainWindow, text = "プログラム終了 (Num 9)", command = exitTCApp)
    buttonExit.grid(row=10,column=0,columnspan=2)

    # キー待機部分
    mainWindow.bind("<KeyPress>", windowKeyPress)

    # 表示更新スレッド開始
    threadWindow = threading.Thread(target=windowDaemon, daemon=True)
    threadWindow.start()
    mainWindow.mainloop()

# ターミナルモード
else:
    print("管制システムは既に起動しています")
    # キー待機部分
    terminalKeyPressWait()