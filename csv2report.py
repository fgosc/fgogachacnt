#!/usr/bin/env python3
## スクショ集計したCSVから報告書式に変換
import csv
import sys
import argparse
import fgogachacnt
from pathlib import Path

Servant_file = Path(__file__).resolve().parent / Path("hash_srv.csv")
CE_file = Path(__file__).resolve().parent / Path("hash_ce.csv")
CCode_file = Path(__file__).resolve().parent / Path("hash_ccode.csv")

servant_rarity = {}
ce_rarity = {}
ccode_rarity = {}

def make_rarity():
    """
    CSVからサーヴァントと概念礼装とコマンドコードのレアリティ情報を作成
    """
    for i in range(6):
        servant_rarity[i] = []
        
    with open(Servant_file, encoding='UTF-8') as f:
        reader = csv.reader(f)
        srvs = [row for row in reader]
        for srv in srvs:
            servant_rarity[int(srv[1])] = servant_rarity[int(srv[1])] + [srv[0]]

    for i in range(5):
        ce_rarity[i+1] = []

    with open(CE_file, encoding='UTF-8') as f:
        reader = csv.reader(f)
        ces = [row for row in reader]
        for ce in ces:
            ce_rarity[int(ce[1])] = ce_rarity[int(ce[1])] + [ce[0]]

    for i in range(2):
        ccode_rarity[i+1] = []

    with open(CCode_file, encoding='UTF-8') as f:
        reader = csv.reader(f)
        ccodes = [row for row in reader]
        for ccode in ccodes:
            ccode_rarity[int(ccode[1])] = ccode_rarity[int(ccode[1])] + [ccode[0]]

def make_data(args):
    """
    報告内容を作成
    """
    mode = "fp"
    num_servant_0star = 0
    num_servant_1star = 0
    num_servant_2star = 0
    num_servant_3star = 0
    num_servant_4star = 0
    num_servant_5star = 0

    num_exp_1star = 0
    num_exp_2star = 0
    num_exp_3star = 0
    num_exp_4star = 0
    num_exp_5star = 0

    num_status_1star = 0
    num_status_2star = 0
    num_status_3star = 0

    num_ce_1star = 0
    num_ce_2star = 0
    num_ce_3star = 0
    num_ce_exp_3star = 0
    num_ce_4star = 0
    num_ce_5star = 0

    num_kalesco = 0
    num_nobukatsu = 0
    num_lily = 0
    num_habetrot = 0

    num_ccode_1star = 0
    num_ccode_2star = 0

    num_summon = 0
    result = ""
    
    with args.infile as f:
        reader = csv.DictReader(f)
        l = [row for row in reader]

    if l[2]['召喚数'] == "11":
        mode = "stone"

    for i, item in enumerate(l[0].keys()):
        if item == "召喚数":
            num_summon = l[0]['召喚数']

        if mode == "stone":
            if item in servant_rarity[3]:
                num_servant_3star = num_servant_3star + int(l[0][item])
            elif item in servant_rarity[4]:
                num_servant_4star = num_servant_4star + int(l[0][item])
            elif item in servant_rarity[5]:
                num_servant_5star = num_servant_5star + int(l[0][item])
            elif item in ce_rarity[3]:
                num_ce_3star = num_ce_3star + int(l[0][item])
            elif item in ce_rarity[4]:
                num_ce_4star = num_ce_4star + int(l[0][item])
            elif item in ce_rarity[5]:
                num_ce_5star = num_ce_5star + int(l[0][item])

            if item == "カレイドスコープ":
                num_kalesco = num_kalesco + int(l[0][item])
            continue

        if item in servant_rarity[0]:
            num_servant_0star = num_servant_0star + int(l[0][item])
        elif item in servant_rarity[1]:
            num_servant_1star = num_servant_1star + int(l[0][item])
        elif item in servant_rarity[2]:
            num_servant_2star = num_servant_2star + int(l[0][item])
        elif item in servant_rarity[3]:
            num_servant_3star = num_servant_3star + int(l[0][item])
        elif item in servant_rarity[4]:
            num_servant_4star = num_servant_4star + int(l[0][item])

        elif item in fgogachacnt.exp_1star:
            num_exp_1star = num_exp_1star + int(l[0][item])
        elif item in fgogachacnt.exp_2star:
            num_exp_2star = num_exp_2star + int(l[0][item])
        elif item in fgogachacnt.exp_3star:
            num_exp_3star = num_exp_3star + int(l[0][item])
        elif item in fgogachacnt.exp_4star:
            num_exp_4star = num_exp_4star + int(l[0][item])
        elif item in fgogachacnt.exp_5star:
            num_exp_5star = num_exp_5star + int(l[0][item])

        elif item in fgogachacnt.status_1star:
            num_status_1star = num_status_1star + int(l[0][item])
        elif item in fgogachacnt.status_2star:
            num_status_2star = num_status_2star + int(l[0][item])
        elif item in fgogachacnt.status_3star:
            num_status_3star = num_status_3star + int(l[0][item])

        elif item in ce_rarity[1]:
            num_ce_1star = num_ce_1star + int(l[0][item])
        elif item in ce_rarity[2]:
            num_ce_2star = num_ce_2star + int(l[0][item])
        elif item.startswith("概念礼装EXPカード") and item in ce_rarity[3]:
            num_ce_exp_3star = num_ce_exp_3star + int(l[0][item])
        elif item in ce_rarity[3]:
            num_ce_3star = num_ce_3star + int(l[0][item])
        elif item in ce_rarity[4]:
            num_ce_4star = num_ce_4star + int(l[0][item])

        elif item in ccode_rarity[1]:
            num_ccode_1star = num_ccode_1star + int(l[0][item])
        elif item in ccode_rarity[2]:
            num_ccode_2star = num_ccode_2star + int(l[0][item])

        if item == "織田信勝【弓】":
            num_nobukatsu = num_nobukatsu + int(l[0][item])
        if item == "アルトリア・ペンドラゴン〔リリィ〕【剣】":
            num_lily = num_lily + int(l[0][item])
        if item == "ハベトロット【騎】":
            num_habetrot = num_habetrot + int(l[0][item])
        continue

    if mode == "stone":
        sum_std =  num_servant_3star +num_servant_4star  +num_servant_5star \
                + num_ce_3star + num_ce_4star + num_ce_5star

        result = """【聖晶石召喚】{}回
★3鯖{}-★4鯖{}-★5鯖1{}
★3礼装{}-★4礼装{}-★5礼装{}(うちカレスコ{})
""".format(num_summon,
           num_servant_3star, num_servant_4star, num_servant_5star,
           num_ce_3star,num_ce_4star,num_ce_5star,
           num_kalesco)

        summon_diff = int(num_summon) - sum_std
        if summon_diff > 0:
            result = result + "その他" + str(summon_diff) + "\n"

        result = result + "#FGO_聖晶石召喚報告"

        return result
    
    sum_std = num_servant_0star + num_servant_1star + num_servant_2star \
          + num_servant_3star +num_servant_4star \
            + num_exp_1star + num_exp_2star + num_exp_3star \
            + num_exp_4star + num_exp_5star \
            + num_status_1star + num_status_2star + num_status_3star \
            + num_ce_1star + num_ce_2star + num_ce_3star + num_ce_exp_3star + num_ce_4star \
            +num_ccode_1star + num_ccode_2star

    if args.yamataikoku:
        result = """【フレンドポイント召喚】{}回
鯖: ★0_{}-★1_{}(信勝{})-★2_{}-★3_{}-★4_{}(リリィ{},ハベ{})
種火: ★1_{}-★2_{}-★3_{}-★4_{}-★5_{}
フォウ: ★1_{}-★2_{}-★3_{}
礼装: ★1_{}-★2_{}-★3_{}-★3EXP_{}-★4EXP_{}
コード: ★1_{}-★2_{}
""".format(num_summon,
            num_servant_0star, num_servant_1star, num_nobukatsu, num_servant_2star, num_servant_3star, num_servant_4star, num_lily, num_habetrot,
            num_exp_1star, num_exp_2star, num_exp_3star, num_exp_4star, num_exp_5star,
            num_status_1star, num_status_2star, num_status_3star,
            num_ce_1star, num_ce_2star, num_ce_3star, num_ce_exp_3star, num_ce_4star,
            num_ccode_1star, num_ccode_2star)
    elif num_ce_exp_3star + num_ce_4star > 0:
        result = """【フレンドポイント召喚】{}回
鯖: ★0_{}-★1_{}-★2_{}-★3_{}-★4_{}(リリィ{},ハベ{})
種火: ★1_{}-★2_{}-★3_{}-★4_{}-★5_{}
フォウ: ★1_{}-★2_{}-★3_{}
礼装: ★1_{}-★2_{}-★3_{}-★3EXP_{}-★4EXP_{}
コード: ★1_{}-★2_{}
""".format(num_summon,
            num_servant_0star, num_servant_1star, num_servant_2star, num_servant_3star, num_servant_4star, num_lily, num_habetrot,
            num_exp_1star, num_exp_2star, num_exp_3star, num_exp_4star, num_exp_5star,
            num_status_1star, num_status_2star, num_status_3star,
            num_ce_1star, num_ce_2star, num_ce_3star, num_ce_exp_3star, num_ce_4star,
            num_ccode_1star, num_ccode_2star)
    else:
        result = """【フレンドポイント召喚】{}回
鯖: ★0_{}-★1_{}-★2_{}-★3_{}-★4_{}(リリィ{},ハベ{})
種火: ★1_{}-★2_{}-★3_{}-★4_{}-★5_{}
フォウ: ★1_{}-★2_{}-★3_{}
礼装: ★1_{}-★2_{}-★3_{}
コード: ★1_{}-★2_{}
""".format(num_summon,
            num_servant_0star, num_servant_1star, num_servant_2star, num_servant_3star, num_servant_4star, num_lily, num_habetrot,
            num_exp_1star, num_exp_2star, num_exp_3star, num_exp_4star, num_exp_5star,
            num_status_1star, num_status_2star, num_status_3star,
            num_ce_1star, num_ce_2star, num_ce_3star,
            num_ccode_1star, num_ccode_2star)

    summon_diff = int(num_summon) - sum_std
    if summon_diff > 0:
        result = result + "その他" + str(summon_diff) + "\n"

    result = result + "#FGO_FP召喚報告"

    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--yamataikoku', action='store_true',
                        help='邪馬台国限定FP召喚')
    parser.add_argument('infile', nargs='?', type=argparse.FileType(),
                        default=sys.stdin)
    args = parser.parse_args()
    make_rarity()
    result = make_data(args)
    print(result)

