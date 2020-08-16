#!/usr/bin/env python3
#
# ガチャ結果画面のスクショのカードを数え上げのデータアップデート
#
# FGO game data API https://api.atlasacademy.io/docs を使用
# 新鯖や新概念礼装が実装されたときどれぐらいのスピードで追加されるかは不明です
#
#
# ・廃止される★1★2礼装
# ・聖晶石召喚からフレンドポイントに移行される★3礼装
# ・フレンドポイントでもでるようになった★3鯖
#  などの情報は無い(自分が認識している限り)のでブラックリストやホワイトリストの更新はされないので
# 手動で行わないといけない
# 
import requests
from pathlib import Path
import codecs
import csv
import cv2
from tqdm import tqdm

ID_KIKOU_START = 9304760
ID_KIKOU_END = 9305230

Image_dir = Path(__file__).resolve().parent / Path("data/")
Image_dir_ce = Image_dir / Path("ce/")
Image_dir_servant = Image_dir / Path("servant/")
Image_dir_ccode = Image_dir / Path("ccode/")
CE_blacklist_file = Path(__file__).resolve().parent / Path("ce_bl.txt")
Servant_blacklist_file = Path(__file__).resolve().parent / Path("srv_bl.csv")
Servant_output_file = Path(__file__).resolve().parent / Path("hash_srv.csv")
CE_output_file = Path(__file__).resolve().parent / Path("hash_ce.csv")
CE_center_output_file = Path(__file__).resolve().parent / Path("hash_ce_center.csv")
CCode_output_file = Path(__file__).resolve().parent / Path("hash_ccode.csv")
if not Image_dir.is_dir():
    Image_dir.mkdir()
if not Image_dir_ce.is_dir():
    Image_dir_ce.mkdir()
if not Image_dir_servant.is_dir():
    Image_dir_servant.mkdir()
if not Image_dir_ccode.is_dir():
    Image_dir_ccode.mkdir()

url_ce = "https://api.atlasacademy.io/export/JP/nice_equip.json"
url_servant = "https://api.atlasacademy.io/export/JP/nice_servant.json"
url_ccode = "https://api.atlasacademy.io/export/JP/nice_command_code.json"

hasher = cv2.img_hash.PHash_create()

servant_class = {'saber':'剣',
                 'lancer':'槍',
                 'archer':'弓',
                 'rider':'騎',
                 'caster':'術',
                 'assassin':'殺',
                 'berserker':'狂',
                 'ruler':'裁',
                 'avenger':'讐',
                 'alterEgo':'分',
                 'moonCancer':'月',
                 'foreigner':'降'}
    
def compute_hash_inner(img_rgb):
    img = img_rgb[34:104,:]    
##    img = img_rgb[34:86,:]    
    return hasher.compute(img)

def make_ce_data():
    ce_output =[]
    ce_center_output =[]
##    for i in range(5):
    r_get = requests.get(url_ce)

    ce_list = r_get.json()
    with open(CE_blacklist_file, encoding='UTF-8') as f:
        bl_ces = [s.strip() for s in f.readlines()]
    for ce in tqdm(ce_list):
        name = ce["name"]
##        b = name.encode('cp932', "ignore")
##        name_after = b.decode('cp932')
        if ce["atkMax"]-ce["atkBase"]+ce["hpMax"]-ce["hpBase"]==0 \
           and ID_KIKOU_START > ce["id"] < ID_KIKOU_END:
##            print(": exclude")
            continue
##        if ce["name"].startswith("概念礼装EXPカード："):
##            continue
        # ここにファイルから召喚除外礼装を読み込む
        # イベント交換(ドロップ)礼装、マナプリ交換礼装
        if name in bl_ces:
            continue
##        id = ce["id"]
        mylist = list(ce['extraAssets']['faces']['equip'].values())
        url_download = mylist[0]
        tmp = url_download.split('/')
        savefilename = tmp[-1]
        Image_dir_sub = Image_dir_ce / str(ce["rarity"]) 
        Image_file = Image_dir_sub / Path(savefilename)
        if Image_dir_sub.is_dir() == False:
            Image_dir_sub.mkdir()
        if Image_file.is_file() == False:
            response = requests.get(url_download)
            with open(Image_file, 'wb') as saveFile:
                saveFile.write(response.content)
        img_rgb = cv2.imread(str(Image_file))
        hash = compute_hash_inner(img_rgb)
        tmp = [name] + [ce['rarity']] + list(hash[0])
#            print(hash[0][0])
#            print(tmp)
        ce_output.append(tmp)
        if ce["rarity"] <= 3:
            hash_center = hasher.compute(img_rgb[35:77,40:88])
            tmp_center = [name] + [ce['rarity']] + list(hash_center[0])
            ce_center_output.append(tmp_center)
            

    with open(CE_output_file, 'w', encoding="UTF-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerows(ce_output)

    with open(CE_center_output_file, 'w', encoding="UTF-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerows(ce_center_output)

def make_servant_data():
    srv_output =[]

    r_get = requests.get(url_servant)

    seravnt_list = r_get.json()
    with open(Servant_blacklist_file, encoding='UTF-8') as f:

        reader = csv.DictReader(f)
        bl_sarvants = [row for row in reader]

    for servant in tqdm(seravnt_list):
        name = servant["name"]
        if name == "哪吒": # "Windows の cp932 でエラーになる問題
            name = "ナタ" 
        b = name.encode('cp932', "ignore")
        # ここにファイルから召喚除外礼装を読み込む
        # イベント交換(ドロップ)礼装、マナプリ交換礼装
        distribution = False
        for l in bl_sarvants:
            if name == l['name'] and servant['rarity'] == int(l['rarity']) \
               and servant['className'] == l['className']:
                distribution = True
                continue
        if distribution:
            continue

        mylist = list(servant['extraAssets']['faces']['ascension'].values())
        url_download = mylist[0]
        tmp = url_download.split('/')
        savefilename = tmp[-1]
        Image_dir_sub = Image_dir_servant / str(servant["rarity"]) 
        Image_file = Image_dir_sub / Path(savefilename)
        if Image_dir_sub.is_dir() == False:
            Image_dir_sub.mkdir()
        if Image_file.is_file() == False:
            # ファイルがなければデータダウンロード
            response = requests.get(url_download)
            with open(Image_file, 'wb') as saveFile:
                saveFile.write(response.content)
        img_rgb = cv2.imread(str(Image_file))
        name = name + "【"  + servant_class[servant['className']] + "】"
        hash = compute_hash_inner(img_rgb)
        tmp = [name] + [servant['rarity']] + list(hash[0])
#            print(hash[0][0])
#            print(tmp)
        srv_output.append(tmp)
    with open(Servant_output_file, 'w', encoding="UTF-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerows(srv_output)

def make_ccode_data():
    ccode_output =[]
    ccode_center_output =[]
##    for i in range(5):
    r_get = requests.get(url_ccode)

    ccode_list = r_get.json()
##    with open(CCode_blacklist_file, encoding='UTF-8') as f:
##        bl_ccodes = [s.strip() for s in f.readlines()]
    for ccode in tqdm(ccode_list):
        if ccode["rarity"] <= 2:
            name = ccode["name"]
            mylist = list(ccode['extraAssets']['faces']['cc'].values())
            url_download = mylist[0]
            tmp = url_download.split('/')
            savefilename = tmp[-1]
            Image_dir_sub = Image_dir_ccode / str(ccode["rarity"]) 
            Image_file = Image_dir_sub / Path(savefilename)
            if Image_dir_sub.is_dir() == False:
                Image_dir_sub.mkdir()
            if Image_file.is_file() == False:
                response = requests.get(url_download)
                with open(Image_file, 'wb') as saveFile:
                    saveFile.write(response.content)
            img_rgb = cv2.imread(str(Image_file))
            h, w = img_rgb.shape[:2]
            size = 54
            hash = hasher.compute(img_rgb[int(h/2-size/2):int(h/2+size/2),
                                                int(w/2-size/2):int(w/2+size/2)])
            tmp = [name] + [ccode['rarity']] + list(hash[0])
    #            print(hash[0][0])
    #            print(tmp)
            ccode_output.append(tmp)

    with open(CCode_output_file, 'w', encoding="UTF-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerows(ccode_output)


if __name__ == '__main__':
    make_ce_data()
    make_servant_data()
    make_ccode_data()
