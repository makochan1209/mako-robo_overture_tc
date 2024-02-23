# venv
## git
https://qiita.com/TooFuu/items/9524198fab5b2ebf46a3

## 使い方
https://qiita.com/bluepost59/items/c13c88a9387e28189d7b
https://qiita.com/fiftystorm36/items/b2fd47cf32c7694adc2e
https://qiita.com/fiftystorm36/items/b2fd47cf32c7694adc2e

### 環境構築
```
python -m venv venv_overture_tc
```

以下は仮想環境ディレクトリ（```venv_overture_tc```）内で行う。

仮想環境起動後に、```requirements.txt```は```Scripts```ディレクトリ内に配置してモジュールインストール。
```
pip install -r requirements.txt
```

### 仮想環境起動・終了
Powershell
```
.\Scripts\Activate.ps1
deactivate
```

Linux
```
. ./bin/activate
deactivate
```

### requirements.txtの生成
```
pip freeze > requirements.txt
```
```venv_config```ディレクトリを共有用に用意済。

## Raspberry Pi 4
https://qiita.com/osw_nuco/items/a5d7173c1e443030875f
https://irohaplat.com/raspberry-pi-local-web-server/

```:overture.sh
~/overture/venv_overture_tc/bin/python ~/overture/TC_main.py
```

### systemd
https://www.raspberrypirulo.net/entry/systemd
https://qiita.com/marumen/items/e4c75a2617cb5d0113ce
https://qiita.com/tabimoba/items/e0230eb9d1f943b8708f

```:/lib/systemd/system/overture.service
[Unit]
Description = Overture by Team mako-robo TC_main.py Auto Run
ConditionPathExists=/home/makochan12.9/overture

[Service]
WorkingDirectory=/home/makochan12.9/overture
ExecStart=/home/makochan12.9/overture/venv_overture_tc/bin/python /home/makochan12.9/overture/TC_main.py
Restart=always
Type=simple

[Install]
WantedBy=multi-user.target
```

### サービスの起動、終了
```:terminal
sudo systemctl start overture.service
sudo systemctl stop test.service
```

GitでPullなどしたあとは再起動を
```:terminal
sudo systemctl restart overture.service
```

### サービスの自動起動の有効、無効
```:terminal
sudo systemctl enable test.service
sudo systemctl disable test.service
```