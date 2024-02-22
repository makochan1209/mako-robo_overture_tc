<!DOCTYPE html>
<html lang="en">
<head>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>World Clock</title>
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
                <div class = "robot-ball">ボール状況：赤<span></span>個、黄<span></span>個、青<span></span>個</div>
                <div class = "robot-request">現在の許可要求：<span></span></div>
                <div class = "robot-act">現在の許可要求の目的地：<span></span></div>
                <div class = "robot-permit">直近の許可内容：<span></span></div>
            </div>
        % end
    </div>
    <div><button onclick = "connect()">1: ロボットと接続</button><button onclick = "emgStop()">2: 全ロボット緊急停止</button><button onclick = "start()">3: 競技開始</button></div>
    <script type="text/javascript">
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

        function updateDOM() {
            $.ajax("/update", {
                type: "get"
            }).done(function(received_data) {           // 戻ってきたのはJSON（文字列）
                let dict = JSON.parse(received_data);   // JSONを連想配列にする
                // 以下、Javascriptで料理する
                let dt = dict["dt"];
                let serial = dict["serial"];
                $("#time").html(dt);              // html要素を書き換える
                $("#serial").html(serial);              // html要素を書き換える
            }).fail(function() {
                console.log("失敗");
            });
        };
        updateDOM();
        setInterval(updateDOM, 100);
    </script>
</body>
</html>