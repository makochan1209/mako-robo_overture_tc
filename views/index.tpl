<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <link href = "/static/index.css" rel = "stylesheet">
    <title>Overture - mako-robo Manager</title>
    <meta name="viewport" content="width = device-width, initial-scale = 1, shrink-to-fit = no">
    <link rel="stylesheet" href="/static/odometer-theme-minimal.css">
</head>
<body>
    <div id = "all-wrapper">
        <header>
            <div class = "wrapper">
                <div class = "mrma-icon"><div>mako-robo</div><div>Manager</div></div>
                <div id = "time"><span></span>/<span></span>/<span></span> <span></span>:<span></span>:<span></span></div>
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
                            <div class = "value"><span id = "serial" class = "main-value"></span></div>
                        </div>
                        <div class = "info-bar-telemetry-box small-margin-right">
                            <div class = "title">Total Point</div>
                            <div class = "value"><span id = "total-point-value" class = "main-value">44</span><span class = "smaller-value">/ 50</span></div>
                        </div>
                        <div class = "info-bar-telemetry-box total-point-detail-box">
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
                                    <h4>Robot {{i + 1}} <span class = "robot-twe-id"></span></h4>
                                    <div class = "robot-info-box">
                                        <div class = "robot-info-status">
                                            <span class = "value">SEARCHING</span><span class = "smaller-value">(5 / 5)</span>
                                        </div>
                                        <ul class = "robot-ball-status">
                                            <li class = "red-ball-status ball-point-elem red-ball-point-elem">1</li>
                                            <li class = "yellow-ball-status ball-point-elem yellow-ball-point-elem">1</li>
                                            <li class = "blue-ball-status ball-point-elem blue-ball-point-elem">2</li>
                                        </ul>
                                    </div>
                                </div>
                            % end
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

    <script src="/static/odometer.js"></script>
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
                const dt = dict["dt"].split(' ');
                const serial = dict["serial"];
                const robot = dict["robot"];

                // TWE-Lite接続数
                let tweCount = 0;
                for (let i = 0; robot["tweAddr"].length; i++) {
                    if (robot["tweAddr"] != 0xff) {
                        tweCount++;
                    }
                }
                
                // 時刻
                const dtArray = [dt[0].split('/'), dt[1].split(':')];
                const dtSpanElements = document.getElementById("time").getElementsByTagName("span");
                for (let i = 0; i < 6; i++) {
                    dtSpanElements[i].innerHTML = dtArray[Math.floor(i / 3)][i % 3];
                }
                
                // 全体の情報
                document.getElementById("serial").innerText = (serial != null ? serial : "未接続")
                
                /*const infoBarStatusClass = ["inactive", "idle", "run"];
                const infoBarStatusElement = document.getElementById("info-bar-status");
                infoBarStatusClass.forEach((elem) => infoBarStatusElement.classList.remove(elem));
                if (serial == null) {
                    infoBarStatusElement.innerText = "INACTIVE";
                    infoBarStatusElement.classList.add("inactive");
                }
                else if (tweCount == 0) {
                    infoBarStatusElement.innerText = "OFFLINE";
                    infoBarStatusElement.classList.add("inactive");
                }
                else if (tweCount > 0 && 1 == 1) {//競技中かどうか
                    infoBarStatusElement.innerText = "IDLING";
                    infoBarStatusElement.classList.add("idle");
                }
                else {
                    infoBarStatusElement.innerText = "RUNNING";
                    infoBarStatusElement.classList.add("run");
                }*/

                // マップ準備
                const mapPosElementsList = [document.getElementById("map-pos00"), document.getElementById("map-pos01"), document.getElementById("map-pos02"), document.getElementById("map-pos03"), document.getElementById("map-pos04"), document.getElementById("map-pos05"), document.getElementById("map-pos06"), document.getElementById("map-pos07"), document.getElementById("map-pos08"), document.getElementById("map-pos09")];
                for (let i = 0; i < mapPosElementsList.length; i++) {
                    mapPosElementsList[i].innerHTML = "";
                }

                // ロボットごとの情報・マップ反映
                for (let i = 0; i < dict["robot_num"]; i++) {
                    const robotContainer = document.getElementsByClassName("robot-container")[i];

                    robotContainer.getElementsByClassName("robot-twe-id")[0].innerText = (robot["tweAddr"][i] != 0xff ? ("(TWE-Lite: " + ("0x" + robot["tweAddr"][i].toString(16)) + ")") : "");
                    robotInfoStatusElement = robotContainer.getElementsByClassName("robot-info-status")[0];
                    robotInfoStatusValueElement = robotInfoStatusElement.getElementsByClassName("value")[0];
                    robotInfoStatusSmallerValueElement = robotInfoStatusElement.getElementsByClassName("smaller-value")[0];

                    if (robot["tweAddr"][i] == 0xff) {
                        robotInfoStatusValueElement.innerText = "NOT CONNECTED";
                    }
                    else {
                        switch (robot["act"][i]) {
                            case 0x00:
                            robotInfoStatusValueElement.innerText = "WAITING";
                            break;
                            case 0x01:
                            robotInfoStatusValueElement.innerText = "MOVING";
                            break;
                            case 0x02:
                            case 0x03:
                            robotInfoStatusValueElement.innerText = "SEARCHING";
                            break;
                            case 0x04:
                            case 0x05:
                            robotInfoStatusValueElement.innerText = "APPROACH";
                            break;
                            case 0x06:
                            robotInfoStatusValueElement.innerText = "CATCHING";
                            break;
                            case 0x07:
                            robotInfoStatusValueElement.innerText = "SHOOTING";
                            break;
                        }
                    }

                    if ((robot["act"][i] <= 0x01 && robot["act"][i] >= 0x06) || robot["tweAddr"][i] == 0xff) {
                        robotInfoStatusSmallerValueElement.classList.add("d-none");
                        robotInfoStatusSmallerValueElement.innerText = "";
                    }
                    else {
                        robotInfoStatusSmallerValueElement.innerText = "(" + "-" + " / " + "-" + ")";
                        robotInfoStatusSmallerValueElement.classList.remove("d-none");
                    }

                    robotBallStatusElement = robotContainer.getElementsByClassName("robot-ball-status")[0];

                    if (robot["ballStatus"][i]["r"] + robot["ballStatus"][i]["y"] + robot["ballStatus"][i]["b"] == 0) {
                        robotBallStatusElement.classList.add("d-none");
                    }
                    else {
                        robotBallStatusElement.classList.remove("d-none");
                    }

                    robotBallStatusElement.getElementsByClassName("red-ball-status")[0].innerText = robot["ballStatus"][i]["r"];
                    robotBallStatusElement.getElementsByClassName("yellow-ball-status")[0].innerText = robot["ballStatus"][i]["y"];
                    robotBallStatusElement.getElementsByClassName("blue-ball-status")[0].innerText = robot["ballStatus"][i]["b"];

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

                // メッセージ
                /*const noticeElement = document.getElementById("notice");
                if (serial == none) {
                    noticeElement.innerHTML = `
                        TWE-Lite（親機）が接続されていません。<br>
                        「シリアルポートに接続」を押して接続してください。
                    `;
                }
                else if (tweCount == 0) {
                    noticeElement.innerHTML = `
                        ロボットが接続されていません。<br>
                        「ロボットに接続」を押してください。
                    `;
                }
                else {
                    if (tweCount == 1) {
                        noticeElement.innerHTML = `
                            1台のロボットに接続されています。単独試技モードで走行可能です。<br>
                            「出走前チェックリスト」を開いて、出走前チェックを行ってください。 / チェックリスト完了。「競技開始」を押して出走してください。
                        `;
                    }
                    else if (tweCount == 2) {
                        noticeElement.innerHTML = `
                            2台のロボットに接続されています。協調試技モードで走行可能です。<br>
                            「出走前チェックリスト」を開いて、出走前チェックを行ってください。 / チェックリスト完了。「競技開始」を押して出走してください。
                        `;
                    }
                }*/
                

                // ボタン
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

                // 出力
                terminalElement = document.getElementById("terminal")
                for (i = 0; i < robot["terminal"].length; i++) {
                    terminalElement.value += (robot["terminal"][i] + "\n")
                }
                terminalElement.scrollTop = terminalElement.scrollHeight;
            };
        }

        window.addEventListener("load", (event) => {
            updateDOM();
            setInterval(updateDOM, 250);
        });
    </script>
</body>
</html>