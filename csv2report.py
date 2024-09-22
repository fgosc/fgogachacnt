#!/usr/bin/env python3
"""スクショ集計したCSVから報告書式に変換

"""
import csv
import sys
import argparse
import fgogachacnt
from pathlib import Path
import dataclasses
import logging
import contextlib

logger = logging.getLogger(__name__)

Servant_file = Path(__file__).resolve().parent / Path("hash_srv.csv")
CE_file = Path(__file__).resolve().parent / Path("hash_ce.csv")
CCode_file = Path(__file__).resolve().parent / Path("hash_ccode.csv")

servant_rarity = {}
ce_rarity = {}
ccode_rarity = {}


@dataclasses.dataclass
class FpSummon():
    servant_0star: int = 0
    servant_1star: int = 0
    servant_2star: int = 0
    servant_3star: int = 0
    servant_4star: int = 0

    exp_1star: int = 0
    exp_2star: int = 0
    exp_3star: int = 0
    exp_4star: int = 0
    exp_5star: int = 0

    status_1star: int = 0
    status_2star: int = 0
    status_3star: int = 0

    ce_1star: int = 0
    ce_2star: int = 0
    ce_3star: int = 0
    ce_exp_3star: int = 0
    ce_exp_4star: int = 0

    nobukatsu: int = 0
    anning: int = 0
    lily: int = 0
    habetrot: int = 0
    xavio: int = 0
    xaviko: int = 0

    ccode_1star: int = 0
    ccode_2star: int = 0

    sum_summon: int = 0

    def format(self):
        result = """【フレンドポイント召喚】{}回
鯖: ★0_{}-★1_{}-★2_{}-★3_{}-★4_{}(リリィ{},ハベ{},ザビ男{},ザビ子{})
種火: ★1_{}-★2_{}-★3_{}-★4_{}-★5_{}
フォウ: ★1_{}-★2_{}-★3_{}
礼装: ★1_{}-★2_{}-★3_{}
コード: ★1_{}-★2_{}
""".format(self.sum_summon,
            self.servant_0star, self.servant_1star, self.servant_2star, self.servant_3star, self.servant_4star,
            self.lily, self.habetrot, self.xavio, self.xaviko,
            self.exp_1star, self.exp_2star, self.exp_3star, self.exp_4star, self.exp_5star,
            self.status_1star, self.status_2star, self.status_3star,
            self.ce_1star, self.ce_2star, self.ce_3star,
            self.ccode_1star, self.ccode_2star)

        num_summon = self.servant_0star + self.servant_1star + self.servant_2star \
                     + self.servant_3star + self.servant_4star \
                     + self.exp_1star + self.exp_2star + self.exp_3star \
                     + self.exp_4star + self.exp_5star \
                     + self.status_1star + self.status_2star + self.status_3star \
                     + self.ce_1star + self.ce_2star + self.ce_3star \
                     + self.ccode_1star + self.ccode_2star
        summon_diff = self.sum_summon - num_summon
        if summon_diff > 0:
            result += "その他" + str(summon_diff) + "\n"

        result += "#FGO_FP召喚報告\n"

        result += """
【まんわかFP召喚】{}回
鯖: ★0_{}-★1_{}(アニング{})-★2_{}-★3_{}-★4_{}(リリィ{},ハベ{},ザビ男{},ザビ子{})
種火: ★1_{}-★2_{}-★3_{}-★4_{}-★5_{}
フォウ: ★1_{}-★2_{}-★3_{}
礼装: ★1_{}-★2_{}-★3_{}-★3EXP_{}-★4EXP_{}
コード: ★1_{}-★2_{}
""".format(self.sum_summon,
            self.servant_0star, self.servant_1star, self.anning, self.servant_2star, self.servant_3star, self.servant_4star,
            self.lily, self.habetrot, self.xavio, self.xaviko,
            self.exp_1star, self.exp_2star, self.exp_3star, self.exp_4star, self.exp_5star,
            self.status_1star, self.status_2star, self.status_3star,
            self.ce_1star, self.ce_2star, self.ce_3star, self.ce_exp_3star, self.ce_exp_4star,
            self.ccode_1star, self.ccode_2star)

        num_summon = self.servant_0star + self.servant_1star + self.servant_2star \
                     + self.servant_3star + self.servant_4star \
                     + self.exp_1star + self.exp_2star + self.exp_3star \
                     + self.exp_4star + self.exp_5star \
                     + self.status_1star + self.status_2star + self.status_3star \
                     + self.ce_1star + self.ce_2star + self.ce_3star + self.ce_exp_3star + self.ce_exp_4star \
                     + self.ccode_1star + self.ccode_2star
        summon_diff = self.sum_summon - num_summon
        if summon_diff > 0:
            result += "その他" + str(summon_diff) + "\n"

        result += "#FGO_FP召喚報告\n"

        result += """
【邪馬台国FP召喚】{}回
鯖: ★0_{}-★1_{}(信勝{})-★2_{}-★3_{}-★4_{}(リリィ{},ハベ{},ザビ男{},ザビ子{})
種火: ★1_{}-★2_{}-★3_{}-★4_{}-★5_{}
フォウ: ★1_{}-★2_{}-★3_{}
礼装: ★1_{}-★2_{}-★3_{}-★3EXP_{}-★4EXP_{}
コード: ★1_{}-★2_{}
""".format(self.sum_summon,
            self.servant_0star, self.servant_1star, self.nobukatsu, self.servant_2star, self.servant_3star, self.servant_4star,
            self.lily, self.habetrot, self.xavio, self.xaviko,
            self.exp_1star, self.exp_2star, self.exp_3star, self.exp_4star, self.exp_5star,
            self.status_1star, self.status_2star, self.status_3star,
            self.ce_1star, self.ce_2star, self.ce_3star, self.ce_exp_3star, self.ce_exp_4star,
            self.ccode_1star, self.ccode_2star)

        num_summon = self.servant_0star + self.servant_1star + self.servant_2star \
                     + self.servant_3star + self.servant_4star \
                     + self.exp_1star + self.exp_2star + self.exp_3star \
                     + self.exp_4star + self.exp_5star \
                     + self.status_1star + self.status_2star + self.status_3star \
                     + self.ce_1star + self.ce_2star + self.ce_3star + self.ce_exp_3star + self.ce_exp_4star \
                     + self.ccode_1star + self.ccode_2star
        summon_diff = self.sum_summon - num_summon
        if summon_diff > 0:
            result += "その他" + str(summon_diff) + "\n"

        result += "#FGO_FP召喚報告\n"

        return result


@dataclasses.dataclass
class SqSummon:
    servant_3star: int = 0
    servant_4star: int = 0
    servant_5star: int = 0

    ce_3star: int = 0
    ce_4star: int = 0
    ce_5star: int = 0

    kalesco: int = 0

    sum_summon: int = 0

    def format(self):
        result = """
【聖晶石召喚】{}回
★3鯖{}-★4鯖{}-★5鯖{}
★3礼装{}-★4礼装{}-★5礼装{}(うちカレスコ{})
""".format(self.sum_summon,
           self.servant_3star, self.servant_4star, self.servant_5star,
           self.ce_3star, self.ce_4star, self.ce_5star,
           self.kalesco)

        num_summon = self.servant_3star + self.servant_3star + self.servant_5star \
                     + self.ce_3star + self.ce_4star + self.ce_5star
        summon_diff = self.sum_summon - num_summon
        if summon_diff > 0:
            result += "その他" + str(summon_diff) + "\n"

        result += "#FGO_聖晶石召喚報告\n"
        return result


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
    fp_summon = FpSummon()
    sq_summon = SqSummon()

    f = csv.DictReader(args.infile)

    for row in f:
        if row['filename'] == "合計":
            continue
        if row['聖晶石召喚'] == "1":
            logger.debug("sq summon")
            for item in row.keys():
                if row[item] == "":
                    continue
                if item == "召喚数":
                    sq_summon.sum_summon += int(row[item])
                if item in servant_rarity[3]:
                    sq_summon.servant_3star += int(row[item])
                elif item in servant_rarity[4]:
                    sq_summon.servant_4star += int(row[item])
                elif item in servant_rarity[5]:
                    sq_summon.servant_5star += int(row[item])
                elif item in ce_rarity[3]:
                    sq_summon.ce_3star += int(row[item])
                elif item in ce_rarity[4]:
                    sq_summon.ce_4star += int(row[item])
                elif item in ce_rarity[5]:
                    sq_summon.ce_5star += int(row[item])

                if item == "カレイドスコープ":
                    sq_summon.kalesco += int(row[item])
        else:
            logger.debug("fp summon")
            for item in row.keys():
                if row[item] == "":
                    continue
                if item == "召喚数":
                    fp_summon.sum_summon += int(row[item])
                if item in servant_rarity[0]:
                    fp_summon.servant_0star += int(row[item])
                elif item in servant_rarity[1]:
                    fp_summon.servant_1star += int(row[item])
                elif item in servant_rarity[2]:
                    fp_summon.servant_2star += int(row[item])
                elif item in servant_rarity[3]:
                    fp_summon.servant_3star += int(row[item])
                elif item in servant_rarity[4]:
                    fp_summon.servant_4star += int(row[item])

                elif item in fgogachacnt.exp_1star:
                    fp_summon.exp_1star += int(row[item])
                elif item in fgogachacnt.exp_2star:
                    fp_summon.exp_2star += int(row[item])
                elif item in fgogachacnt.exp_3star:
                    fp_summon.exp_3star += int(row[item])
                elif item in fgogachacnt.exp_4star:
                    fp_summon.exp_4star += int(row[item])
                elif item in fgogachacnt.exp_5star:
                    fp_summon.exp_5star += int(row[item])

                elif item in fgogachacnt.status_1star:
                    fp_summon.status_1star += int(row[item])
                elif item in fgogachacnt.status_2star:
                    fp_summon.status_2star += int(row[item])
                elif item in fgogachacnt.status_3star:
                    fp_summon.status_3star += int(row[item])

                elif item in ce_rarity[1]:
                    fp_summon.ce_1star += int(row[item])
                elif item in ce_rarity[2]:
                    fp_summon.ce_2star += int(row[item])
                elif item.startswith("概念礼装EXPカード") and item in ce_rarity[3]:
                    fp_summon.ce_exp_3star += int(row[item])
                elif item in ce_rarity[3]:
                    fp_summon.ce_3star += int(row[item])
                elif item.startswith("概念礼装EXPカード") and item in ce_rarity[4]:
                    fp_summon.ce_exp_4star += int(row[item])

                elif item in ccode_rarity[1]:
                    fp_summon.ccode_1star += int(row[item])
                elif item in ccode_rarity[2]:
                    fp_summon.ccode_2star += int(row[item])
                else:
                    if item not in ["filename", "召喚数"]:
                        logger.warning("その他のアイテムを検知: %s", item)

                if item == "織田信勝【弓】":
                    fp_summon.nobukatsu += int(row[item])
                if item == "メアリー・アニング【槍】":
                    fp_summon.anning += int(row[item])
                if item == "アルトリア・ペンドラゴン〔リリィ〕【剣】":
                    fp_summon.lily += int(row[item])
                if item == "ハベトロット【騎】":
                    fp_summon.habetrot += int(row[item])
                if item == "ザビ男【月】":
                    fp_summon.xavio += int(row[item])
                if item == "ザビ子【月】":
                    fp_summon.xaviko += int(row[item])

    return fp_summon.format() + sq_summon.format()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', nargs='?', type=argparse.FileType(),
                        default=sys.stdin)
    parser.add_argument(
                    '--loglevel', '-l',
                    choices=('warning', 'debug', 'info'),
                    default='info'
                    )
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format='%(name)s <%(filename)s-L%(lineno)s> [%(levelname)s] %(message)s',
    )
    logger.setLevel(args.loglevel.upper())

    make_rarity()
    result = make_data(args)
    print(result)
