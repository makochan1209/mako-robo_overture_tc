<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <link href = "/static/index.css" rel = "stylesheet">
    <title>Overture - mako-robo Manager</title>
</head>
<body>
    <div id = "all-wrapper">
        <header>
            <div class = "wrapper">
                <div class = "mrma-icon">mako-robo<div>Manager</div></div>
                <div id = "time"></div>
            </div>
        </header>
        <div id = "info-bar">
            <div class = "wrapper">
                <div id = "info-bar-img">
                    <img src = "/static/overture.png">
                </div>
                <div id = "info-bar-telemetry">
                    <div id = "info-bar-telemetry-upper">
                        <h1>Overture</h1>
                        <div id = "info-bar-status" class = "running">RUNNING</div>
                        <div class = "info-bar-telemetry-box">
                            <div class = "title">Port</div>
                            <div class = "value"><span id = "serial" class = "value"></span></div>
                        </div>
                        <div class = "info-bar-telemetry-box small-margin-right">
                            <div class = "title">Total Point</div>
                            <div class = "value"><span id = "total-point-value" class = "value">44</span><span class = "smaller-value"> / 50</span></div>
                        </div>
                        <div class = "info-bar-telemetry-box">
                            <ul class = "total-point-detail-list">
                                <li class = "ball-point-elem red-ball-point-elem" id = "total-red">5</li>
                                <li class = "ball-point-elem yellow-ball-point-elem" id = "total-yellow">4</li>
                            </ul>
                            <ul class = "total-point-detail-list">
                                <li class = "ball-point-elem blue-ball-point-elem" id = "total-blue">4</li>
                                <li class = "ball-point-elem tennis-ball-point-elem" id = "total-tennis">1</li>
                            </ul>
                        </div>
                    </div>
                    <div id = "info-bar-telemetry-lower">
                        <div id = "robot-list-container">
                            % for i in range(ROBOT_NUM):
                                <div class = "robot-container">
                                    <h4>Robot %i% <span class = "twe-lite-address"></span></h4>
                                    <div class = "robot-info-box">
                                        <div class = "robot-info-status">
                                            <span class = "value">SEARCHING</span><span class = "smaller-value"></span>
                                        </div>
                                        <ul class = "robot-ball-status">
                                            <li class = "ball-point-elem red-ball-point-elem" id = "total-red">5</li>
                                            <li class = "ball-point-elem yellow-ball-point-elem" id = "total-yellow">4</li>
                                            <li class = "ball-point-elem blue-ball-point-elem" id = "total-blue">4</li>
                                        </div>
                                    </div>
                                </div>
                    </div>
                </div>
            </div>
        </div>
        <div id = "main-page">
            <div class = "wrapper">
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
                        <li><span class = "icon-dest-pos">①②</span>：許可目的地</li>
                        <li><span class = "icon-final-dest-pos">①②</span>：最終目的地</li>
                    </ul>
                </div>
                
                <div id = "main-content-container">
                    <div id = "notice-container">
                        <h2>Notice</h2>
                        <p id = "notice">
                            TWE-Lite（親機）が接続されていません。<br>
                            「シリアルポートに接続」を押して接続してください。
                        </p>
                    </div>
                    <div id = "control-container">
                        <h2>Control</h2>
                        <div id = "button-wrapper">
                            <button id = "btn-connect-serial" onclick = "connectSerial()">シリアルポートと接続</button>
                            <button id = "btn-connect" onclick = "connect()">ロボットと接続</button>
                            <button id = "btn-emg-stop" onclick = "emgStop()">ロボット緊急停止</button>
                            <button id = "btn-start" onclick = "start()">競技開始</button>
                            <button id = "btn-init" onclick = "initTC()">リセット（動作不調時のみ）</button>
                        </div>
                    </div>
                    <div id = "terminal-container">
                        <h2>Output</h2>
                        <textarea id = "terminal" cols="80" rows="8"></textarea>
                    </div>
                </div>
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
                numString = "②";
                break;
                case 3:
                numString = "③";
                break;
                case 4:
                numString = "④";
                break;
                case 5:
                numString = "⑤";
                break;
                case 6:
                numString = "⑥";
                break;
                case 7:
                numString = "⑦";
                break;
                case 8:
                numString = "⑧";
                break;
                case 9:
                numString = "⑨";
                break;
                default:
                numString = i + " "
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

                const btnConnectSerialElement = document.getElementById("btn-connect-serial");
                const btnConnectElement = document.getElementById("btn-connect");
                const btnEmgStopElement = document.getElementById("btn-emg-stop");
                const btnStartElement = document.getElementById("btn-start");
                const btnInitElement = document.getElementById("btn-init");
                if (serial != null) {
                    btnConnectSerialElement.style.display = 'none';
                    btnConnectElement.style.display = 'block';
                    btnEmgStopElement.style.display = 'block';
                    btnStartElement.style.display = 'block';
                }
                else {
                    btnConnectSerialElement.style.display = 'block';
                    btnConnectElement.style.display = 'none';
                    btnEmgStopElement.style.display = 'none';
                    btnStartElement.style.display = 'none';
                }

                const mapPosElementsList = [document.getElementById("map-pos00"), document.getElementById("map-pos01"), document.getElementById("map-pos02"), document.getElementById("map-pos03"), document.getElementById("map-pos04"), document.getElementById("map-pos05"), document.getElementById("map-pos06"), document.getElementById("map-pos07"), document.getElementById("map-pos08"), document.getElementById("map-pos09")];
                for (let i = 0; i < mapPosElementsList.length; i++) {
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
                    if (robot["finalDestPos"][i] <= 0x09) {
                        const spanElement = document.createElement("span");
                        spanElement.classList.add("icon-final-dest-pos");
                        spanElement.innerText = numString;
                        mapPosElementsList[i].appendChild(spanElement);
                    }
                }
                terminalElement = document.getElementById("terminal")
                for (i = 0; i < robot["terminal"].length; i++) {
                    terminalElement.value += (robot["terminal"][i] + "\n")
                }
                terminalElement.scrollTop = terminalElement.scrollHeight;
            };
        }

        updateDOM();
        setInterval(updateDOM, 250);
    </script>
</body>
</html>