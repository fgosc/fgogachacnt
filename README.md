# fgogachacnt
FGOのガチャ結果スクショを集計する

実装されている全てのサーヴァント・概念礼装の認識に対応しています(新規サーヴァント・概念礼装の実装時には `update.py` の実行で対応)

一般的な使用法はしょっぽさんが集計しているフレンドポイント召喚集計 https://sites.google.com/site/gurugurufgo/home/flyer/fp-gacha の詳細報告をするためのツールです

# 必要なソフトウェア
Python 3.7以降

# ファイル
1. `fgogachacnt.py` :実行ファイル(画像認識)
2. `csv2report.py` :実行ファイル(報告作成)
3. `makecard.py` card.xml を作成
4. `makerarity.py` rarity.xml を作成
5. `data/` 3.4.で使用されるフォルダ
6. `hash_srv.csv` :サーヴァントの認識データ(update.pyで更新)
7. `hash_ce.csv` :概念礼装の認識データ(update.pyで更新)
8. `hash_ce_center.csv` :概念礼装の認識データ(update.pyで更新)
9. `srv_bl.csv`:ガチャから排出されないサーヴァントのリスト
10. `ce_bl.txt` :ガチャから排出されない概念礼装のリスト(絆礼装・記念礼装・経験値礼装以外)
11. `fp_34srv_wl.txt`  :フレンドポイントで召喚される★3★4サーヴァントのリスト
12. `fp_12ce_bl.txt` :フレンドポイントから排出されなくなった★1★2概念礼装のリスト
13. `fp_3ce_wl.txt` :フレンドポイントで召喚される★3概念礼装のリスト

以下は3.実行時に作成される

14. `card.xml`:  カード下部の文字を読むSVMのトレーニングファイル
15. `rality.xml`:  フォウくんのレアリティを判別するSVMのトレーニングファイル

# インストール
下記コマンドを実行
```
$ pip install -r requirements.txt
$ python makecard.py
$ python makerality.py
```
※`fgogachacnt.py`, `csv2report.py`, `*.xml`, `*.csv`, `*.txt`をを同じフォルダにいれること


# 使い方
```
usage: fgogachacnt.py [-h] [-m {fp,stone}] [-n {10,11}] [-f FOLDER] [-o] [-d]
                      [--version]
                      [filenames [filenames ...]]

FGOの召喚スクショを数えをCSV出力する

positional arguments:
  filenames             入力ファイル

optional arguments:
  -h, --help            show this help message and exit
  -m {fp,stone}, --mode {fp,stone}
                        召喚モード フレポ:fp 聖晶石:stone
  -n {10,11}, --num {10,11}
                        召喚数
  -f FOLDER, --folder FOLDER
                        フォルダで指定
  -o, --old             2018年8月以前の召喚画面
  -d, --debug           デバッグ情報の出力
  --version             show program's version number and exit
```

# 実行例
# フレンドポイント召喚のスクショ処理から召喚報告まで
```
$ python fgogachacnt.py -f image >output.csv
$ python csv2report.py output.csv
【フレンドポイント召喚】8860回
★0鯖0-★1鯖899-★2鯖427-★3鯖77-★4鯖3
★1種火832-★2種火677-★3種火442-★4種火257-★5種火100
★1フォウ338-★2フォウ168-★3フォウ120
★1礼装2551-★2礼装1412-★3礼装441
★1コード79-★2コード37
#FGO_FP召喚報告
```
# 聖晶石召喚のスクショ処理から召喚報告まで
```
$ python fgogachacnt.py -n 11 -m stone -f image >output.csv
$ python csv2report.py output.csv
【聖晶石召喚】1628回
★3鯖569-★4鯖85-★5鯖1145
★3礼装490-★4礼装271-★5礼装68(うちカレスコ4)
#FGO_聖晶石召喚報告
```
# サーヴァント・概念礼装データのアップデート
```
$ python update.py
```

***
* 認識できないカードを初めて認識させた場合、item フォルダ内に servent???.png, ce???.png というファイルができる
* 出力でDuplication が出た場合は、同じ召喚画面を二回スクショしているものである
* ファイル名servent???.png, ce???.pngをアイテム名に変更すると次回実行以降そのアイテム名で表示されるため可読性があがる
* 新規実装カードなどがあるスクショを認識させた場合 `csv2report.py` ではレアリティ認識できないので、分類「その他」として出力されるので計算結果を自分で修正する必要がある
* スクショをJPEGに変換しても認識する模様

# 制限
* 【重要】全ての機種のスクショの認識に対応しているわけではない
* QPカンスト時にフォウ君を自動売却設定しているスクショではレアリティを誤認識する
* フレンドポイントの10連未満の召喚数のスクショ認識には対応していない
* 10連画像と11連画像の切り替えは自動認識ではないので--num で指定して別々に実行する必要あ
* ガチャ排出コマンドコードの新規実装には自動対応されない
