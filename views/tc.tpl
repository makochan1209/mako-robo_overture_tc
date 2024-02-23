<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Overture by Team mako-robo 管理コンソール</title>
</head>
<body>
    <h2>Overture by Team mako-robo 管理コンソール</h2>
    <div>
        現在時刻：<span id = "time"></span>
    </div>
    <div>シリアルポート：<span id = "serial"></span></div>
    <div>
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

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
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
            $.ajax("/connect", {
                type: "get"
            }).done(function(received_data) {
                console.log(received_data);
            }).fail(function() {
                console.log("失敗");
            });
        }

        function emgStop() {
            $.ajax("/emgStop", {
                type: "get"
            }).done(function(received_data) {
                console.log(received_data);
            }).fail(function() {
                console.log("失敗");
            });
        }

        function start() {
            $.ajax("/start", {
                type: "get"
            }).done(function(received_data) {
                console.log(received_data);
            }).fail(function() {
                console.log("失敗");
            });
        }

        function exitTC() {
            $.ajax("/exit", {
                type: "get"
            }).done(function(received_data) {
                console.log(received_data);
            }).fail(function() {
                console.log("失敗");
            });
        }

        function updateDOM() {
            $.ajax("/update", {
                type: "get"
            }).done(function(received_data) {           // 戻ってきたのはJSON（文字列）
                let dict = JSON.parse(received_data);   // JSONを連想配列にする
                // 以下、Javascriptで料理する
                let dt = dict["dt"];
                let serial = dict["serial"];
                $("#time").html(dt);              // html要素を書き換える
                $("#serial").html(serial != null ? serial : "未接続");              // html要素を書き換える

                for (let i = 0; i < dict["robot_num"]; i++) {
                    let robot = dict["robot"];
                    $(".robot-container").eq(i).find(".robot-twe-id").find("span").html(robot["tweAddr"][i] != 0xff ? ("0x" + robot["tweAddr"][i].toString(16)) : "未接続");
                    $(".robot-container").eq(i).find(".robot-pos").find("span").html("0x" + robot["pos"][i].toString(16));
                    $(".robot-container").eq(i).find(".robot-dest-pos").find("span").html("0x" + robot["destPos"][i].toString(16));
                    $(".robot-container").eq(i).find(".robot-act").find("span").html((robot["act"][i] != 0xff ? robot["actText"][robot["act"][i]] : "なし") + "（0x" + robot["act"][i].toString(16) + "）");
                    //$(".robot-container").eq(i).find(".robot-ball").find("span.r").html(robot["ballStatus"][i]["r"]);
                    //$(".robot-container").eq(i).find(".robot-ball").find("span.y").html(robot["ballStatus"][i]["y"]);
                    //$(".robot-container").eq(i).find(".robot-ball").find("span.b").html(robot["ballStatus"][i]["b"]);
                    $(".robot-container").eq(i).find(".robot-request").find("span").html((robot["request"][i] != 0xff ? robot["requestText"][robot["request"][i]] : "なし") + "（0x" + robot["request"][i].toString(16) + "）");
                    //$(".robot-container").eq(i).find(".robot-request-dest").find("span").html("0x" + robot["requestDestPos"][i].toString(16) + "）");
                    $(".robot-container").eq(i).find(".robot-permit").find("span").html((robot["permit"][i] != 0xff ? robot["permitText"][robot["permit"][i]] : "なし") + "（0x" + robot["permit"][i].toString(16) + "）");
                }
            }).fail(function() {
                console.log("失敗");
            });
        };
        updateDOM();
        setInterval(updateDOM, 500);
    </script>
</body>
</html>