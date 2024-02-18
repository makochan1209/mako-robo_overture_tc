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