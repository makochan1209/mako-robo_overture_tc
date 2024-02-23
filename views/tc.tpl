<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Overture by Team mako-robo 管理コンソール</title>
</head>
<body>
    <style>
        #wrapper {
            padding: 0 100px;
        }

        #robot-list-container {
            display: flex;
        }

        .robot-container {
            width: 300px;

        }
    </style>
    <div id = "wrapper">
        <h2>Overture by Team mako-robo 管理コンソール</h2>
        <div>
            現在時刻：<span id = "time"></span>
        </div>
        <div>シリアルポート：<span id = "serial"></span></div>
        <div id = "robot-list-container">
            % for i in range(ROBOT_NUM):
                <div class = "robot-container">
                    <div class = "robot-no">{{i + 1}}号機</div>
                    <div class = "robot-twe-id">TWE-LITE アドレス：<span></span></div>
                    <div class = "robot-pos">現在地：<span></span></div>
                    <div class = "robot-dest-pos">目的地：<span></span></div>
                    <div class = "robot-act">現在の行動：<span></span></div>
                    <div class = "robot-ball">ボール状況：赤<span class = "r"></span>個、黄<span class = "y"></span>個、青<span class = "b"></span>個</div>
                    <div class = "robot-request">現在の許可要求：<span></span></div>
                    <div class = "robot-act">現在の許可要求の目的地：<span></span></div>
                    <div class = "robot-permit">直近の許可内容：<span></span></div>
                </div>
            % end
        </div>
        <div>
            <button onclick = "connectSerial()">1: シリアルポートと接続</button>
            <button onclick = "connect()">2: ロボットと接続</button>
            <button onclick = "emgStop()">3: 全ロボット緊急停止</button>
            <button onclick = "start()">4: 競技開始</button>
            <!--<button onclick = "exitTC()">9: プログラム終了</button>-->
            <button onclick = "initTC()">0: プログラムのリセット（動作不調時のみ、シリアルポートはリセットされない）</button>
        </div>
    </div>

    <script type="text/javascript">
        function initTC() {
            let xhr = new XMLHttpRequest();
            xhr.open('GET', '/initTC');
            xhr.send();
            xhr.onload = function () {
                console.log(xhr.response);
            };
        }

        function connectSerial() {
            let xhr = new XMLHttpRequest();
            xhr.open('GET', '/connect-serial');
            xhr.send();
            xhr.onload = function () {
                console.log(xhr.response);
            };
        }

        function connect() {
            let xhr = new XMLHttpRequest();
            xhr.open('GET', '/connect');
            xhr.send();
            xhr.onload = function () {
                console.log(xhr.response);
            };
        }

        function emgStop() {
            let xhr = new XMLHttpRequest();
            xhr.open('GET', '/emgStop');
            xhr.send();
            xhr.onload = function () {
                console.log(xhr.response);
            };
        }

        function start() {
            let xhr = new XMLHttpRequest();
            xhr.open('GET', '/start');
            xhr.send();
            xhr.onload = function () {
                console.log(xhr.response);
            };
        }

        function exitTC() {
            let xhr = new XMLHttpRequest();
            xhr.open('GET', '/exit');
            xhr.send();
            xhr.onload = function () {
                console.log(xhr.response);
            };
        }

        function updateDOM() {
            let xhr = new XMLHttpRequest();
            xhr.open('GET', '/update');
            xhr.send();
            xhr.onload = function () {
                const dict = JSON.parse(xhr.responseText);
                // 以下、Javascriptで料理する
                const dt = dict["dt"];
                const serial = dict["serial"];
                const robot = dict["robot"];
                document.getElementById("time").innerText = dt
                document.getElementById("serial").innerText = (serial != null ? serial : "未接続")

                for (let i = 0; i < dict["robot_num"]; i++) {
                    const robotContainer = document.getElementsByClassName("robot-container")[i];

                    robotContainer.getElementsByClassName("robot-twe-id")[0].getElementsByTagName("span")[0].innerText = (robot["tweAddr"][i] != 0xff ? ("0x" + robot["tweAddr"][i].toString(16)) : "未接続");
                    robotContainer.getElementsByClassName("robot-pos")[0].getElementsByTagName("span")[0].innerText = ("0x" + robot["pos"][i].toString(16));
                    robotContainer.getElementsByClassName("robot-dest-pos")[0].getElementsByTagName("span")[0].innerText = ("0x" + robot["destPos"][i].toString(16));
                    robotContainer.getElementsByClassName("robot-act")[0].getElementsByTagName("span")[0].innerText = ((robot["act"][i] != 0xff ? robot["actText"][robot["act"][i]] : "なし") + "（0x" + robot["act"][i].toString(16) + "）");
                    robotContainer.getElementsByClassName("robot-ball")[0].getElementsByClassName("r")[0].innerText = robot["ballStatus"][i]["r"];
                    robotContainer.getElementsByClassName("robot-ball")[0].getElementsByClassName("y")[0].innerText = robot["ballStatus"][i]["y"];
                    robotContainer.getElementsByClassName("robot-ball")[0].getElementsByClassName("b")[0].innerText = robot["ballStatus"][i]["b"];
                    robotContainer.getElementsByClassName("robot-request")[0].getElementsByTagName("span")[0].innerText = ((robot["request"][i] != 0xff ? robot["requestText"][robot["request"][i]] : "なし") + "（0x" + robot["request"][i].toString(16) + "）");
                    // robotContainer.getElementsByClassName("robot-request-dest")[0].getElementsByTagName("span")[0].innerText = ("0x" + robot["requestDestPos"][i].toString(16) + "）");
                    robotContainer.getElementsByClassName("robot-permit")[0].getElementsByTagName("span")[0].innerText = ((robot["permit"][i] != 0xff ? robot["permitText"][robot["permit"][i]] : "なし") + "（0x" + robot["permit"][i].toString(16) + "）");
                }
            };
        }

        updateDOM();
        setInterval(updateDOM, 250);
    </script>
</body>
</html>