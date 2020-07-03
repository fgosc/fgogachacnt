# fgogachacnt
FGOのガチャ結果スクショを集計する

しょっぽさんが集計しているフレンドポイント召喚集計 https://sites.google.com/site/gurugurufgo/home/flyer/fp-gacha の詳細報告をするためのツールです

# 必要なソフトウェア
Python 3.7以降

# ファイル
1. fgogachacnt.py :実行ファイル(画像認識)
2. csv2report.py :実行ファイル(報告作成)
3. makecard.py card.xml を作成
4. data 3.で使用されるフォルダ

以下は3.実行時に作成される

5. card.xml:  カード下部の文字を読むSVMのトレーニングファイル

# インストール

* OpenCV をインストール
* makecard.py を実行

下記コマンドを実行

`$ python makecard.py`

※fgogachacnt.py, csv2report.py, card.xmlを同じフォルダにいれること


# 使い方
```
usage: fgogachacnt.py [-h] [-m {10,11}] [-f FOLDER] [-d] [--version]
                      [filenames [filenames ...]]

FGO召喚スクショを数えをCSV出力する

positional arguments:
  filenames             入力ファイル

optional arguments:
  -h, --help            show this help message and exit
  -m {10,11}, --mode {10,11}
                        召喚モード
  -f FOLDER, --folder FOLDER
                        フォルダで指定
  -d, --debug           デバッグ情報の出力
  --version             show program's version number and exit
```

# 実行例
```
$ python fgogachacnt.py image/IMG_????.PNG >output.csv
$ python csv2report.py output.csv
【フレンドポイント召喚】8860回
★0鯖0-★1鯖899-★2鯖427-★3鯖77-★4鯖3
★1種火832-★2種火677-★3種火442-★4種火257-★5種火100
★1フォウ338-★2フォウ168-★3フォウ120
★1礼装2551-★2礼装1412-★3礼装441
★1コード79-★2コード37
#FGO_FP召喚報告
```

***
* 恒常以外のカードを初めて認識させた場合、item フォルダ内に servent???.png, ce???.png というファイルができる
* ファイル名をアイテム名に変更すると次回実行以降もそのアイテム名で表示されるため可読性があがる
* 恒常以外のカードがあるスクショを認識させた場合 `csv2report.py` ではレアリティ認識できないので、分類「その他」として出力されるため計算結果を自分で修正する必要がある

# 制限
* QPカンスト時にフォウ君を自動売却設定しているとレアリティを誤認識する
