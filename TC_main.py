import time
# import subprocess

import serial
import threading

import serial.tools.list_ports
import json, datetime
from bottle import route, run, template, static_file
import twelite

WINDOW_MODE = False  # ウィンドウモードかどうか

# グリッドの大きさ
GRID_WIDTH = 40
GRID_HEIGHT = 10

ROBOT_NUM = 2    # ロボットの台数（1台から6台に対応、2台と6台のみ動作確認）

tweAddr = []  # 各機のTWELITEのアドレス（TWELITE交換に対応）、0xffは未接続

tcStatus = 0    # 0: 待機中、1: 競技中
pos = [] # ロボットの位置
destPos = [] # ロボットの行き先
finalDestPos = [] # ロボットの最終目的地
act = [] # ロボットの現在の行動内容
request = [] # ロボットの許可要求内容（許可されていないもののみ）
requestDestPos = [] # ロボットの許可要求内容における目的地（許可されていないもののみ）
requestQueue = [] # ロボットの許可要求の順序キュー
permit = [] # ロボットの直近許可内容
ballStatus = [] # ボール取得個数、ロボットごとの配列で、その中の各値は連想配列（r, g, b）で管理
searchNum = []  # 探索回数
terminalOutputBuff = [] # 出力テキスト
totalBalls = {"r": 0, "y": 0, "b": 0, "t": 0}  # 各色の得点済のボールの総数
testData = []   # 測定テストデータ（未実装）

actText = ["待機中", "走行中", "ボール探索中（未発見、LiDARなし）", "ボール探索中（未発見、LiDARあり）", "ボール探索中（発見済、LiDARなし）", "ボール探索中（発見済、LiDARあり）", "ボールキャッチ", "ボールシュート"]
requestText = ["", "移動許可要求", "", "ボール探索（未発見）LiDAR照射許可要求", "", "ボール探索（発見済）LiDAR照射許可要求", "ボールキャッチ許可要求", "ボールシュート許可要求"]
permitText = ["", "移動許可", "", "ボール探索（未発見）LiDAR照射許可", "", "ボール探索（発見済）LiDAR照射許可", "ボールキャッチ許可", "ボールシュート許可"]

nearerRoutePos = [0x08, 0x09]   # 手前回りルートの場所コード

twe = None
ser = None
use_port = None

threadTC = None
pauseTC = False # 管制プログラムの一時停止

labelR = []

def init():
    global use_port, ser, twe, tweAddr, pos, destPos, act, request, requestDestPos, permit, ballStatus, threadTC, searchNum
    
    #if use_port is not None:
        #ser.close()
        #use_port = None
    
    # 初期化
    tweAddr.clear()
    pos.clear()
    destPos.clear()
    act.clear()
    request.clear()
    requestDestPos.clear()
    permit.clear()
    ballStatus.clear()
    searchNum.clear()
    
    for i in range(ROBOT_NUM):
        tweAddr.append(0xff)
        pos.append(0xff)
        destPos.append(0xff)
        finalDestPos.append(0xff)
        act.append(0xff)
        request.append(0xff)
        requestDestPos.append(0xff)
        permit.append(0xff)
        ballStatus.append({"r": 0, "y": 0, "b": 0})
        searchNum.append(0)

def terminalPrint(a):
    global terminalOutputBuff
    print(a)
    terminalOutputBuff.append(a)
    if len(terminalOutputBuff) > 20:
        terminalOutputBuff.pop(0)

def connectSerial():
    global ser, use_port, twe, threadTC
    use_port = twelite.twe_serial_ports_detect()
    if use_port is not None:
        ser = serial.Serial(use_port)
        twe = twelite.TWELITE(ser)
        
        # 管制プログラムの起動（受信した信号に対して送信するパッシブなものなので常に動かす）
        threadTC = threading.Thread(target=TCDaemon, daemon=True)
        threadTC.start()
        terminalPrint("Serial connected: " + use_port)
        return True
    
    else:
        terminalPrint("Serial not connected")
        return False

# [0xA5, 0x5A, 0x80, "Length", "Data", "CD", 0x04]の形式で受信
# "Data": 0x0*（送信元）, Command, Data
# ボール探索開始, ボールシュート完了, LiDAR露光許可要求

# 管制・受信（受信したら指示を返信（送信）する形、常に起動している）
# 経路上の場所コードのリスト生成（通る順にリストを作る）
def routePosGen(startPos, goalPos):
    routePosList = []
    if goalPos == 0xff: # 目的地がないとき
        routePosList.append(startPos)
    elif startPos in nearerRoutePos or goalPos in nearerRoutePos: # 手前回りルートの場所を通る場合
        posNotNearer = goalPos if goalPos not in nearerRoutePos else startPos
        posNearer = goalPos if goalPos in nearerRoutePos else startPos
        
        if posNearer == 0x09:
            routePosList.append(0x09)
        routePosList.append(0x08)   # 0x08は確定で通る
        
        if posNotNearer != 0x00:    # スタート地点以外
            for j in range(0x01, posNotNearer + 1): # 0x01からゴール側の範囲
                routePosList.append(j)
        else:   # スタート地点の場合：0x00, 0x01の範囲を通る
            routePosList.append(0x01)
            routePosList.append(0x00)
        
        if goalPos == posNearer: # 逆順にする
            routePosList.reverse()

    else:   # 手前回りルート専用の場所を通らない場合
        if startPos < goalPos:
            routePosList = list(range(startPos, goalPos + 1))
        else:
            routePosList = list(range(goalPos, startPos - 1, -1))
    return routePosList

# 各機の占有位置の判断。現在地と目的地の間に位置する領域を占有と判断する。除外する機体番号（自機）を引数にとる。返り値はタプル。
def occupiedJudge(exception = []):
    occupiedPosList = []
    if not isinstance(exception, list):
        exception = [exception]
    
    for i in range(ROBOT_NUM):
        if i not in exception:
            occupiedPosList += routePosGen(pos[i], destPos[i])
    occupiedPosTuple = set(occupiedPosList)
    return occupiedPosTuple

# 目的地に最も近い到達可能な場所の値を返す
def reachablePos(fromID, startPos, goalPos):
    occupiedPosList = []
    occupiedPosList += occupiedJudge(fromID)
    reachablePos = []
    reachablePos += routePosGen(startPos, goalPos)
    for i in range(len(reachablePos)):
        if reachablePos[i] in occupiedPosList:
            reachablePos = reachablePos[:i]
            break
    return reachablePos[-1] if (reachablePos != [] and reachablePos != startPos) else 0xff

# 許可要求への判断。許可できる場合は許可の出力をする一方で、許可できない場合は何もしない。
def permitJudge():
    for i in range(len(requestQueue)):
        permitted = False   # 許可を出す場合はこれをTrueにする、ひとつ許可が出たらこの関数は終了して次のループの呼び出しでまたこの関数が実行される。
        fromID = requestQueue[i]
        if request[fromID] == 0x01: # 移動許可要求
            # 許可判断
            # ゴールゾーンでどのゴールに行くか判断する必要あり、ゴール内での移動でデッドロックにならないように、などなど
            # 基本的には奥からボールを入れていくが、相手がボールをシュートしに来ている場合は手前から行う。
            # ゴールゾーン関連
            # 1周目はまず一番遠いゴール、次に一番近いゴールを見る。
            # 2周目は本当は移動中にゴールゾーンが解放される可能性も考慮したほうがいいか？
            requestDestPosList = []
            if fromID == 0: # 1号機（奥回りルート）
                if requestDestPos[i] == 0x51:   # ボールをどこかのゴールに捨てたい（ゴールゾーンに向かうのも含む）場合
                    if pos[i] <= 0x05 and pos[i] >= 0x01:  # ゴールゾーン内にいる場合：一番近いゴールに捨てに行く
                        if pos[i] == 0x01:  # 赤色ゴールにいる場合
                            if ballStatus[i]["y"] != 0:
                                requestDestPosList.append(0x03)
                            if ballStatus[i]["b"] != 0:
                                requestDestPosList.append(0x05)

                        elif pos[i] == 0x03:    # 黄色ゴールにいる場合
                            if ballStatus[i]["r"] != 0:
                                requestDestPosList.append(0x01)
                            if ballStatus[i]["b"] != 0:
                                requestDestPosList.append(0x05)
                                
                        elif pos[i] == 0x05:    # 青色ゴールにいる場合
                            if ballStatus[i]["y"] != 0: # 黄色ゴールに向かう
                                requestDestPosList.append(0x03)
                            if ballStatus[i]["r"] != 0:   # 赤色ゴールに向かう
                                requestDestPosList.append(0x01)
                        
                    else:  # ゴールゾーンの外にいる場合：一番遠いゴールに向かうが、途中で占有されている場合は一番近いゴールまで向かう
                        if ballStatus[i]["r"] != 0: # 赤色ボールを持っている場合
                            requestDestPosList.append(0x01)
                        elif ballStatus[i]["y"] != 0:   # 赤色ボールを持っていないが黄色ボールを持っている場合
                            requestDestPosList.append(0x03)
                        if ballStatus[i]["b"] != 0: # 青色ボールを持っている場合（青色ボールのみor他の色のボールを持っているが最も近い青色ゴールも候補）
                            requestDestPosList.append(0x05)
                        elif ballStatus[i]["y"] != 0 and ballStatus[i]["r"] != 0:   # 黄色ボールと赤色ボールを持っている場合：一番近いのが黄色ゴール
                            requestDestPosList.append(0x03)
                
                elif requestDestPos[i] == 0x52: # ボールゾーン
                    requestDestPosList.append(0x07)
                
                else:
                    requestDestPosList.append(requestDestPos[i])

            elif fromID == 1:   # 2号機（手前回りルート）
                if requestDestPos[i] == 0x51:   # ボールをどこかのゴールに捨てたい（ゴールゾーンに向かうのも含む）場合
                    if pos[i] <= 0x05 and pos[i] >= 0x01:  # ゴールゾーン内にいる場合：一番近いゴールに捨てに行く
                        if pos[i] == 0x01:  # 赤色ゴールにいる場合
                            if ballStatus[i]["y"] != 0:
                                requestDestPosList.append(0x03)
                            if ballStatus[i]["b"] != 0:
                                requestDestPosList.append(0x05)

                        elif pos[i] == 0x03:    # 黄色ゴールにいる場合
                            if ballStatus[i]["b"] != 0:
                                requestDestPosList.append(0x05)
                            if ballStatus[i]["r"] != 0:
                                requestDestPosList.append(0x01)
                                
                        elif pos[i] == 0x05:    # 青色ゴールにいる場合
                            if ballStatus[i]["y"] != 0: # 黄色ゴールに向かう
                                requestDestPosList.append(0x03)
                            if ballStatus[i]["r"] != 0:   # 赤色ゴールに向かう
                                requestDestPosList.append(0x01)
                        
                    else:  # ゴールゾーンの外にいる場合：一番遠いゴールに向かうが、途中で占有されている場合は一番近いゴールまで向かう
                        if ballStatus[i]["b"] != 0: # 青色ボールを持っている場合（青色ボールのみor他の色のボールを持っているが最も近い青色ゴールも候補）
                            requestDestPosList.append(0x05)
                        elif ballStatus[i]["y"] != 0:   # 赤色ボールを持っていないが黄色ボールを持っている場合
                            requestDestPosList.append(0x03)
                        if ballStatus[i]["r"] != 0: # 赤色ボールを持っている場合
                            requestDestPosList.append(0x01)
                        elif ballStatus[i]["y"] != 0 and ballStatus[i]["r"] != 0:   # 黄色ボールと赤色ボールを持っている場合：一番近いのが黄色ゴール
                            requestDestPosList.append(0x03)
                
                elif requestDestPos[i] == 0x52: # ボールゾーン
                    requestDestPosList.append(0x09)
                
                else:
                    requestDestPosList.append(requestDestPos[i])
            
            permitDestPos = 0xff    # 許可する目的地のバッファ（destPosにすぐ代入されるため表示等不要）
            reachableDestPosBuff = 0xff # 近くまで行くことができる場合の目的地バッファ、直接目的地に行ける場合はそちらが優先される。
            finalDestPosBuff = 0xff # 最終目的地のバッファ、近くまで行くことができるままで最終目的地にたどり着けない場合に使用
            for j in range(len(requestDestPosList)):
                destPosBuff = reachablePos(fromID, pos[i], requestDestPosList[j])
                if destPosBuff == requestDestPosList[j]:
                    permitDestPos = destPosBuff
                    finalDestPosBuff = destPosBuff
                    permitted = True
                    break
                elif destPosBuff != 0xff and reachableDestPosBuff == 0xff:  # 近くまで行ける場所が見つかって、まだ「近くまで行くことができる場所」が見つかっていない場合
                    reachableDestPosBuff = destPosBuff
                    finalDestPosBuff = requestDestPosList[j]
                    permitted = True
            
            if permitDestPos == 0xff and reachableDestPosBuff != 0xff:
                permitDestPos = reachableDestPosBuff

            if permitted:
                permit[fromID] = 0x01
                destPos[fromID] = permitDestPos
                finalDestPos[fromID] = finalDestPosBuff
                requestDestPos[fromID] = 0xff
                terminalPrint("移動許可、許可目的地: " + hex(destPos[fromID]) + "、最終目的地：" + hex(finalDestPos[fromID]))
                twe.sendTWE(tweAddr[fromID], 0x50, [permit[fromID], destPos[fromID], finalDestPos[fromID]]) # 許可を返信
        elif request[fromID] == 0x02:   # ボール探索許可要求、探索個数
            global searchNum
            ballNum = 0
            searchNum[fromID] += 1
            if searchNum[fromID] == 1:  # 1周目
                if fromID == 0: # 1号機（奥回りルート）
                    ballNum = 4
                elif fromID == 1:   # 2号機（手前回りルート）
                    ballNum = 3 # 手前の3個を取り切る
            elif searchNum[fromID] == 2:    # 2周目
                if fromID == 0: # 1号機（奥回りルート）
                    ballNum = 4
                elif fromID == 1:   # 2号機（手前回りルート）
                    ballNum = 4

            permit[fromID] = 0x02
            twe.sendTWE(tweAddr[fromID], 0x50, [permit[fromID], ballNum]) # 許可を返信

        elif request[fromID] == 0x03 or request[fromID] == 0x05: # ボール探索LiDAR照射許可要求
            # 許可判断
            for j in range(ROBOT_NUM):
                if j != fromID and (act[j] == 0x03 or act[j] == 0x05):
                    permitted = False
                else:
                    permitted = True

            if permitted:
                permit[fromID] = request[fromID]
                twe.sendTWE(tweAddr[fromID], 0x50, [permit[fromID]]) # 許可を返信

        elif request[fromID] == 0x06:   # ボールキャッチ許可要求
            # 許可判断
            for j in range(ROBOT_NUM):
                if j != fromID and act[j] == 0x06:
                    permitted = False
                else:
                    permitted = True

            if permitted:
                permit[fromID] = 0x06
                twe.sendTWE(tweAddr[fromID], 0x50, [permit[fromID]])

        elif request[fromID] == 0x07:   # ボールシュート許可要求（今回は同一領域で走路がかぶることがないため基本許可）
            # 許可判断
            permitted = True
            if permitted:
                permit[fromID] = 0x07
                twe.sendTWE(tweAddr[fromID], 0x50, [permit[fromID]])
        
        if permitted:   # 許可時の共通処理
            terminalPrint("許可内容: " + hex(permit[fromID]) + " (" + permitText[permit[fromID]] + ")")
            requestQueue.pop(i)
            request[fromID] = 0xff
            break

# 通信デーモン
def TCDaemon():
    while True: # このループは1回の受信パケット＋データ解析ごと
        if not pauseTC:
            # 1パケット受信
            tweResult = twe.recvTWE(ser)
            
            # データ解析
            if tweResult.address != "":    # パケットが受信できたとき
                fromID = tweAddr.index(tweResult.address)  # 通信相手（n台目→n-1）
                terminalPrint(str(fromID + 1) + "台目: ")
                if tweResult.command == 0x00:   # 探索結果報告
                    ballStatus[fromID]["r"] = tweResult.data[0]
                    ballStatus[fromID]["y"] = tweResult.data[1]
                    ballStatus[fromID]["b"] = tweResult.data[2]
                    terminalPrint("探索結果報告：赤" + str(ballStatus[fromID]["r"]) + "個、黄" + str(ballStatus[fromID]["y"]) + "個、青" + str(ballStatus[fromID]["b"]) + "個")
                elif tweResult.command == 0x02: # 行動報告
                    act[fromID] = tweResult.data[0]
                    terminalPrint("行動報告")
                    terminalPrint("行動内容: " + hex(act[fromID])) + " (" + actText[act[fromID]] + ")"
                    if act[fromID] == 0x00:
                        pos[fromID] = tweResult.data[1]
                        terminalPrint("現在地: " + hex(pos[fromID]))
                    elif act[fromID] == 0x01:
                        pos[fromID] = tweResult.data[1]
                        terminalPrint("現在地: " + hex(pos[fromID]))
                    elif act[fromID] == 0x07:
                        if tweResult.data[1] == 0x00:
                            totalBalls["r"] += ballStatus[fromID]["r"]
                            ballStatus[fromID]["r"] = 0
                        elif tweResult.data[1] == 0x01:
                            totalBalls["y"] += ballStatus[fromID]["y"]
                            ballStatus[fromID]["y"] = 0
                        elif tweResult.data[1] == 0x02:
                            totalBalls["b"] += ballStatus[fromID]["b"]
                            ballStatus[fromID]["b"] = 0
                        elif tweResult.data[1] == 0x03:
                            totalBalls["t"] += 1

                elif tweResult.command == 0x20: # 許可要求。ここで管制や許可を行う、管制処理はすべてここ。
                    requestQueue.append(fromID)
                    request[fromID] = tweResult.data[0]
                    terminalPrint("許可要求")
                    terminalPrint("要求内容: " + hex(request[fromID]) + " (" + requestText[request[fromID]] + ")")
                    if request[fromID] == 0x01: # 移動許可要求
                        requestDestPos[fromID] = tweResult.data[1]
                        terminalPrint("移動許可要求の目的地: " + hex(requestDestPos[fromID]))
                
                terminalPrint("")
        
        permitJudge()   # 許可要求の判断（過去分含む）
        time.sleep(0.2)


# ボタン操作からの管制への反映
def compStart():
    connectedNum = 0    # 接続済機体数のカウント
    for i in range(ROBOT_NUM):
        if tweAddr[i] != 0xff:
            connectedNum += 1

    global pauseTC, totalBalls, tcStatus
    pauseTC = True
    terminalPrint("start")
    totalBalls = {"r": 0, "y": 0, "b": 0, "t": 0}
    tcStatus = 1
    twe.sendTWE(tweAddr[0], 0x71, [0x00, 0x00 if connectedNum == 2 else 0x01]) # 2台ともに競技開始を通知、2台の場合は協調モード、1台の場合は単独モード
    pauseTC = False

def compEmgStop():
    global pauseTC, tcStatus
    pauseTC = True
    terminalPrint("emgStop")
    twe.sendTWE(tweAddr[0], 0x71, [0xff])
    tcStatus = 0
    pauseTC = False

# ロボット本体との接続
def connect():
    # buttonConnect.grid_forget()
    global pauseTC
    pauseTC = True  # TCの一時停止
    
    for i in range(ROBOT_NUM):  # 1台ずつ接続
        if tweAddr[i] == 0xff:    # 未接続のとき
            terminalPrint("Connecting: " + str(i + 1))
            timeData = time.localtime()
            twe.sendTWE(0x78, 0x70, [i + 1, timeData.tm_year - 2000, timeData.tm_mon, timeData.tm_mday, timeData.tm_hour, timeData.tm_min, timeData.tm_sec])
            c = 0
            while True:
                tweResult = twe.recvTWE()
                # データ解析をするようにする
                if tweResult.address != "":    # パケットが受信できたとき
                    if tweResult.command == 0x30: # 通信成立報告
                        if tweResult.data[0] == i + 1:
                            terminalPrint("Connected: " + str(i + 1))
                            terminalPrint("TWE-Lite address: " + hex(tweResult.address))
                            terminalPrint("")
                            tweAddr[i] = tweResult.address
                            break
                        else:
                            terminalPrint("Failed: " + str(i + 1) + "Received: " + str(tweResult.data[0]))
                            terminalPrint("")
                            break
                time.sleep(0.01)
                c += 1
                if c > 100:
                    terminalPrint("No Connection: " + str(i + 1))
                    terminalPrint("")
                    break

    # buttonStart.grid(row=6,column=0,columnspan=2)
    pauseTC = False  # TCの再開

def exitTCApp():
    global pauseTC
    pauseTC = True
    ser.close()
    exit()

# 以下メインルーチン
init()
connectSerial()

# Bottleの設定
@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='./static/')

@route('/')
def index():
    return template('index', ROBOT_NUM = ROBOT_NUM)

@route('/update')
def ajax_update():
    dt = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    dict = {
        'dt': dt,
        'serial': use_port,
        'robot_num': ROBOT_NUM,
        'tcStatus': tcStatus,
        'terminal': terminalOutputBuff.copy(),
        'robot': {
            'pos': pos,
            'destPos': destPos,
            'finalDestPos': finalDestPos,
            'act': act,
            'request': request,
            'requestDestPos': requestDestPos,
            'permit': permit,
            'ballStatus': ballStatus,
            'tweAddr': tweAddr,
            'totalBalls': totalBalls,
            'testData': testData
        }
    }
    terminalOutputBuff.clear()
    return json.dumps(dict)

@route('/initTC')
def ajax_initTC():
    init()
    return "initTC"

@route('/connect-serial')
def ajax_connectSerial():
    res = connectSerial()
    if res:
        return "serial connected"
    else:
        return "serial not connected"

@route('/connect')
def ajax_connect():
    connect()
    return "connected"

@route('/emgStop')
def ajax_emgStop():
    compEmgStop()
    return "emgStop"

@route('/start')
def ajax_start():
    compStart()
    return "start"

@route('/exit')
def ajax_exit():
    exitTCApp()
    return "exit"

# 最後に実行
if __name__ == '__main__':
    run(host = '0.0.0.0', port = 5678, reloader = True, debug = True)