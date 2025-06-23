# 積立投資シミュレーター

このアプリは、指定した株式ティッカーの過去の株価をもとに、毎月一定額を積み立てた場合の投資成果をシミュレーションできるツールです。  
Streamlitを用いて手軽に実行・可視化が可能です。

---

##　主な機能

- 任意の株式ティッカー（例：AAPL, NVDA）で月次株価データを自動取得
- 毎月の積立額を自由に指定可能
- スライダーで積立表示期間を自由に選択可能
- 累積投資額、評価額、含み損益を自動で計算
- グラフ表示で投資成績の推移を可視化
- シミュレーション結果を履歴として記録・比較

---

## セットアップ手順
以下の手順でこのアプリをローカル環境で動かせます。

###1. リポジトリをクローンする
```bash
git clone https://github.com/your-username/stock_simulator.git
cd stock_simulator
※上記のURLのyour-usernameの部分は自身のGitHubアカウントのものに置き換えてください。

###2. 仮想環境の作成と起動(Windowsの場合)
python -m venv venv
.\venv\Scripts\activate
**PowerShellを使用していてエラーが出る場合は一時的にスクリプト実行を許可します。
Set-ExecutionPolicy RemoteSigned -Scope Process

###3. ライブラリのインストール
pip install -r requirements.txt

###4. アプリの軌道
以下のコマンドでStreamlitアプリが起動します。
streamlit run app.py
(自動的にアプリが立ち上がります)

## ディレクトリ構成
stock_simulator/
├── app.py                  # メインアプリケーション
├── requirements.txt        # 必要なライブラリ一覧
├── README.md               # この説明ファイル
└── venv/                   # 仮想環境フォルダ

## 使用ライブラリ
・streamlit
・pandas
・matplotlib
・yfinance
・datetime

##開発者メモ
今後の改善案
・為替変換機能の追加
・複数銘柄の比較機能