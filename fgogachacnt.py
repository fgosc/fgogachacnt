#!/usr/bin/env python3
#
# Fate/Grand Order のガチャ結果画面のスクショのカードを数え上げます
#

import argparse
from pathlib import Path
from collections import Counter
import csv
import sys
import time
import logging

import cv2
import numpy as np
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

progname = "FGOガチャカウント"
version = "0.0.2"

Item_dir = Path(__file__).resolve().parent / Path("item/")
Servant_dir = Path(__file__).resolve().parent / Path("item/servant/")
CE_dir = Path(__file__).resolve().parent / Path("item/ce/")
CCode_dir = Path(__file__).resolve().parent / Path("item/ccode/")
train_card = Path(__file__).resolve().parent / Path("card.xml")  # カード下部認識用
train_rarity = Path(__file__).resolve().parent / Path("rarity.xml")  # カード下部認識用
Servant_dist_file = Path(__file__).resolve().parent / Path("hash_srv.csv")
CE_dist_file = Path(__file__).resolve().parent / Path("hash_ce.csv")
CE_center_dist_file = Path(__file__).resolve().parent / Path("hash_ce_center.csv")
CCode_dist_file = Path(__file__).resolve().parent / Path("hash_ccode.csv")
FP_34Servant_wl = Path(__file__).resolve().parent / Path("fp_34srv_wl.txt")
FP_12CE_bl = Path(__file__).resolve().parent / Path("fp_12ce_bl.txt")
FP_3CE_wl = Path(__file__).resolve().parent / Path("fp_3ce_wl.txt")
hasher = cv2.img_hash.PHash_create()
tmplate_sq = Path(__file__).resolve().parent / Path("data/misc/saint_quarts.jpg")


exp_1star = ['全種火', '剣種火', '槍種火', '弓種火',
             '騎種火', '術種火', '殺種火', '狂種火']
exp_2star = ['全灯火', '剣灯火', '槍灯火', '弓灯火',
             '騎灯火', '術灯火', '殺灯火', '狂灯火']
exp_3star = ['全大火', '剣大火', '槍大火', '弓大火',
             '騎大火', '術大火', '殺大火', '狂大火']
exp_4star = ['全猛火', '剣猛火', '槍猛火', '弓猛火',
             '騎猛火', '術猛火', '殺猛火', '狂猛火']
exp_5star = ['全業火', '剣業火', '槍業火', '弓業火',
             '騎業火', '術業火', '殺業火', '狂業火']
status_1star = ['全★1ATK', '剣★1ATK', '槍★1ATK', '弓★1ATK',
                '騎★1ATK', '術★1ATK', '殺★1ATK', '狂★1ATK',
                '全★1HP', '剣★1HP', '槍★1HP', '弓★1HP',
                '騎★1HP', '術★1HP', '殺★1HP', '狂★1HP']
status_2star = ['全★2ATK', '剣★2ATK', '槍★2ATK', '弓★2ATK',
                '騎★2ATK', '術★2ATK', '殺★2ATK', '狂★2ATK',
                '全★2HP', '剣★2HP', '槍★2HP', '弓★2HP',
                '騎★2HP', '術★2HP', '殺★2HP', '狂★2HP']
status_3star = ['全★3ATK', '剣★3ATK', '槍★3ATK', '弓★3ATK',
                '騎★3ATK', '術★3ATK', '殺★3ATK', '狂★3ATK',
                '全★3HP', '剣★3HP', '槍★3HP', '弓★3HP',
                '騎★3HP', '術★3HP', '殺★3HP', '狂★3HP']
kalesco = ['カレイドスコープ']

std_item = []

std_item_stone = kalesco

dist_local_servant = {
}

dist_local_ce = {
}
dist_local_ce_center = {
}

dist_servant = {
}
dist_ce = {
    }
dist_ce_center = {
    }
dist_ccode = {
    }
dist_exp = {
    '全種火': np.array([[133, 228, 89, 249, 154, 156, 190, 166]], dtype='uint8'),
    '剣種火': np.array([[161, 102, 249, 243, 182, 190, 186, 38]], dtype='uint8'),
    '弓種火': np.array([[161, 102, 249, 243, 182, 190, 186, 38]], dtype='uint8'),
    '槍種火': np.array([[161, 102, 249, 243, 182, 190, 186, 38]], dtype='uint8'),
    '殺種火': np.array([[161, 102, 249, 243, 190, 190, 186, 38]], dtype='uint8'),
    '騎種火': np.array([[161, 102, 249, 243, 182, 190, 186, 38]], dtype='uint8'),
    '術種火': np.array([[171, 102, 249, 243, 190, 190, 250, 38]], dtype='uint8'),
    '狂種火': np.array([[161, 102, 121, 243, 158, 190, 186, 38]], dtype='uint8'),
    '全灯火': np.array([[133, 132, 234, 99, 115, 190, 222, 123]], dtype='uint8'),
    '剣灯火': np.array([[153, 228, 222, 123, 245, 190, 220, 123]], dtype='uint8'),
    '弓灯火': np.array([[153, 228, 222, 123, 245, 190, 220, 123]], dtype='uint8'),
    '槍灯火': np.array([[153, 228, 222, 123, 117, 190, 222, 59]], dtype='uint8'),
    '騎灯火': np.array([[201, 228, 222, 123, 117, 190, 222, 59]], dtype='uint8'),
    '術灯火': np.array([[153, 228, 222, 123, 245, 190, 220, 123]], dtype='uint8'),
    '殺灯火': np.array([[153, 228, 222, 123, 245, 190, 220, 123]], dtype='uint8'),
    '狂灯火': np.array([[153, 228, 222, 115, 245, 190, 156, 123]], dtype='uint8'),
    '全大火': np.array([[103, 100, 224, 75, 217, 158, 54, 233]], dtype='uint8'),
    '剣大火': np.array([[51, 37, 122, 105, 205, 158, 162, 65]], dtype='uint8'),
    '弓大火': np.array([[51, 37, 122, 233, 205, 158, 162, 65]], dtype='uint8'),
    '槍大火': np.array([[51, 37, 122, 233, 205, 158, 162, 65]], dtype='uint8'),
    '殺大火': np.array([[51, 37, 122, 233, 205, 158, 162, 65]], dtype='uint8'),
    '狂大火': np.array([[115, 37, 122, 233, 205, 158, 162, 65]], dtype='uint8'),
    '術大火': np.array([[51, 37, 122, 233, 205, 158, 162, 65]], dtype='uint8'),
    '騎大火': np.array([[51, 37, 122, 109, 205, 158, 162, 65]], dtype='uint8'),
    '全猛火': np.array([[57, 100, 230, 88, 141, 171, 156, 175]], dtype='uint8'),
    '剣猛火': np.array([[59, 36, 166, 90, 141, 171, 28, 161]], dtype='uint8'),
    '弓猛火': np.array([[115, 36, 166, 90, 157, 171, 60, 161]], dtype='uint8'),
    '槍猛火': np.array([[115, 36, 166, 90, 157, 171, 60, 161]], dtype='uint8'),
    '殺猛火': np.array([[59, 36, 166, 90, 157, 171, 28, 165]], dtype='uint8'),
    '狂猛火': np.array([[115, 36, 38, 90, 157, 171, 52, 165]], dtype='uint8'),
    '術猛火': np.array([[59, 36, 166, 90, 157, 171, 28, 161]], dtype='uint8'),
    '騎猛火': np.array([[59, 36, 166, 90, 157, 171, 28, 161]], dtype='uint8'),
    '全業火': np.array([[35, 102, 34, 106, 90, 239, 126, 186]], dtype='uint8'),
    '剣業火': np.array([[163, 102, 34, 106, 90, 235, 126, 186]], dtype='uint8'),
    '弓業火': np.array([[163, 102, 34, 106, 90, 235, 126, 186]], dtype='uint8'),
    '槍業火': np.array([[163, 102, 34, 106, 90, 235, 126, 186]], dtype='uint8'),
    '殺業火': np.array([[163, 102, 162, 106, 90, 239, 126, 186]], dtype='uint8'),
    '狂業火': np.array([[163, 102, 34, 106, 90, 239, 126, 186]], dtype='uint8'),
    '術業火': np.array([[163, 102, 34, 106, 90, 235, 126, 186]], dtype='uint8'),
    '騎業火': np.array([[163, 102, 34, 106, 90, 239, 126, 186]], dtype='uint8'),
    '全種火変換': np.array([[133, 228, 91, 249, 146, 156, 30, 38]], dtype='uint8'),
    '剣種火変換': np.array([[171, 102, 249, 243, 158, 190, 234, 38]], dtype='uint8'),
    '弓種火変換': np.array([[169, 102, 249, 243, 158, 190, 186, 38]], dtype='uint8'),
    '槍種火変換': np.array([[169, 102, 249, 243, 158, 190, 186, 38]], dtype='uint8'),
    '殺種火変換': np.array([[171, 102, 249, 243, 158, 190, 250, 38]], dtype='uint8'),
    '狂種火変換': np.array([[161, 102, 89, 251, 158, 190, 170, 38]], dtype='uint8'),
    '術種火変換': np.array([[169, 102, 249, 243, 158, 190, 186, 38]], dtype='uint8'),
    '騎種火変換': np.array([[169, 102, 249, 243, 158, 190, 186, 38]], dtype='uint8'),
    '全灯火変換': np.array([[133, 132, 235, 99, 83, 190, 222, 123]], dtype='uint8'),
    '剣灯火変換': np.array([[153, 228, 222, 123, 117, 190, 222, 123]], dtype='uint8'),
    '弓灯火変換': np.array([[201, 228, 222, 123, 117, 191, 222, 59]], dtype='uint8'),
    '槍灯火変換': np.array([[201, 228, 222, 123, 117, 190, 222, 59]], dtype='uint8'),
    '殺灯火変換': np.array([[153, 228, 222, 115, 245, 190, 156, 123]], dtype='uint8'),
    '狂灯火変換': np.array([[153, 228, 222, 123, 245, 190, 156, 123]], dtype='uint8'),
    '術灯火変換': np.array([[153, 228, 222, 123, 117, 190, 222, 123]], dtype='uint8'),
    '騎灯火変換': np.array([[201, 228, 222, 123, 117, 191, 222, 59]], dtype='uint8'),
    '全大火変換': np.array([[103, 100, 225, 75, 217, 158, 55, 233]], dtype='uint8'),
    '剣大火変換': np.array([[51, 37, 122, 105, 205, 158, 162, 65]], dtype='uint8'),
    '弓大火変換': np.array([[115, 37, 122, 233, 205, 158, 162, 193]], dtype='uint8'),
    '槍大火変換': np.array([[51, 37, 122, 233, 205, 158, 162, 65]], dtype='uint8'),
    '殺大火変換': np.array([[59, 37, 26, 105, 205, 222, 162, 65]], dtype='uint8'),
    '狂大火変換': np.array([[51, 37, 122, 233, 205, 158, 162, 65]], dtype='uint8'),
    '術大火変換': np.array([[59, 37, 26, 109, 205, 158, 162, 65]], dtype='uint8'),
    '騎大火変換': np.array([[51, 37, 122, 105, 205, 158, 162, 65]], dtype='uint8'),
    }
dist_tanebi_class = {
    '全種火': np.array([[217, 11, 58, 211, 14, 212, 208, 45]], dtype='uint8'),
    '剣種火': np.array([[48, 59, 13, 195, 210, 244, 129, 171]], dtype='uint8'),
    '弓種火': np.array([[197, 207, 57, 19, 91, 73, 130, 182]], dtype='uint8'),
    '槍種火': np.array([[197, 199, 79, 12, 152, 240, 100, 243]], dtype='uint8'),
    '殺種火': np.array([[209, 207, 12, 54, 211, 208, 179, 203]], dtype='uint8'),
    '狂種火': np.array([[17, 203, 204, 52, 30, 48, 51, 235]], dtype='uint8'),
    '術種火': np.array([[85, 91, 141, 134, 210, 88, 36, 102]], dtype='uint8'),
    '騎種火': np.array([[113, 155, 205, 76, 92, 198, 195, 227]], dtype='uint8'),
    '全灯火': np.array([[209, 11, 52, 147, 14, 212, 208, 45]], dtype='uint8'),
    '剣灯火': np.array([[49, 59, 15, 195, 208, 180, 197, 171]], dtype='uint8'),
    '弓灯火': np.array([[231, 207, 25, 18, 201, 25, 149, 182]], dtype='uint8'),
    '槍灯火': np.array([[228, 195, 75, 8, 152, 176, 101, 179]], dtype='uint8'),
    '殺灯火': np.array([[211, 203, 12, 50, 211, 210, 177, 203]], dtype='uint8'),
    '狂灯火': np.array([[51, 203, 204, 54, 180, 178, 49, 171]], dtype='uint8'),
    '術灯火': np.array([[125, 27, 139, 134, 243, 88, 36, 230]], dtype='uint8'),
    '騎灯火': np.array([[122, 155, 175, 110, 76, 198, 195, 161]], dtype='uint8'),
    '全大火': np.array([[193, 75, 48, 146, 28, 244, 210, 47]], dtype='uint8'),
    '剣大火': np.array([[49, 51, 73, 195, 219, 244, 203, 175]], dtype='uint8'),
    '弓大火': np.array([[197, 199, 25, 178, 217, 217, 178, 182]], dtype='uint8'),
    '槍大火': np.array([[197, 199, 75, 12, 152, 240, 100, 179]], dtype='uint8'),
    '殺大火': np.array([[209, 207, 12, 54, 211, 208, 179, 171]], dtype='uint8'),
    '狂大火': np.array([[1, 207, 204, 180, 188, 180, 51, 175]], dtype='uint8'),
    '術大火': np.array([[89, 27, 137, 198, 243, 248, 44, 166]], dtype='uint8'),
    '騎大火': np.array([[241, 147, 205, 100, 220, 214, 195, 167]], dtype='uint8'),
    '全猛火': np.array([[209, 75, 16, 210, 30, 212, 208, 47]], dtype='uint8'),
    '剣猛火': np.array([[49, 59, 45, 195, 219, 244, 211, 43]], dtype='uint8'),
    '弓猛火': np.array([[229, 203, 57, 50, 203, 89, 147, 182]], dtype='uint8'),
    '槍猛火': np.array([[193, 131, 77, 26, 152, 240, 229, 242]], dtype='uint8'),
    '殺猛火': np.array([[241, 203, 44, 50, 219, 244, 147, 195]], dtype='uint8'),
    '狂猛火': np.array([[49, 203, 204, 54, 190, 52, 51, 111]], dtype='uint8'),
    '術猛火': np.array([[117, 91, 141, 198, 210, 120, 6, 38]], dtype='uint8'),
    '騎猛火': np.array([[49, 155, 237, 102, 204, 212, 211, 35]], dtype='uint8'),
    '全業火': np.array([[197, 250, 169, 144, 94, 244, 210, 15]], dtype='uint8'),
    '剣業火': np.array([[49, 58, 13, 210, 219, 52, 210, 15]], dtype='uint8'),
    '弓業火': np.array([[197, 250, 137, 48, 219, 61, 146, 182]], dtype='uint8'),
    '槍業火': np.array([[133, 178, 77, 24, 218, 112, 244, 247]], dtype='uint8'),
    '殺業火': np.array([[209, 250, 12, 50, 219, 244, 211, 203]], dtype='uint8'),
    '狂業火': np.array([[1, 202, 204, 52, 222, 52, 51, 15]], dtype='uint8'),
    '術業火': np.array([[69, 186, 141, 134, 211, 120, 6, 102]], dtype='uint8'),
    '騎業火': np.array([[177, 186, 205, 100, 222, 212, 211, 103]], dtype='uint8'),
    '全種火変換': np.array([[84, 171, 186, 145, 30, 214, 209, 5]], dtype='uint8'),
    '剣種火変換': np.array([[117, 58, 14, 193, 210, 246, 139, 85]], dtype='uint8'),
    '弓種火変換': np.array([[68, 174, 58, 17, 95, 90, 129, 150]], dtype='uint8'),
    '槍種火変換': np.array([[84, 175, 78, 13, 24, 242, 225, 213]], dtype='uint8'),
    '殺種火変換': np.array([[80, 138, 44, 37, 211, 210, 163, 209]], dtype='uint8'),
    '狂種火変換': np.array([[81, 203, 206, 52, 30, 50, 49, 7]], dtype='uint8'),
    '術種火変換': np.array([[84, 187, 142, 135, 210, 88, 45, 102]], dtype='uint8'),
    '騎種火変換': np.array([[80, 187, 142, 109, 92, 198, 131, 197]], dtype='uint8'),
    '全灯火変換': np.array([[85, 171, 190, 145, 14, 214, 209, 5]], dtype='uint8'),
    '剣灯火変換': np.array([[48, 58, 46, 203, 210, 214, 133, 5]], dtype='uint8'),
    '弓灯火変換': np.array([[100, 174, 58, 27, 77, 74, 129, 148]], dtype='uint8'),
    '槍灯火変換': np.array([[213, 131, 110, 9, 24, 242, 101, 147]], dtype='uint8'),
    '殺灯火変換': np.array([[81, 138, 46, 53, 211, 210, 177, 213]], dtype='uint8'),
    '狂灯火変換': np.array([[81, 139, 206, 116, 52, 50, 49, 85]], dtype='uint8'),
    '術灯火変換': np.array([[92, 59, 142, 199, 210, 90, 37, 38]], dtype='uint8'),
    '騎灯火変換': np.array([[80, 155, 46, 111, 76, 214, 129, 1]], dtype='uint8'),
    '全大火変換': np.array([[85, 171, 184, 147, 92, 214, 211, 47]], dtype='uint8'),
    '剣大火変換': np.array([[48, 58, 75, 195, 219, 246, 137, 39]], dtype='uint8'),
    '弓大火変換': np.array([[196, 174, 25, 49, 217, 216, 163, 182]], dtype='uint8'),
    '槍大火変換': np.array([[196, 166, 75, 13, 152, 240, 225, 183]], dtype='uint8'),
    '殺大火変換': np.array([[208, 206, 12, 52, 91, 210, 145, 131]], dtype='uint8'),
    '狂大火変換': np.array([[81, 203, 204, 180, 188, 182, 51, 55]], dtype='uint8'),
    '術大火変換': np.array([[93, 27, 139, 198, 243, 120, 37, 38]], dtype='uint8'),
    '騎大火変換': np.array([[81, 187, 206, 100, 220, 214, 131, 167]], dtype='uint8'),
    }
dist_status = {
    '全★1ATK': np.array([[43, 30, 54, 251, 107, 206, 180, 123]], dtype='uint8'),
    '剣★1ATK': np.array([[161, 62, 54, 251, 105, 206, 172, 123]], dtype='uint8'),
    '弓★1ATK': np.array([[161, 62, 54, 251, 105, 206, 172, 123]], dtype='uint8'),
    '槍★1ATK': np.array([[161, 62, 54, 251, 105, 206, 172, 123]], dtype='uint8'),
    '殺★1ATK': np.array([[169, 62, 54, 251, 105, 206, 188, 107]], dtype='uint8'),
    '狂★1ATK': np.array([[33, 62, 38, 243, 105, 206, 172, 123]], dtype='uint8'),
    '術★1ATK': np.array([[33, 62, 38, 243, 105, 206, 172, 123]], dtype='uint8'),
    '騎★1ATK': np.array([[161, 62, 54, 251, 105, 206, 172, 123]], dtype='uint8'),
    '全★2ATK': np.array([[3, 62, 54, 251, 107, 206, 167, 121]], dtype='uint8'),
    '剣★2ATK': np.array([[43, 62, 54, 243, 225, 206, 172, 123]], dtype='uint8'),
    '弓★2ATK': np.array([[43, 62, 54, 243, 225, 206, 174, 123]], dtype='uint8'),
    '槍★2ATK': np.array([[43, 62, 54, 243, 225, 206, 166, 123]], dtype='uint8'),
    '殺★2ATK': np.array([[43, 62, 54, 243, 225, 206, 172, 123]], dtype='uint8'),
    '狂★2ATK': np.array([[43, 62, 54, 243, 225, 206, 172, 123]], dtype='uint8'),
    '術★2ATK': np.array([[43, 62, 54, 243, 225, 206, 172, 123]], dtype='uint8'),
    '騎★2ATK': np.array([[35, 62, 54, 243, 225, 206, 166, 123]], dtype='uint8'),
    '全★3ATK': np.array([[5, 60, 54, 243, 225, 222, 167, 121]], dtype='uint8'),
    '剣★3ATK': np.array([[39, 60, 52, 243, 225, 206, 183, 121]], dtype='uint8'),
    '弓★3ATK': np.array([[39, 60, 52, 243, 225, 206, 175, 121]], dtype='uint8'),
    '槍★3ATK': np.array([[39, 60, 52, 243, 225, 206, 191, 121]], dtype='uint8'),
    '殺★3ATK': np.array([[7, 60, 52, 243, 225, 206, 191, 121]], dtype='uint8'),
    '狂★3ATK': np.array([[43, 62, 54, 243, 225, 206, 172, 123]], dtype='uint8'),
    '術★3ATK': np.array([[39, 60, 52, 243, 225, 206, 175, 121]], dtype='uint8'),
    '騎★3ATK': np.array([[7, 60, 52, 243, 225, 206, 191, 121]], dtype='uint8'),
    '全★1HP': np.array([[193, 135, 238, 215, 119, 204, 245, 247]], dtype='uint8'),
    '剣★1HP': np.array([[193, 181, 206, 214, 117, 78, 117, 231]], dtype='uint8'),
    '弓★1HP': np.array([[193, 181, 206, 214, 117, 78, 245, 231]], dtype='uint8'),
    '槍★1HP': np.array([[193, 181, 206, 214, 117, 78, 117, 231]], dtype='uint8'),
    '殺★1HP': np.array([[193, 181, 206, 214, 117, 78, 117, 231]], dtype='uint8'),
    '狂★1HP': np.array([[193, 181, 206, 214, 117, 78, 117, 231]], dtype='uint8'),
    '術★1HP': np.array([[193, 181, 238, 214, 117, 78, 117, 231]], dtype='uint8'),
    '騎★1HP': np.array([[193, 181, 206, 214, 117, 78, 245, 231]], dtype='uint8'),
    '全★2HP': np.array([[129, 177, 238, 222, 53, 78, 245, 247]], dtype='uint8'),
    '剣★2HP': np.array([[193, 177, 238, 214, 53, 76, 117, 119]], dtype='uint8'),
    '弓★2HP': np.array([[193, 177, 206, 214, 117, 76, 117, 119]], dtype='uint8'),
    '槍★2HP': np.array([[193, 177, 206, 214, 117, 76, 117, 119]], dtype='uint8'),
    '殺★2HP': np.array([[193, 177, 238, 214, 53, 204, 117, 117]], dtype='uint8'),
    '狂★2HP': np.array([[193, 177, 238, 214, 53, 204, 117, 117]], dtype='uint8'),
    '術★2HP': np.array([[193, 177, 206, 214, 117, 76, 117, 119]], dtype='uint8'),
    '騎★2HP': np.array([[129, 177, 206, 214, 117, 76, 85, 119]], dtype='uint8'),
    '全★3HP': np.array([[129, 241, 238, 210, 53, 78, 181, 247]], dtype='uint8'),
    '剣★3HP': np.array([[197, 177, 238, 218, 53, 78, 161, 119]], dtype='uint8'),
    '弓★3HP': np.array([[197, 177, 230, 218, 53, 78, 161, 119]], dtype='uint8'),
    '槍★3HP': np.array([[197, 177, 238, 218, 53, 78, 161, 119]], dtype='uint8'),
    '殺★3HP': np.array([[197, 177, 230, 218, 53, 78, 161, 119]], dtype='uint8'),
    '狂★3HP': np.array([[197, 177, 230, 218, 53, 78, 161, 119]], dtype='uint8'),
    '術★3HP': np.array([[197, 177, 206, 218, 53, 78, 161, 247]], dtype='uint8'),
    '騎★3HP': np.array([[197, 177, 230, 218, 53, 78, 161, 119]], dtype='uint8'),
    '全★1ATK変換': np.array([[3, 120, 7, 248, 239, 206, 244, 79]], dtype='uint8'),
    '剣★1ATK変換': np.array([[3, 248, 7, 248, 239, 206, 252, 79]], dtype='uint8'),
    '弓★1ATK変換': np.array([[3, 120, 7, 248, 239, 206, 252, 79]], dtype='uint8'),
    '槍★1ATK変換': np.array([[3, 120, 7, 248, 239, 206, 252, 15]], dtype='uint8'),
    '殺★1ATK変換': np.array([[3, 120, 7, 248, 239, 206, 252, 15]], dtype='uint8'),
    '狂★1ATK変換': np.array([[3, 248, 7, 248, 239, 206, 252, 79]], dtype='uint8'),
    '術★1ATK変換': np.array([[3, 120, 7, 248, 239, 206, 252, 15]], dtype='uint8'),
    '騎★1ATK変換': np.array([[3, 120, 7, 248, 239, 206, 252, 15]], dtype='uint8'),
    '全★2ATK変換': np.array([[7, 56, 7, 248, 239, 206, 252, 15]], dtype='uint8'),
    '剣★2ATK変換': np.array([[7, 56, 7, 248, 231, 206, 252, 79]], dtype='uint8'),
    '弓★2ATK変換': np.array([[7, 120, 7, 248, 231, 206, 252, 79]], dtype='uint8'),
    '槍★2ATK変換': np.array([[7, 56, 7, 240, 231, 206, 252, 79]], dtype='uint8'),
    '殺★2ATK変換': np.array([[7, 120, 7, 248, 231, 206, 252, 79]], dtype='uint8'),
    '狂★2ATK変換': np.array([[7, 56, 7, 248, 231, 206, 252, 79]], dtype='uint8'),
    '術★2ATK変換': np.array([[7, 56, 7, 240, 231, 206, 252, 79]], dtype='uint8'),
    '騎★2ATK変換': np.array([[7, 56, 7, 240, 231, 206, 252, 79]], dtype='uint8'),
    '全★3ATK変換': np.array([[7, 190, 126, 248, 173, 199, 248, 90]], dtype='uint8'),
    '剣★3ATK変換': np.array([[7, 30, 122, 248, 173, 215, 248, 90]], dtype='uint8'),
    '弓★3ATK変換': np.array([[7, 30, 122, 248, 173, 199, 248, 90]], dtype='uint8'),
    '槍★3ATK変換': np.array([[7, 30, 122, 248, 173, 199, 248, 90]], dtype='uint8'),
    '殺★3ATK変換': np.array([[7, 62, 122, 248, 173, 223, 248, 90]], dtype='uint8'),
    '狂★3ATK変換': np.array([[7, 62, 122, 248, 173, 159, 248, 122]], dtype='uint8'),
    '術★3ATK変換': np.array([[7, 62, 122, 248, 173, 159, 248, 122]], dtype='uint8'),
    '騎★3ATK変換': np.array([[7, 62, 122, 248, 173, 159, 248, 122]], dtype='uint8'),
    '全★1HP変換': np.array([[131, 240, 143, 248, 103, 14, 240, 135]], dtype='uint8'),
    '剣★1HP変換': np.array([[135, 240, 143, 248, 39, 14, 240, 7]], dtype='uint8'),
    '弓★1HP変換': np.array([[135, 240, 143, 248, 39, 14, 240, 7]], dtype='uint8'),
    '槍★1HP変換': np.array([[135, 240, 143, 248, 39, 14, 240, 7]], dtype='uint8'),
    '殺★1HP変換': np.array([[135, 240, 7, 248, 55, 78, 244, 7]], dtype='uint8'),
    '狂★1HP変換': np.array([[135, 240, 15, 248, 55, 14, 240, 7]], dtype='uint8'),
    '術★1HP変換': np.array([[135, 240, 15, 248, 55, 14, 241, 7]], dtype='uint8'),
    '騎★1HP変換': np.array([[135, 240, 15, 248, 39, 14, 240, 7]], dtype='uint8'),
    '全★2HP変換': np.array([[135, 240, 143, 248, 167, 14, 240, 7]], dtype='uint8'),
    '剣★2HP変換': np.array([[135, 240, 143, 248, 53, 14, 245, 7]], dtype='uint8'),
    '弓★2HP変換': np.array([[135, 240, 143, 248, 53, 14, 241, 7]], dtype='uint8'),
    '槍★2HP変換': np.array([[135, 240, 143, 240, 103, 14, 241, 7]], dtype='uint8'),
    '殺★2HP変換': np.array([[7, 147, 250, 248, 173, 15, 248, 242]], dtype='uint8'),
    '狂★2HP変換': np.array([[135, 240, 143, 248, 229, 14, 241, 7]], dtype='uint8'),
    '術★2HP変換': np.array([[135, 240, 143, 248, 229, 14, 241, 7]], dtype='uint8'),
    '騎★2HP変換': np.array([[135, 240, 143, 248, 39, 14, 241, 7]], dtype='uint8'),
    '全★3HP変換': np.array([[7, 151, 250, 248, 165, 15, 248, 242]], dtype='uint8'),
    '剣★3HP変換': np.array([[7, 147, 250, 248, 165, 15, 248, 242]], dtype='uint8'),
    '弓★3HP変換': np.array([[7, 147, 250, 248, 165, 15, 248, 242]], dtype='uint8'),
    '槍★3HP変換': np.array([[7, 147, 250, 248, 173, 15, 248, 242]], dtype='uint8'),
    '殺★3HP変換': np.array([[7, 147, 250, 248, 165, 15, 248, 242]], dtype='uint8'),
    '狂★3HP変換': np.array([[7, 147, 250, 248, 165, 15, 248, 114]], dtype='uint8'),
    '術★3HP変換': np.array([[7, 147, 250, 248, 165, 15, 248, 242]], dtype='uint8'),
    '騎★3HP変換': np.array([[7, 147, 250, 248, 165, 15, 248, 114]], dtype='uint8'),
    }
dist_status_class = {
    '全★1ATK': np.array([[197, 90, 173, 150, 10, 244, 208, 15]], dtype='uint8'),
    '剣★1ATK': np.array([[49, 59, 14, 195, 214, 244, 133, 171]], dtype='uint8'),
    '弓★1ATK': np.array([[230, 207, 24, 82, 159, 217, 128, 182]], dtype='uint8'),
    '槍★1ATK': np.array([[193, 195, 66, 72, 152, 240, 100, 179]], dtype='uint8'),
    '殺★1ATK': np.array([[210, 203, 14, 18, 83, 208, 147, 131]], dtype='uint8'),
    '狂★1ATK': np.array([[19, 203, 204, 86, 62, 176, 51, 179]], dtype='uint8'),
    '術★1ATK': np.array([[89, 91, 158, 134, 242, 208, 36, 230]], dtype='uint8'),
    '騎★1ATK': np.array([[177, 155, 206, 78, 156, 212, 131, 167]], dtype='uint8'),
    '全★2ATK': np.array([[197, 90, 173, 148, 74, 228, 208, 79]], dtype='uint8'),
    '剣★2ATK': np.array([[53, 50, 45, 197, 202, 116, 211, 85]], dtype='uint8'),
    '弓★2ATK': np.array([[229, 82, 169, 20, 203, 73, 210, 214]], dtype='uint8'),
    '槍★2ATK': np.array([[212, 226, 205, 28, 152, 114, 225, 215]], dtype='uint8'),
    '殺★2ATK': np.array([[213, 218, 45, 52, 203, 192, 179, 195]], dtype='uint8'),
    '狂★2ATK': np.array([[21, 202, 205, 52, 234, 52, 51, 85]], dtype='uint8'),
    '術★2ATK': np.array([[85, 90, 141, 134, 194, 88, 46, 103]], dtype='uint8'),
    '騎★2ATK': np.array([[245, 154, 173, 36, 202, 198, 211, 101]], dtype='uint8'),
    '全★3ATK': np.array([[197, 82, 169, 214, 74, 212, 240, 15]], dtype='uint8'),
    '剣★3ATK': np.array([[49, 58, 9, 195, 218, 244, 195, 163]], dtype='uint8'),
    '弓★3ATK': np.array([[229, 202, 57, 82, 218, 217, 182, 182]], dtype='uint8'),
    '槍★3ATK': np.array([[197, 194, 75, 76, 152, 240, 228, 179]], dtype='uint8'),
    '殺★3ATK': np.array([[209, 202, 44, 18, 251, 208, 179, 203]], dtype='uint8'),
    '狂★3ATK': np.array([[21, 202, 205, 52, 234, 52, 51, 85]], dtype='uint8'),
    '術★3ATK': np.array([[125, 90, 139, 198, 242, 240, 44, 230]], dtype='uint8'),
    '騎★3ATK': np.array([[241, 155, 237, 102, 220, 214, 195, 167]], dtype='uint8'),
    '全★1HP': np.array([[197, 90, 237, 146, 90, 236, 210, 45]], dtype='uint8'),
    '剣★1HP': np.array([[53, 18, 45, 203, 211, 44, 211, 109]], dtype='uint8'),
    '弓★1HP': np.array([[229, 82, 41, 54, 219, 9, 146, 180]], dtype='uint8'),
    '槍★1HP': np.array([[197, 194, 205, 28, 152, 120, 245, 235]], dtype='uint8'),
    '殺★1HP': np.array([[213, 218, 45, 54, 211, 232, 147, 201]], dtype='uint8'),
    '狂★1HP': np.array([[37, 202, 205, 54, 210, 60, 179, 109]], dtype='uint8'),
    '術★1HP': np.array([[117, 90, 141, 134, 211, 104, 6, 102]], dtype='uint8'),
    '騎★1HP': np.array([[181, 18, 141, 110, 218, 140, 211, 237]], dtype='uint8'),
    '全★2HP': np.array([[197, 90, 173, 148, 74, 236, 208, 79]], dtype='uint8'),
    '剣★2HP': np.array([[53, 50, 13, 201, 195, 44, 211, 77]], dtype='uint8'),
    '弓★2HP': np.array([[229, 82, 45, 60, 195, 9, 210, 214]], dtype='uint8'),
    '槍★2HP': np.array([[197, 226, 13, 28, 152, 122, 241, 203]], dtype='uint8'),
    '殺★2HP': np.array([[213, 218, 45, 60, 211, 232, 211, 203]], dtype='uint8'),
    '狂★2HP': np.array([[53, 202, 205, 60, 194, 40, 179, 239]], dtype='uint8'),
    '術★2HP': np.array([[229, 90, 141, 134, 195, 104, 246, 100]], dtype='uint8'),
    '騎★2HP': np.array([[181, 82, 141, 108, 200, 140, 211, 205]], dtype='uint8'),
    '全★3HP': np.array([[197, 90, 241, 146, 90, 244, 240, 47]], dtype='uint8'),
    '剣★3HP': np.array([[53, 50, 13, 201, 210, 252, 211, 239]], dtype='uint8'),
    '弓★3HP': np.array([[229, 74, 137, 56, 202, 73, 210, 182]], dtype='uint8'),
    '槍★3HP': np.array([[197, 226, 77, 12, 152, 114, 229, 243]], dtype='uint8'),
    '殺★3HP': np.array([[213, 202, 44, 60, 211, 200, 243, 203]], dtype='uint8'),
    '狂★3HP': np.array([[53, 203, 204, 60, 242, 56, 51, 43]], dtype='uint8'),
    '術★3HP': np.array([[117, 90, 141, 134, 210, 120, 102, 102]], dtype='uint8'),
    '騎★3HP': np.array([[181, 218, 165, 44, 220, 206, 211, 239]], dtype='uint8'),
    '全★1ATK変換': np.array([[3, 120, 7, 248, 239, 206, 244, 79]], dtype='uint8'),
    '剣★1ATK変換': np.array([[3, 248, 7, 248, 239, 206, 252, 79]], dtype='uint8'),
    '弓★1ATK変換': np.array([[3, 120, 7, 248, 239, 206, 252, 79]], dtype='uint8'),
    '槍★1ATK変換': np.array([[3, 120, 7, 248, 239, 206, 252, 15]], dtype='uint8'),
    '殺★1ATK変換': np.array([[3, 120, 7, 248, 239, 206, 252, 15]], dtype='uint8'),
    '狂★1ATK変換': np.array([[3, 248, 7, 248, 239, 206, 252, 79]], dtype='uint8'),
    '術★1ATK変換': np.array([[3, 120, 7, 248, 239, 206, 252, 15]], dtype='uint8'),
    '騎★1ATK変換': np.array([[3, 120, 7, 248, 239, 206, 252, 15]], dtype='uint8'),
    '全★2ATK変換': np.array([[7, 56, 7, 248, 239, 206, 252, 15]], dtype='uint8'),
    '剣★2ATK変換': np.array([[7, 56, 7, 248, 231, 206, 252, 79]], dtype='uint8'),
    '弓★2ATK変換': np.array([[7, 120, 7, 248, 231, 206, 252, 79]], dtype='uint8'),
    '槍★2ATK変換': np.array([[7, 56, 7, 240, 231, 206, 252, 79]], dtype='uint8'),
    '殺★2ATK変換': np.array([[7, 120, 7, 248, 231, 206, 252, 79]], dtype='uint8'),
    '狂★2ATK変換': np.array([[7, 56, 7, 248, 231, 206, 252, 79]], dtype='uint8'),
    '術★2ATK変換': np.array([[7, 56, 7, 240, 231, 206, 252, 79]], dtype='uint8'),
    '騎★2ATK変換': np.array([[7, 56, 7, 240, 231, 206, 252, 79]], dtype='uint8'),
    '全★3ATK変換': np.array([[7, 190, 126, 248, 173, 199, 248, 90]], dtype='uint8'),
    '剣★3ATK変換': np.array([[7, 30, 122, 248, 173, 215, 248, 90]], dtype='uint8'),
    '弓★3ATK変換': np.array([[7, 30, 122, 248, 173, 199, 248, 90]], dtype='uint8'),
    '槍★3ATK変換': np.array([[7, 30, 122, 248, 173, 199, 248, 90]], dtype='uint8'),
    '殺★3ATK変換': np.array([[7, 62, 122, 248, 173, 223, 248, 90]], dtype='uint8'),
    '狂★3ATK変換': np.array([[7, 62, 122, 248, 173, 159, 248, 122]], dtype='uint8'),
    '術★3ATK変換': np.array([[7, 62, 122, 248, 173, 159, 248, 122]], dtype='uint8'),
    '騎★3ATK変換': np.array([[7, 62, 122, 248, 173, 159, 248, 122]], dtype='uint8'),
    '全★1HP変換': np.array([[131, 240, 143, 248, 103, 14, 240, 135]], dtype='uint8'),
    '剣★1HP変換': np.array([[135, 240, 143, 248, 39, 14, 240, 7]], dtype='uint8'),
    '弓★1HP変換': np.array([[135, 240, 143, 248, 39, 14, 240, 7]], dtype='uint8'),
    '槍★1HP変換': np.array([[135, 240, 143, 248, 39, 14, 240, 7]], dtype='uint8'),
    '殺★1HP変換': np.array([[135, 240, 7, 248, 55, 78, 244, 7]], dtype='uint8'),
    '狂★1HP変換': np.array([[135, 240, 15, 248, 55, 14, 240, 7]], dtype='uint8'),
    '術★1HP変換': np.array([[135, 240, 15, 248, 55, 14, 241, 7]], dtype='uint8'),
    '騎★1HP変換': np.array([[135, 240, 15, 248, 39, 14, 240, 7]], dtype='uint8'),
    '全★2HP変換': np.array([[135, 240, 143, 248, 167, 14, 240, 7]], dtype='uint8'),
    '剣★2HP変換': np.array([[135, 240, 143, 248, 53, 14, 245, 7]], dtype='uint8'),
    '弓★2HP変換': np.array([[135, 240, 143, 248, 53, 14, 241, 7]], dtype='uint8'),
    '槍★2HP変換': np.array([[135, 240, 143, 240, 103, 14, 241, 7]], dtype='uint8'),
    '殺★2HP変換': np.array([[7, 147, 250, 248, 173, 15, 248, 242]], dtype='uint8'),
    '狂★2HP変換': np.array([[135, 240, 143, 248, 229, 14, 241, 7]], dtype='uint8'),
    '術★2HP変換': np.array([[135, 240, 143, 248, 229, 14, 241, 7]], dtype='uint8'),
    '騎★2HP変換': np.array([[135, 240, 143, 248, 39, 14, 241, 7]], dtype='uint8'),
    '全★3HP変換': np.array([[7, 151, 250, 248, 165, 15, 248, 242]], dtype='uint8'),
    '剣★3HP変換': np.array([[7, 147, 250, 248, 165, 15, 248, 242]], dtype='uint8'),
    '弓★3HP変換': np.array([[7, 147, 250, 248, 165, 15, 248, 242]], dtype='uint8'),
    '槍★3HP変換': np.array([[7, 147, 250, 248, 173, 15, 248, 242]], dtype='uint8'),
    '殺★3HP変換': np.array([[7, 147, 250, 248, 165, 15, 248, 242]], dtype='uint8'),
    '狂★3HP変換': np.array([[7, 147, 250, 248, 165, 15, 248, 114]], dtype='uint8'),
    '術★3HP変換': np.array([[7, 147, 250, 248, 165, 15, 248, 242]], dtype='uint8'),
    '騎★3HP変換': np.array([[7, 147, 250, 248, 165, 15, 248, 114]], dtype='uint8'),
    }

std_item_dic = {}

std_item_stone_dic = {}
for i in std_item_stone:
    std_item_stone_dic[i] = 0


def imread(filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
    """
    OpenCVのimreadが日本語ファイル名が読めない対策
    """
    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        print(e)
        return None


def has_intersect(a, b):
    """
    二つの矩形の当たり判定
    """
    return max(a[0], b[0]) <= min(a[2], b[2]) \
            and max(a[1], b[1]) <= min(a[3], b[3])


class ScreenShot:
    """
    スクリーンショットを表すクラス
    """
    def __init__(self, img_rgb, svm_card, svm_rarity, card_imgs, args):
        TRAINING_IMG_WIDTH = 968
        self.img_rgb_orig = img_rgb
        self.img_gray_orig = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        self.img_hsv_orig = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2HSV)

        game_screen = self.extract_game_screen(args)
        if args.debug:
            cv2.imwrite('game_screen.png', game_screen)

        _, width_g, _ = game_screen.shape
        wscale = (1.0 * width_g) / TRAINING_IMG_WIDTH
        resizeScale = 1 / wscale

        if resizeScale > 1:
            self.img_rgb = cv2.resize(game_screen, (0, 0), fx=resizeScale, fy=resizeScale, interpolation=cv2.INTER_CUBIC)
            self.img_orig_resize = cv2.resize(self.img_rgb_orig, (0, 0), fx=resizeScale, fy=resizeScale, interpolation=cv2.INTER_CUBIC)
        else:
            self.img_rgb = cv2.resize(game_screen, (0, 0), fx=resizeScale, fy=resizeScale, interpolation=cv2.INTER_AREA)
            self.img_orig_resize = cv2.resize(self.img_rgb_orig, (0, 0), fx=resizeScale, fy=resizeScale, interpolation=cv2.INTER_AREA)

        if args.debug:
            cv2.imwrite('game_screen_resize.png', self.img_rgb)

        self.summon_type()
        self.calc_num_summon(card_imgs)

        self.img_gray = cv2.cvtColor(self.img_rgb, cv2.COLOR_BGR2GRAY)
        item_pts = self.img2points(self.num_summon)
        self.items = []

        for i, pt in enumerate(item_pts):
            item_img_rgb = self.img_rgb[pt[1]: pt[3], pt[0]: pt[2]]
            title_img_rgb = self.img_rgb[pt[3] + 1: pt[3] + 10, pt[0] + 31: pt[0] + 98]
            self.items.append(Item(item_img_rgb, title_img_rgb, svm_card, svm_rarity, args.debug))
            if args.debug:
                cv2.imwrite('item' + str(i) + '.png', item_img_rgb)

        self.itemlist = self.makelist()
        self.allitemdic = dict(Counter(self.itemlist))

    def calc_num_summon(self, card_imgs):
        # カードを引いた数を判別
        pts = []

        # 下部の判定
        # 「続けて(10|11)回召喚」を連打するためタップ跡の影響が置きやすい
        for tmpl in card_imgs:
            h, w = tmpl.shape[:2]
            res = cv2.matchTemplate(self.img_rgb[380:420, :], tmpl, cv2.TM_CCOEFF_NORMED)
            threshold = 0.7
            loc = np.where(res >= threshold)
            for pt in zip(*loc[::-1]):
                # もし座標が衝突しなかったら採用
                flag_intersect = False
                area_a = (pt[0], pt[1], pt[0] + w, pt[1] + h)
                for tmp_pts in pts:
                    if has_intersect(area_a, tmp_pts):
                        flag_intersect = True
                        break
                if not flag_intersect:
                    pts.append(area_a)
            if self.summon_mode == "FP":
                if len(pts) == 4:
                    break
            else:
                if len(pts) == 5:
                    break
        pts.sort()
        # logger.info(pts)
        if len(pts) > 0:
            num_cards = 6 + len(pts)
            # 誤認識をエラー訂正
            if len(pts) > 1:
                x = pts[0][0]
                card_width = 140
                for pt in pts[1:]:
                    num_cards += int((pt[0] - x)/card_width) - 1
                    x = pt[0]
        else:
            for tmpl in card_imgs:
                h, w = tmpl.shape[:2]
                res = cv2.matchTemplate(self.img_rgb[295:320, :], tmpl, cv2.TM_CCOEFF_NORMED)
                threshold = 0.8
                loc = np.where(res >= threshold)
                for pt in zip(*loc[::-1]):
                    # もし座標が衝突しなかったら採用
                    flag_intersect = False
                    area_a = (pt[0], pt[1], pt[0] + w, pt[1] + h)
                    for tmp_pts in pts:
                        if has_intersect(area_a, tmp_pts):
                            flag_intersect = True
                            break
                    if not flag_intersect:
                        pts.append(area_a)
            num_cards = len(pts)
        self.num_summon = num_cards

    def summon_type(self):
        # ガチャの種類を判別
        hight, width = self.img_orig_resize.shape[:2]
        sq_tmpl = cv2.imread(str(tmplate_sq))
        res = cv2.matchTemplate(self.img_orig_resize[0:int(hight*1/3), int(width*1/4):int(width*1/2)],
                                sq_tmpl,
                                cv2.TM_CCOEFF_NORMED)
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(res)
        if maxVal > 0.8:
            self.summon_mode = "SQ"
        else:
            self.summon_mode = "FP"

    def makelist(self):
        """
        アイテムをリスト出力
        """
        itemlist = []
        for i, item in enumerate(self.items):
            name = item.name
            itemlist.append(name)
        return itemlist

    def extract_game_screen(self, args):
        """
        額縁の影響を除去してどのスクショでも同じ画面を切り出す
        """
        height_orig, width_orig = self.img_rgb_orig.shape[:2]
        if width_orig/height_orig > 16.02/9:
            # logger.info("Not 16:9 screen")
            x1, y1, x2, y2 = self.find_notch(self.img_hsv_orig)
            # logger.info("screen: (%d, %d), (%d, %d)", x1, y1, width_orig - x2, height_orig - y2)
            img_rgb = self.img_rgb_orig[y1: height_orig - y2, x1: width_orig - x2]
            height, width = img_rgb.shape[:2]
            cut_x1 = int(width/2 - 892/1080*height)
            cut_x2 = int(width/2 + 892/1080*height)
            cut_y1 = int(118/1080*height)
            cut_y2 = int(1033/1080*height)
        else:
            # logger.debug("16:9 screen")
            # 上下青帯(横を基準に) 2048 → 1906x976
            img_rgb = self.img_rgb_orig
            w_scale = 1906/2048
            cut_x1 = int((width_orig - width_orig*w_scale)/2)
            cut_x2 = width_orig - cut_x1
            cut_y1 = int(height_orig/2 - width_orig*429/2048)
            cut_y2 = int(height_orig/2 + width_orig*547/2048)
        # logger.info(cut_x1)
        # logger.info(cut_x2)
        # logger.info(cut_y1)
        # logger.info(cut_y2)
        gamescreen = img_rgb[cut_y1:cut_y2, cut_x1:cut_x2]

        return gamescreen

    def fitpts(self, pts):
        """
        カード位置を微修正する
        """
        _, bin_img = cv2.threshold(self.img_gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        tmp_pts = []

        cards = ['ce', 'exp_up', 'servant', 'status_up']
        for card in cards:
            template = cv2.imread('data/template/' + card + '.png', 0)
            w, h = template.shape[::-1]
            res = cv2.matchTemplate(bin_img, template, cv2.TM_CCOEFF_NORMED)
            threshold = 0.7
            loc = np.where(res >= threshold)
            for pt in zip(*loc[::-1]):
                new_pt = [pt[0] - 6, pt[1] + h + 3 - 288, pt[0] - 6 + 264, pt[1] + h + 3]
                flag = False
                for pt2 in tmp_pts:
                    if has_intersect(new_pt, pt2):
                        flag = True
                        break
                if flag is False:
                    tmp_pts.append(new_pt)
        if len(tmp_pts) == 11:
            return tmp_pts
        new_pts = []
        for pt1 in pts:
            flag = False
            for pt2 in tmp_pts:
                if has_intersect(pt1, pt2):
                    flag = True
                    break
            if flag is True:
                new_pts.append(pt2)
            else:
                new_pts.append(pt1)
        return new_pts

    def img2points(self, num):
        """
        カードが出現する座標
        """

        if num == 11:
            pts = [(39, 83, 167, 211), (192, 83, 320, 211),
                   (344, 83, 472, 211),
                   (496, 83, 624, 211), (648, 83, 776, 211),
                   (801, 83, 929, 211),
                   (115, 266, 243, 394), (268, 266, 396, 394),
                   (420, 266, 548, 394),
                   (572, 266, 700, 394), (725, 266, 852, 394)]
        elif num == 10:
            pts = [(39, 83, 167, 211), (192, 83, 320, 211),
                   (344, 83, 472, 211),
                   (496, 83, 624, 211), (648, 83, 776, 211),
                   (801, 83, 929, 211),
                   (192, 266, 320, 394), (344, 266, 472, 394),
                   (496, 266, 624, 394), (648, 266, 776, 394)]
        elif num == 9:
            pts = [(39, 83, 167, 211), (192, 83, 320, 211),
                   (344, 83, 472, 211),
                   (496, 83, 624, 211), (648, 83, 776, 211),
                   (801, 83, 929, 211),
                   (268, 266, 396, 394), (420, 266, 548, 394),
                   (572, 266, 700, 394)]
        elif num == 8:
            pts = [(39, 83, 167, 211), (192, 83, 320, 211),
                   (344, 83, 472, 211),
                   (496, 83, 624, 211), (648, 83, 776, 211),
                   (801, 83, 929, 211),
                   (344, 266, 472, 394), (496, 266, 624, 394)]
        elif num == 7:
            pts = [(39, 83, 167, 211), (192, 83, 320, 211),
                   (344, 83, 472, 211),
                   (496, 83, 624, 211), (648, 83, 776, 211),
                   (801, 83, 929, 211),
                   (420, 266, 548, 394)]
        elif num == 6:
            pts = [(39, 174, 167, 302), (192, 174, 320, 302),
                   (344, 174, 472, 302),
                   (496, 174, 624, 302), (648, 174, 776, 302),
                   (801, 174, 929, 302)]
        elif num == 5:
            pts = [(115, 174, 243, 302), (268, 174, 396, 302),
                   (420, 174, 548, 302), (572, 174, 700, 302),
                   (725, 174, 852, 302)]
        elif num == 4:
            pts = [(192, 174, 320, 302), (344, 174, 472, 302),
                   (496, 174, 624, 302), (648, 174, 776, 302)]
        elif num == 3:
            pts = [(268, 174, 396, 302), (420, 174, 548, 302),
                   (572, 174, 700, 302)]
        elif num == 2:
            pts = [(344, 174, 472, 302), (496, 174, 624, 302)]
        elif num == 1:
            pts = [(420, 174, 548, 302)]
        else:
            raise ValueError("カード数認識エラー: " + str(num))
        return pts

    def find_notch(self, img_hsv):
        """
        直線検出で検出されなかったフチ幅を検出
        """
        edge_width = 150

        height, width = img_hsv.shape[:2]
        target_color = 0
        for lx in range(edge_width):
            img_hsv_x = img_hsv[:, lx:lx + 1]
            # ヒストグラムを計算
            hist = cv2.calcHist([img_hsv_x], [0], None, [256], [0, 256])
            # 最小値・最大値・最小値の位置・最大値の位置を取得
            _, maxVal, _, maxLoc = cv2.minMaxLoc(hist)
            if not (maxLoc[1] == target_color and maxVal > height * 0.4):
                break
        for ty in range(edge_width):
            img_hsv_y = img_hsv[ty: ty + 1, :]
            # ヒストグラムを計算
            hist = cv2.calcHist([img_hsv_y], [0], None, [256], [0, 256])
            # 最小値・最大値・最小値の位置・最大値の位置を取得
            _, maxVal, _, maxLoc = cv2.minMaxLoc(hist)
            if not (maxLoc[1] == target_color and maxVal > width * 0.4):
                break
        for rx in range(edge_width):
            img_hsv_x = img_hsv[:, width - rx - 1: width - rx]
            # ヒストグラムを計算
            hist = cv2.calcHist([img_hsv_x], [0], None, [256], [0, 256])
            # 最小値・最大値・最小値の位置・最大値の位置を取得
            _, maxVal, _, maxLoc = cv2.minMaxLoc(hist)
            if not (maxLoc[1] == target_color and maxVal > height * 0.4):
                break
        for by in range(edge_width):
            img_hsv_y = img_hsv[height - by - 1: height - by, :]
            # ヒストグラムを計算
            hist = cv2.calcHist([img_hsv_y], [0], None, [256], [0, 256])
            # 最小値・最大値・最小値の位置・最大値の位置を取得
            _, maxVal, _, maxLoc = cv2.minMaxLoc(hist)
            if not (maxLoc[1] == target_color and maxVal > width * 0.4):
                break

        return lx, ty, rx, by


class Item:
    def __init__(self, img_rgb, title_img_rgb, svm_card, svm_rarity, debug=False):
        self.img_rgb = img_rgb
        self.title_img_rgb = title_img_rgb
        self.card = self.classify_card(svm_card)
        self.name = self.classify_item(svm_rarity)
        if debug:
            print(self.card, end=": ")
            print(self.name)

    def make_new_servant(self):
        """
        ファイル名候補を探す
        """
        for i in range(999):
            itemfile = Servant_dir / ('servant{:0=3}'.format(i + 1) + '.png')
            if itemfile.is_file():
                continue
            else:
                cv2.imwrite(itemfile.as_posix(), self.img_rgb)
                dist_local_servant[itemfile] = compute_hash_inner(self.img_rgb)
                break
        return itemfile.stem

    def make_new_ce(self):
        """
        ファイル名候補を探す
        """
        for i in range(999):
            itemfile = CE_dir / ('ce{:0=3}'.format(i + 1) + '.png')
            if itemfile.is_file():
                continue
            else:
                cv2.imwrite(itemfile.as_posix(), self.img_rgb)
                dist_local_ce[itemfile] = compute_hash_ce(self.img_rgb)
                dist_local_ce_center[itemfile] = hasher.compute(self.img_rgb[78:163, 86:190])
                break
        return itemfile.stem

    def classify_servant(self):
        """
        既所持のアイテム画像の距離を計算して保持
        """
        hash_item = compute_hash_inner(self.img_rgb)  # 画像の距離
        itemfiles = {}
        # 既存のアイテムとの距離を比較
        for i in dist_servant.keys():
            d = hasher.compare(hash_item, dist_servant[i])
            if d <= 20:  # 16だと誤認識
                itemfiles[i] = d
        if len(itemfiles) > 0:
            itemfiles = sorted(itemfiles.items(), key=lambda x: x[1])
            item = next(iter(itemfiles))
            return item[0]

        return ""

    def classify_ce(self):
        """
        既所持のアイテム画像の距離を計算して保持
        """
        hash_item = compute_hash_ce(self.img_rgb)  # 画像の距離

        itemfiles = {}
        # 既存のアイテムとの距離を比較
        for i in dist_ce.keys():
            d = hasher.compare(hash_item, dist_ce[i])
            if d <= 17:  # 18以上にすると誤認識あり
                itemfiles[i] = d
        if len(itemfiles) > 0:
            itemfiles = sorted(itemfiles.items(), key=lambda x: x[1])
            item = next(iter(itemfiles))
            return item[0]
        # 自動変換された礼装の判定
        hash_item = hasher.compute(self.img_rgb[35:77, 40:88])  # 画像の距離
        itemfiles = {}
        # 既存のアイテムとの距離を比較
        for i in dist_ce_center.keys():
            d = hasher.compare(hash_item, dist_ce_center[i])
            if d <= 15:  # 10だと失敗する場合あり
                itemfiles[i] = d
        if len(itemfiles) > 0:
            itemfiles = sorted(itemfiles.items(), key=lambda x: x[1])
            item = next(iter(itemfiles))
            return item[0]

        return ""

    def classify_ccode(self):
        """
        既所持のアイテム画像の距離を計算して保持
        """
        h, w = self.img_rgb.shape[:2]
        size = 54
        hash_item = hasher.compute(self.img_rgb[int(h/2-size/2):int(h/2+size/2),
                                                int(w/2-size/2):int(w/2+size/2)])  # 画像の距離
        itemfiles = {}

        # 既存のアイテムとの距離を比較
        for i in dist_ccode.keys():
            d = hasher.compare(hash_item, dist_ccode[i])
            if d <= 20:  # 15だとエラー有り
                itemfiles[i] = d
        if len(itemfiles) > 0:
            itemfiles = sorted(itemfiles.items(), key=lambda x: x[1])
            item = next(iter(itemfiles))
            return item[0]

        return ""

    def classify_exp(self):
        """
        既所持のアイテム画像の距離を計算して保持
        """
        hash_item = hasher.compute(self.img_rgb[35:77, 40:88])  # 画像の距離
        # 自動変換(売却)したときにマナプリアイコンや数字にかぶらない範囲
        itemfiles = {}
        # 既存のアイテムとの距離を比較
        for i in dist_exp.keys():
            d = hasher.compare(hash_item, dist_exp[i])
            if d <= 15:
                itemfiles[i] = d
        if len(itemfiles) > 0:
            itemfiles = sorted(itemfiles.items(), key=lambda x: x[1])
            item = next(iter(itemfiles))
            hash_tanebi_class = self.compute_tanebi_class_hash(self.img_rgb)
            tanebiclassfiles = {}
            for i in dist_tanebi_class.keys():
                if (item[0].replace('変換', ''))[-2:] in i:
                    dtc = hasher.compare(hash_tanebi_class, dist_tanebi_class[i])
                    if dtc <= 22:  # 22離れることがあったので
                        tanebiclassfiles[i] = dtc
            tanebiclassfiles = sorted(tanebiclassfiles.items(), key=lambda x: x[1])
            if len(tanebiclassfiles) > 0:
                tanebiclass = next(iter(tanebiclassfiles))
                return tanebiclass[0].replace('変換', '')

            return item[0]

        return ""

    def classify_status(self, svm_rarity):
        """
        既所持のアイテム画像の距離を計算して保持
        """
        rarity = self.classify_rarity(svm_rarity)

        hash_item = compute_hash_exp(self.img_rgb)  # 画像の距離
        itemfiles = {}
        # 既存のアイテムとの距離を比較
        for i in dist_status.keys():
            d = hasher.compare(hash_item, dist_status[i])
            if d <= 15:
                itemfiles[i] = d
        if len(itemfiles) > 0:
            itemfiles = sorted(itemfiles.items(), key=lambda x: x[1])
            item = next(iter(itemfiles))
            hash_status_class = self.compute_tanebi_class_hash(self.img_rgb)
            statusclassfiles = {}
            for i in dist_status_class.keys():
                # クラス判定
                if (item[0].replace('変換', ''))[-2:] in i:
                    dtc = hasher.compare(hash_status_class, dist_status_class[i])
                    statusclassfiles[i] = dtc
            statusclassfiles = sorted(statusclassfiles.items(), key=lambda x: x[1])
            if len(statusclassfiles) > 0:
                statusclass = next(iter(statusclassfiles))
                return statusclass[0][0] + rarity + statusclass[0][3:].replace('変換', '')

            return item[0][0] + rarity + item[0][3:].replace('変換', '')

        return ""

    def classify_local_servant(self):
        """
        既所持のアイテム画像の距離を計算して保持
        """
        hash_item = compute_hash_inner(self.img_rgb)  # 画像の距離

        itemfiles = {}
        # 既存のアイテムとの距離を比較
        for i in dist_local_servant.keys():
            d = hasher.compare(hash_item, dist_local_servant[i])
            if d <= 20:
                itemfiles[i] = d
        if len(itemfiles) > 0:
            itemfiles = sorted(itemfiles.items(), key=lambda x: x[1])
            item = next(iter(itemfiles))
            return item[0].stem

        return ""

    def classify_local_ce(self):
        """
        既所持のアイテム画像の距離を計算して保持
        """
        hash_item = compute_hash_ce(self.img_rgb)  # 画像の距離

        itemfiles = {}
        # 既存のアイテムとの距離を比較
        for i in dist_local_ce.keys():
            d = hasher.compare(hash_item, dist_local_ce[i])
            if d <= 15:
                itemfiles[i] = d
        if len(itemfiles) > 0:
            itemfiles = sorted(itemfiles.items(), key=lambda x: x[1])
            item = next(iter(itemfiles))
            return item[0].stem
        # 自動変換された礼装の判定
        hash_item = hasher.compute(self.img_rgb[78:163, 86:190])  # 画像の距離
        itemfiles = {}
        # 既存のアイテムとの距離を比較
        for i in dist_local_ce_center.keys():
            d = hasher.compare(hash_item, dist_local_ce_center[i])
            if d <= 10:
                itemfiles[i] = d
        if len(itemfiles) > 0:
            itemfiles = sorted(itemfiles.items(), key=lambda x: x[1])
            item = next(iter(itemfiles))
            return item[0].stem

        return ""

    def classify_card(self, svm_card):
        """
        カード判別器
       """
        """
        カード判別器
        この場合は画像全域のハッシュをとる
        """
        # Hog特徴のパラメータ
        win_size = (120, 60)
        block_size = (16, 16)
        block_stride = (4, 4)
        cell_size = (4, 4)
        bins = 9
        test = []
        carddic = {1: 'Servant', 2: 'Craft Essence', 3: 'Exp. UP', 4: 'Status UP', 5: "Command Code"}

        tmpimg = self.title_img_rgb
        # cv2.imshow("img", cv2.resize(tmpimg, dsize=None, fx=5.5, fy=5.5))
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        # cv2.imwrite("cardimg.png", tmpimg)
        tmpimg = cv2.resize(tmpimg, (win_size))
        hog = cv2.HOGDescriptor(win_size, block_size, block_stride, cell_size, bins)
        test.append(hog.compute(tmpimg))  # 特徴量の格納
        test = np.array(test)
        pred = svm_card.predict(test)

        return carddic[pred[1][0][0]]

    def classify_rarity(self, svm_rarity):
        """
        レアリティ判別器
        """
        # Hog特徴のパラメータ
        win_size = (120, 60)
        block_size = (16, 16)
        block_stride = (4, 4)
        cell_size = (4, 4)
        bins = 9
        test = []
        raritydic = {10: '★1', 11: '★1', 20: '★2', 21: '★2', 30: '★3', 31: '★3'}

        tmpimg = self.img_rgb[99:125, 76:125]

        tmpimg = cv2.resize(tmpimg, (win_size))
        hog = cv2.HOGDescriptor(win_size, block_size, block_stride, cell_size, bins)
        test.append(hog.compute(tmpimg))  # 特徴量の格納
        test = np.array(test)
        pred = svm_rarity.predict(test)

        return raritydic[pred[1][0][0]]

    def classify_item(self, svm_rarity, debug=False):
        """
        アイテム判別器
        """
        if self.card == "Servant":
            item = self.classify_servant()
            if item == "":
                item = self.classify_local_servant()
            if item == "":
                item = self.make_new_servant()
        elif self.card == "Craft Essence":
            item = self.classify_ce()
            if item == "":
                item = self.classify_local_ce()
            if item == "":
                item = self.make_new_ce()
        elif self.card == "Command Code":
            item = self.classify_ccode()
        elif self.card == "Exp. UP":
            item = self.classify_exp()
        elif self.card == "Status UP":
            item = self.classify_status(svm_rarity)

        return item

    def compute_tanebi_class_hash(self, img_rgb):
        """
        種火クラス判別器
        記述した比率は枠を取り除いた128x128イメージのの実測値
        """
        height, width = img_rgb.shape[:2]
        img = img_rgb[:34, :35]
        return hasher.compute(img)


def compute_hash_ce(img_rgb):
    """
    判別器
    この判別器は上部のクラスアイコンと下部の★表示を除いた部分を比較するもの
    """
    img = img_rgb[34:87, :]
    return hasher.compute(img)


def compute_hash_inner(img_rgb):
    """
    判別器
    この判別器は上部のクラスアイコンと下部の★表示を除いた部分を比較するもの
    """
    img = img_rgb[34:104, :]
    # cv2.imshow("img", cv2.resize(img, dsize=None, fx=5.5, fy=5.5))
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # cv2.imwrite("antan_gacha.png", img)

    return hasher.compute(img)


def compute_hash_exp(img_rgb):
    """
    判別器
    この判別器は上部のクラスアイコンと下部の★表示を除いた部分を比較するもの
    """
    img = img_rgb[34:104, :]
    return hasher.compute(img)


def calc_dist_local_servant():
    """
    既所持のアイテム画像の距離(一次元配列)の辞書を作成して保持
    """
    files = Servant_dir.glob('**/*.png')
    for fname in files:
        img = imread(fname)
        dist_local_servant[fname] = compute_hash_inner(img)


def calc_dist_servant():
    """
    既所持のアイテム画像の距離(一次元配列)の辞書を作成して保持
    """
    with open(Servant_dist_file, encoding='UTF-8') as f:
        reader = csv.reader(f)
        for row in reader:
            dist_servant[row[0]] = np.array([row[2:]], dtype='uint8')


def calc_dist_ce():
    """
    既所持のアイテム画像の距離(一次元配列)の辞書を作成して保持
    """
    with open(CE_dist_file, encoding='UTF-8') as f:
        reader = csv.reader(f)
        for row in reader:
            dist_ce[row[0]] = np.array([row[2:]], dtype='uint8')

    with open(CE_center_dist_file, encoding='UTF-8') as f:
        reader = csv.reader(f)
        for row in reader:
            dist_ce_center[row[0]] = np.array([row[2:]], dtype='uint8')


def calc_dist_ccode():
    """
    既所持のアイテム画像の距離(一次元配列)の辞書を作成して保持
    """
    with open(CCode_dist_file, encoding='UTF-8') as f:
        reader = csv.reader(f)
        for row in reader:
            dist_ccode[row[0]] = np.array([row[2:]], dtype='uint8')


def calc_dist_local_ce():
    """
    既所持のアイテム画像の距離(一次元配列)の辞書を作成して保持
    """
    files = CE_dir.glob('**/*.png')
    for fname in files:
        img = imread(fname)
        dist_local_ce[fname] = compute_hash_ce(img)
        dist_local_ce_center[fname] = hasher.compute(img[35:77, 40:88])


def make_std_item():
    # 鯖リストを作成
    # ★0-2鯖はそのまま
    # ★3-4鯖はホワイトリストのみ読み込む
    with open(FP_34Servant_wl, encoding='UTF-8') as f:
        wl_servants = [s.strip() for s in f.readlines()]

    servant = []
    with open(Servant_dist_file, encoding='UTF-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[1] in ['0', '1', '2']:
                servant.append(row[0])
            elif row[1] in ['3', '4'] and row[0] in wl_servants:
                servant.append(row[0])
    # 礼装リストを作成
    # ★1-2礼装はブラックリストを除外
    # ★3礼装はホワイトリストのみ読み込む
    with open(FP_12CE_bl, encoding='UTF-8') as f:
        bl_ce = [s.strip() for s in f.readlines()]
    with open(FP_3CE_wl, encoding='UTF-8') as f:
        wl_ce = [s.strip() for s in f.readlines()]

    ce = []
    with open(CE_dist_file, encoding='UTF-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[1] in ['1', '2'] and row[0] not in bl_ce:
                ce.append(row[0])
            elif row[1] in ['3'] and row[0] in wl_ce:
                ce.append(row[0])
    ccode = []
    with open(CCode_dist_file, encoding='UTF-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[1] in ['1', '2']:
                ccode.append(row[0])

    std_item = servant \
               + exp_1star + exp_2star + exp_3star + exp_4star + exp_5star \
               + status_1star + status_2star + status_3star \
               + ce \
               + ccode

    for i in std_item:
        std_item_dic[i] = 0


def initialize():
    calc_dist_local_servant()
    calc_dist_servant()
    calc_dist_local_ce()
    calc_dist_ce()
    calc_dist_ccode()
    make_std_item()
    svm_card = cv2.ml.SVM_load(str(train_card))
    svm_rarity = cv2.ml.SVM_load(str(train_rarity))
    card_path = Path(__file__).resolve().parent / Path("data/cardimgs")
    p_temp = list(card_path.glob("*.jpg"))
    card_imgs = []
    for f in p_temp:
        card_imgs.append(cv2.imread(str(f)))

    return svm_card, svm_rarity, card_imgs


class Processor:
    def __init__(self, svm_card, svm_rarity, card_imgs, args):
        self.svm_card = svm_card
        self.svm_rarity = svm_rarity
        self.card_imgs = card_imgs
        self.args = args
        # 重複検出用: 直前の処理結果を保持する
        self.prev_itemlist = []
        # 実行結果蓄積用: process() のたびにデータが積みあがっていく
        self.wholelist = []
        self.outputlist = []
        self.num_summon = 0

    def process(self, filename):
        result = self._process(filename)
        logger.info(f"processed {filename}")
        self.outputlist.append(result)

    def _process(self, filename):
        if self.args.debug:
            print(filename)

        f = Path(filename)

        if not f.exists():
            return {'filename': str(filename) + ': Not Found'}

        elif f.suffix.upper() not in ('.PNG', '.JPG', '.JPEG'):
            return {'filename': str(filename) + ': Not Supported'}

        img_rgb = imread(filename)

        try:
            sc = ScreenShot(img_rgb, self.svm_card, self.svm_rarity, self.card_imgs, self.args)
            # 戦利品順番ルールに則った対応による出力処理
            if self.prev_itemlist == sc.itemlist:
                return {'filename': str(filename) + ': Duplicate'}

            self.wholelist += sc.itemlist
            output = {'filename': filename}
            output.update(sc.allitemdic)
            output['召喚数'] = len(sc.itemlist)
            output['聖晶石召喚'] = "1" if sc.summon_mode == "SQ" else ""
            self.num_summon += sc.num_summon
            self.prev_itemlist = sc.itemlist
            return output

        except Exception as e:
            logger.error(f'{filename}: {e}', exc_info=True)
            return {'filename': str(filename) + ': not valid'}

    def get_output(self):
        """
        出力内容を作成
        """

        # CSVフィールド名用 key しか使わない
        csvfieldnames = {'filename': "合計", '召喚数': "", '聖晶石召喚': ""}

        tmpdic = {'召喚数': self.num_summon}
        csvfieldnames.update(tmpdic)
        std_item_dic.update(dict(Counter(self.wholelist)))
        csvfieldnames.update(std_item_dic)

        return csvfieldnames, self.outputlist


class OnCreatedEventHandler(FileSystemEventHandler):
    """
    ファイル作成イベントで呼ばれるイベントハンドラ
    """
    def __init__(self, processor):
        super().__init__()

        self.processor = processor

    def on_created(self, event):
        super().on_created(event)
        logger.info(f"{event.src_path} created")

        if event.is_directory:
            logger.info(f"{event.src_path} is a directory, skip")
            return

        # ファイルコピーの完了まで待つ
        # https://stackoverflow.com/a/41105283
        src = Path(event.src_path)
        filesize = -1
        while filesize != src.stat().st_size:
            filesize = src.stat().st_size
            time.sleep(0.5)

        self.processor.process(event.src_path)


class EventDrivenRunner:
    """
    指定フォルダーを監視し、ファイルが新しく作成されたらそれを processor に渡す runner.

    監視機構の実現に watchdog を使用する。
    """
    def __init__(self, processor, path):
        self.processor = processor
        self.path = path

    def run(self):
        handler = OnCreatedEventHandler(self.processor)
        observer = Observer()
        observer.schedule(handler, self.path, recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(0.5)

        except KeyboardInterrupt:
            pass

        finally:
            observer.stop()
            observer.join()


class BatchRunner:
    """
    初期化時に渡されたファイル群をバッチ処理で processor に処理させる runner.
    """
    def __init__(self, processor, filenames):
        self.processor = processor
        self.filenames = filenames

    def run(self):
        for filename in self.filenames:
            self.processor.process(filename)


if __name__ == '__main__':
    # オプションの解析
    parser = argparse.ArgumentParser(description='FGOの召喚スクショを数えをCSV出力する')
    # 3. parser.add_argumentで受け取る引数を追加していく
    parser.add_argument('filenames', help='入力ファイル', nargs='*')    # 必須の引数を追加
    parser.add_argument('-f', '--folder', help='フォルダで指定')
    parser.add_argument('-o', '--old', help='2018年8月以前の召喚画面', action='store_true')
    parser.add_argument('-d', '--debug', help='デバッグ情報の出力', action='store_true')
    parser.add_argument('-w', '--watch', help='フォルダ監視モード', action='store_true')
    parser.add_argument('--version', action='version', version=progname + " " + version)

    args = parser.parse_args()    # 引数を解析
    if args.watch and not args.folder:
        parser.error("argument -w/--watch must be specified with -f/--folder")

    logging.basicConfig(
        level=logging.INFO,
        format='%(name)s <%(filename)s-L%(lineno)s> [%(levelname)s] %(message)s',
    )

    if not Item_dir.is_dir():
        Item_dir.mkdir()
    if not Servant_dir.is_dir():
        Servant_dir.mkdir()
    if not CE_dir.is_dir():
        CE_dir.mkdir()

    svm_card, svm_rarity, card_imgs = initialize()
    processor = Processor(
        svm_card=svm_card,
        svm_rarity=svm_rarity,
        card_imgs=card_imgs,
        args=args,
    )
    if args.watch:
        runner = EventDrivenRunner(processor, args.folder)

    elif args.folder:
        inputs = [x for x in Path(args.folder).iterdir()]
        runner = BatchRunner(processor, inputs)

    else:
        runner = BatchRunner(processor, args.filenames)

    runner.run()
    csvfieldnames, outputcsv = processor.get_output()

    fnames = csvfieldnames.keys()
    writer = csv.DictWriter(sys.stdout, fieldnames=fnames, lineterminator='\n')
    writer.writeheader()
    if len(outputcsv) > 1:  # ファイル一つのときは合計値は出さない
        writer.writerow(csvfieldnames)
    for o in outputcsv:
        writer.writerow(o)
