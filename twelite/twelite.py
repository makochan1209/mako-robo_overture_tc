import serial
import sys
import struct
import time

import serial.tools.list_ports

class Sample: pass # 空のクラス

# [0xA5, 0x5A, 0x80, "Length", "Data", "CD", 0x04]の形式で受信
# "Data": 0x0*（送信元）, Command, Data

class TWELITE:
    def __init__(self, ser):
        self.ser = ser
        self.ser.baudrate = 115200
        self.ser.parity = serial.PARITY_NONE
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.timeout = None
            
    def recvTWE(self, responcePacket = False):
        """
        TWEが受信したデータを返す関数。返り値は受信したデータのオブジェクト。

        Parameters
        ----------
        responcePacket : リスポンスパケットを出力するかどうか（省略時はFalse, 出力せず省略する）
        
        Returns
        -------
        address : 送信元論理ID
        command : コマンド
        data : データ（配列）
        """
        # 値の初期化
        cdBuff = 0
        serBuffStr = []
        result = Sample()

        WAIT_TIME = 1
        waitTimeCount = 0
        
        # データ受信
        if self.ser.in_waiting > 0:    # データが来ていないとき
            while True: # データが来ているか・またはデバッグモードのとき。このループは1バイトごと、パケット受信完了でbreak
                if self.ser.in_waiting <= 0:    # データが来ていないとき
                    time.sleep(0.05)
                    waitTimeCount += 0.05
                    if waitTimeCount >= WAIT_TIME:  # 1秒以上データが来ないとき
                        break
                
                else:
                    waitTimeCount = 0

                    buff = struct.unpack("<B", self.ser.read())[0]
                    serBuffStr.append(buff)
                
                    if len(serBuffStr) == 1 and buff != 0xA5: # パケット開始がA5でない場合は破棄
                        serBuffStr = []
                        
                    elif len(serBuffStr) > 4:    # データの範囲
                        if len(serBuffStr) <= 4 + serBuffStr[3]:    # データ終了まで
                            cdBuff = cdBuff ^ buff   # CD計算
                        elif len(serBuffStr) == 4 + serBuffStr[3] + 2:    # EOTまで終了
                            break
            
            if serBuffStr != []:
                print("Packet Received")
                print("Recieved Data:")
                print([hex(i) for i in serBuffStr])
                if serBuffStr[len(serBuffStr) - 1] == 0x04: # EOTチェック
                    print("EOT OK")
                    if cdBuff == serBuffStr[len(serBuffStr) - 2]:
                        print("CD OK")
                    else:
                        print("CD NG, Expected: " + hex(cdBuff) + ", Received: " + hex(serBuffStr[len(serBuffStr) - 2]))
                else:
                    print("EOT NG")

                if serBuffStr != [] and len(serBuffStr) < 8:    # パケットが短すぎる場合は破棄
                    serBuffStr = []
                    print("Packet too short")
                elif serBuffStr != [] and serBuffStr[4] == 0xdb:   # 応答メッセージなので省略
                    if not responcePacket:  # リスポンスパケットを省略する場合は破棄
                        serBuffStr = []
                    print("Response Packet")

        # データ解析
        if serBuffStr != []:
            result.address = serBuffStr[4]
            result.command = serBuffStr[5]
            result.data = serBuffStr[6:len(serBuffStr) - 2]
        else:
            result.address = ""
            result.command = ""
            result.data = []
        return result

    def sendTWE(self, toID, command, data):
        """
        TWEから他のTWEへデータを送信する関数。返り値は成功したかどうかの真偽値。

        Parameters
        ----------
        toID : 送信先論理ID、0x78のときは全台に送信
        command : コマンド
        data : データ（配列または1バイト）
        """
        result = False
        sendPacket = [0xA5, 0x5A, 0x80, 0x03, toID, command]
        if isinstance(data, list):
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
            
        self.ser.write(b''.join([struct.pack("<B", val) for val in sendPacket]))

        for i in range(0, 20):  # 1秒待つ
            tweResult = self.recvTWE(True)
            if tweResult.address != "":
                if tweResult.address == 0xdb:   # リスポンスパケット
                    result = True
                    break
            time.sleep(0.05)
        return result

def twe_serial_ports_detect():
    """
    TWELITEに接続されているシリアルポートを自動で検出する関数。返り値はポート名。
    """
    result = None
    if sys.platform.startswith('win') or sys.platform.startswith('linux'):
        suggestPorts = []
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            if (p.vid == 0x0403 and (p.pid == 0x6001 or p.pid == 0x6015)) or p.device == '/dev/serial0':    # TWE-Lite-R, Raspberry Pi => GPIO UART
                ser_ = serial.Serial(p.device)
                twe = TWELITE(ser_)
                sendResult = twe.sendTWE(0x00, 0x00, 0x00)
                if sendResult:
                    suggestPorts.append(p.device)
        
        if len(suggestPorts) == 0:
            print('TWELITE not found')
        
        else:
            if len(suggestPorts) == 1:
                print(suggestPorts[0])
                result = suggestPorts[0]
            else:
                i = 1
                for port in suggestPorts:
                    print("i: ", port)
                    i += 1
                print("Enter the number or the port name you want to use")
                result = input()
                if result.isdigit():
                    result = suggestPorts[int(result) - 1]
            print("Port " + result + " is connected to TWE-Lite.")
            
    else:
        print('Unsupported platform')
    return result