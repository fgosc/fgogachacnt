#!/usr/bin/env python3
## スクショ集計したCSVから報告書式に変換
import csv
import sys
import argparse
import fgogachacnt

num_servant_0star = 0
num_servant_1star = 0
num_servant_2star = 0
num_servant_3star = 0
num_servant_4star = 0

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

num_ccode_1star = 0
num_ccode_2star = 0

num_summon = 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', nargs='?', type=argparse.FileType(),
                        default=sys.stdin)
    args = parser.parse_args()


    with args.infile as f:
        reader = csv.DictReader(f)
        l = [row for row in reader]

    for i, item in enumerate(l[0].keys()):
        if item == "召喚数":
            num_summon = l[0]['召喚数']
        if item in fgogachacnt.servant_0star:
            num_servant_0star = num_servant_0star + int(l[0][item])
        if item in fgogachacnt.servant_1star:
            num_servant_1star = num_servant_1star + int(l[0][item])
        if item in fgogachacnt.servant_2star:
            num_servant_2star = num_servant_2star + int(l[0][item])
        if item in fgogachacnt.servant_3star:
            num_servant_3star = num_servant_3star + int(l[0][item])
        if item in fgogachacnt.servant_4star:
            num_servant_4star = num_servant_4star + int(l[0][item])

        if item in fgogachacnt.exp_1star:
            num_exp_1star = num_exp_1star + int(l[0][item])
        if item in fgogachacnt.exp_2star:
            num_exp_2star = num_exp_2star + int(l[0][item])
        if item in fgogachacnt.exp_3star:
            num_exp_3star = num_exp_3star + int(l[0][item])
        if item in fgogachacnt.exp_4star:
            num_exp_4star = num_exp_4star + int(l[0][item])
        if item in fgogachacnt.exp_5star:
            num_exp_5star = num_exp_5star + int(l[0][item])

        if item in fgogachacnt.status_1star:
            num_status_1star = num_status_1star + int(l[0][item])
        if item in fgogachacnt.status_2star:
            num_status_2star = num_status_2star + int(l[0][item])
        if item in fgogachacnt.status_3star:
            num_status_3star = num_status_3star + int(l[0][item])

        if item in fgogachacnt.ce_1star:
            num_ce_1star = num_ce_1star + int(l[0][item])
        if item in fgogachacnt.ce_2star:
            num_ce_2star = num_ce_2star + int(l[0][item])
        if item in fgogachacnt.ce_3star:
            num_ce_3star = num_ce_3star + int(l[0][item])

        if item in fgogachacnt.ccode_1star:
            num_ccode_1star = num_ccode_1star + int(l[0][item])
        if item in fgogachacnt.ccode_2star:
            num_ccode_2star = num_ccode_2star + int(l[0][item])


    sum_std = num_servant_0star + num_servant_1star + num_servant_2star \
          + num_servant_3star +num_servant_4star \
            + num_exp_1star + num_exp_2star + num_exp_3star \
            + num_exp_4star + num_exp_5star \
            + num_status_1star + num_status_2star + num_status_3star \
            + num_ce_1star + num_ce_2star + num_ce_3star \
            +num_ccode_1star + num_ccode_2star
    print("【フレンドポイント召喚】", end="")
    print(num_summon, end="回\n")

    print("★0鯖",end="")
    print(num_servant_0star, end="-")
    print("★1鯖",end="")
    print(num_servant_1star, end="-")
    print("★2鯖",end="")
    print(num_servant_2star, end="-")
    print("★3鯖",end="")
    print(num_servant_3star, end="-")
    print("★4鯖",end="")
    print(num_servant_4star)

    print("★1種火",end="")
    print(num_exp_1star, end="-")
    print("★2種火",end="")
    print(num_exp_2star, end="-")
    print("★3種火",end="")
    print(num_exp_3star, end="-")
    print("★4種火",end="")
    print(num_exp_4star, end="-")
    print("★5種火",end="")
    print(num_exp_5star)

    print("★1フォウ",end="")
    print(num_status_1star, end="-")
    print("★2フォウ",end="")
    print(num_status_2star, end="-")
    print("★3フォウ",end="")
    print(num_status_3star)

    print("★1礼装",end="")
    print(num_ce_1star, end="-")
    print("★2礼装",end="")
    print(num_ce_2star, end="-")
    print("★3礼装",end="")
    print(num_ce_3star)

    print("★1コード",end="")
    print(num_ccode_1star, end="-")
    print("★2コード",end="")
    print(num_ccode_2star)

    summon_diff = int(num_summon) - sum_std
    if summon_diff > 0:
        print("その他",end="")
        print(summon_diff)
        
    print("#FGO_FP召喚報告")
