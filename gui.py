import subprocess
import sys
from datetime import datetime
from pathlib import Path

import PySimpleGUIWx as sg

KEY_TARGET_FOLDER = "TargetFolder"
KEY_EXEC_BUTTON = "ExecButton"
KEY_SUMMON_MODE = "SummonMode"
KEY_SUMMON_MODE_FP = "SummonModeRadioFPNormal"
KEY_SUMMON_MODE_FP_YAMATAI = "SummonModeRadioFPYamatai"
KEY_SUMMON_MODE_SQ = "SummonModeRadioSQ"
KEY_ENABLE_DEBUGMODE = "EnableDebugging"
KEY_EXEC_RESULT_OUTPUT = "ResultOutput"


def make_window(theme):
    sg.theme(theme)

    layout = [
        [
            sg.Text("フォルダ"),
            sg.InputText(key=KEY_TARGET_FOLDER), sg.FolderBrowse(),
            sg.Checkbox("デバッグ出力を有効にする", default=False, pad=(20, 0), key=KEY_ENABLE_DEBUGMODE),
        ],
        [
            sg.Text("召喚モード"),
            sg.Radio("フレンドポイント召喚", KEY_SUMMON_MODE, size=(15, 1), default=True, key=KEY_SUMMON_MODE_FP),
            sg.Radio("邪馬台国限定FP召喚", KEY_SUMMON_MODE, size=(16, 1), key=KEY_SUMMON_MODE_FP_YAMATAI),
            sg.Radio("聖晶石召喚", KEY_SUMMON_MODE, size=(10, 1), key=KEY_SUMMON_MODE_SQ),
        ],
        [sg.Submit("実行", key=KEY_EXEC_BUTTON)],
        [sg.Text("\n実行結果（Twitter投稿用）")],
        [sg.Multiline(size=(80, 10), key=KEY_EXEC_RESULT_OUTPUT)],
        [sg.Text("\nログ")],
        [sg.Output(size=(80, 10))],
    ]

    return sg.Window('fgogachacnt FGOガチャ結果スクショ集計', layout)


def run_command(cmd, input=None):
    print(cmd)
    print("実行中...")
    proc = subprocess.run(cmd, input=input, capture_output=True)
    print("=== stdout ===")
    print(proc.stdout.decode("cp932"))
    print("=== stderr ===")
    print(proc.stderr.decode("cp932"))
    print(f"return code: {proc.returncode}")
    return proc.stdout


def run_fgogachacnt(mode, num, folder, enable_debug):
    cmd = [
        "gui\\python\\python",
        "fgogachacnt.py",
        "-m",
        mode,
        "-n",
        num,
        "-f",
        folder,
    ]
    if enable_debug:
        cmd.append("-d")

    return run_command(cmd)


def run_csv2report(input, option):
    cmd = [
        "gui\\python\\python",
        "csv2report.py",
    ]
    if option:
        cmd.append(option)
    return run_command(cmd, input)


def main():
    window = make_window(sg.theme())

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break

        print(event, values)

        if event == KEY_EXEC_BUTTON:
            targetFolder = values[KEY_TARGET_FOLDER]
            if targetFolder == "":
                sg.popup("フォルダを指定してください。")
                continue

            p = Path(targetFolder)
            if not p.glob("*.png") and not p.glob("*.jpg") and not p.glob("*.jpeg"):
                sg.popup("フォルダ内に画像ファイルが見つかりません。")
                continue

            if values[KEY_SUMMON_MODE_FP]:
                mode = "fp"
                num = "10"
                report_option = ""

            elif values[KEY_SUMMON_MODE_FP_YAMATAI]:
                mode = "fp"
                num = "10"
                report_option = "--yamataikoku"

            elif values[KEY_SUMMON_MODE_SQ]:
                mode = "stone"
                num = "11"
                report_option = ""

            else:
                sg.popup("予期しないエラーが発生しました。")
                continue

            if values[KEY_ENABLE_DEBUGMODE]:
                enable_debug = True
            else:
                enable_debug = False

            out = run_fgogachacnt(mode, num, targetFolder, enable_debug)
            result = run_csv2report(out, report_option)

            window[KEY_EXEC_RESULT_OUTPUT].update(result.decode("cp932"))


if __name__ == "__main__":
    main()
