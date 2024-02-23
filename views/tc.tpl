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
        #all-wrapper {
            padding: 0 100px;
        }

        #button-wrapper {
            margin: 0.5rem 0;
        }

        #content-wrapper {
            margin: 1rem 0;
            display: flex;
            justify-content: space-between;
        }

        #robot-list-container {
            display: flex;
            flex-wrap: wrap;
        }

        .robot-container {
            width: 300px;
            margin-bottom: 0.5rem;
        }

        #robot-stage-container {
            display: flex;
            flex-direction: column;
            align-items: end;
            max-height: 50vh;
        }

        #robot-stage {
            position: relative;
            height: 100%;
        }

        #robot-stage img {
            height: 100%;
            object-fit: contain;
        }

        #robot-stage div.map-pos {
            display: inline-block;
            position: absolute;
            text-align: center;
            transform: translateX(-50%) translateY(-50%);
            background-color: white;
        }

        #map-pos00 {
            top: calc(100% / 810 * 665);
            left: calc(100% / 704 * 205);
        }

        #map-pos01, #map-pos02, #map-pos03, #map-pos04 {
            left: calc(100% / 704 * 221);
        }

        #map-pos01 {
            top: calc(100% / 810 * 505);
        }

        #map-pos02 {
            top: calc(100% / 810 * 405);
        }
        
        #map-pos03 {
            top: calc(100% / 810 * 306);
        }

        #map-pos04 {
            top: calc(100% / 810 * 206);
        }

        #map-pos05, #map-pos06 {
            top: calc(100% / 810 * 107);
        }
        
        #map-pos05 {
            left: calc(100% / 704 * 145);
        }

        #map-pos06, #map-pos08 {
            left: calc(100% / 704 * 313);
        }

        #map-pos07, #map-pos09 {
            left: calc(100% / 704 * 540);
        }

        #map-pos07 {
            top: calc(100% / 810 * 184);
        }

        #map-pos08, #map-pos09 {
            top: calc(100% / 810 * 525);
        }

        #button-wrapper {
            display: flex;
            flex-wrap: wrap;
        }

        ul#legend {
            display: flex;
            list-style: none;
        }

        ul#legend li {
            margin-left: 0.5rem;
        }

        span.icon-pos {
            color: green;
        }

        span.icon-dest-pos {
            color: red;
        }

        button {
            font-size: 1rem;
            padding: 1rem 0.5rem;
            margin-right: 0.5rem;
        }
    </style>
    <div id = "all-wrapper">
        <h2>Overture by Team mako-robo 管理コンソール</h2>
        <div>
            現在時刻：<span id = "time"></span>
        </div>
        <div>シリアルポート：<span id = "serial"></span></div>
        <div id = "button-wrapper">
            <button id = "btn-connect-serial" onclick = "connectSerial()">1: シリアルポートと接続</button>
            <button id = "btn-connect" onclick = "connect()">2: ロボットと接続</button>
            <button id = "btn-emg-stop" onclick = "emgStop()">3: 全ロボット緊急停止</button>
            <button id = "btn-start" onclick = "start()">4: 競技開始</button>
            <!--<button id = "btn-exit" onclick = "exitTC()">9: プログラム終了</button>-->
            <button id = "btn-init" onclick = "initTC()">0: プログラムのリセット（動作不調時のみ、シリアルポートはリセットされない）</button>
        </div>
        <div id = "content-wrapper">
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
            <div id = "robot-stage-container">
                <div id = "robot-stage">
                    <img src = "/static/stage.webp">
                    <div id = "map-pos00" class = "map-pos"></div>
                    <div id = "map-pos01" class = "map-pos"></div>
                    <div id = "map-pos02" class = "map-pos"></div>
                    <div id = "map-pos03" class = "map-pos"></div>
                    <div id = "map-pos04" class = "map-pos"></div>
                    <div id = "map-pos05" class = "map-pos"></div>
                    <div id = "map-pos06" class = "map-pos"></div>
                    <div id = "map-pos07" class = "map-pos"></div>
                    <div id = "map-pos08" class = "map-pos"></div>
                    <div id = "map-pos09" class = "map-pos"></div>
                </div>
                <ul id = "legend">
                    <li><span class = "icon-pos">①②</span>：現在地</li>
                    <li><span class = "icon-dest-pos">①②</span>：目的地</li>
                </ul>
            </div>
        </div>
    </div>

    <script type="text/javascript">
        function numStringConv(i) {
            switch(i) {
                case 1:
                numString = "①";
                break;
                case 2:
                numString = "①";
                break;
                case 3:
                numString = "①";
                break;
                case 4:
                numString = "①";
                break;
                case 5:
                numString = "①";
                break;
                case 6:
                numString = "①";
                break;
                case 7:
                numString = "①";
                break;
                case 8:
                numString = "①";
                break;
                case 9:
                numString = "①";
                break;
            }
            return numString;
        }

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

                const mapPosElementsList = [document.getElementById("map-pos00"), document.getElementById("map-pos01"), document.getElementById("map-pos02"), document.getElementById("map-pos03"), document.getElementById("map-pos04"), document.getElementById("map-pos05"), document.getElementById("map-pos06"), document.getElementById("map-pos07"), document.getElementById("map-pos08"), document.getElementById("map-pos09")];
                for (let i = 0; i < mapPosElementsList.len; i++) {
                    mapPosElementsList[i].innerHTML = "";
                }

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

                    const numString = numStringConv(i + 1);
                    if (robot["pos"][i] <= 0x09) {
                        const spanElement = document.createElement("span");
                        spanElement.classList.add("icon-pos");
                        spanElement.innerText = numString;
                        mapPosElementsList[i].appendChild(spanElement);
                    }
                    if (robot["destPos"][i] <= 0x09) {
                        const spanElement = document.createElement("span");
                        spanElement.classList.add("icon-dest-pos");
                        spanElement.innerText = numString;
                        mapPosElementsList[i].appendChild(spanElement);
                    }
                }
            };
        }

        updateDOM();
        setInterval(updateDOM, 250);
    </script>
</body>
</html>