import argparse
import subprocess
from pathlib import Path

import PySimpleGUIWx as sg

try:
    from version import version
except ImportError:
    version = "develop"

KEY_TARGET_FOLDER = "TargetFolder"
KEY_EXEC_BUTTON = "ExecButton"
KEY_ENABLE_DEBUGMODE = "EnableDebugging"
KEY_EXEC_RESULT_OUTPUT = "ResultOutput"

BUNDLED_PYTHON = "gui\\python\\python"
SYSTEM_PYTHON = "python"


def make_window(theme):
    sg.theme(theme)

    layout = [
        [
            sg.Text("フォルダ"),
            sg.InputText(key=KEY_TARGET_FOLDER), sg.FolderBrowse(),
            sg.Checkbox("デバッグ出力を有効にする", default=False, pad=(20, 0), key=KEY_ENABLE_DEBUGMODE),
        ],
        [sg.Submit("実行", key=KEY_EXEC_BUTTON)],
        [sg.Text("\n実行結果")],
        [sg.Multiline(size=(80, 12), key=KEY_EXEC_RESULT_OUTPUT)],
        [sg.Text("全パターン出力されます。適切なものを1つ選んで Twitter に投稿してください。")],
        [sg.Text("\n\nログ")],
        [sg.Output(size=(80, 12))],
    ]

    return sg.Window(f'fgogachacnt FGOガチャ結果スクショ集計 {version}', layout)


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


def run_fgogachacnt(python_exe, folder, enable_debug=False):
    cmd = [
        python_exe,
        "fgogachacnt.py",
        "-f",
        folder,
    ]
    if enable_debug:
        cmd.append("-d")

    return run_command(cmd)


def run_csv2report(python_exe, input):
    cmd = [
        python_exe,
        "csv2report.py",
    ]
    return run_command(cmd, input)


def main(args):
    window = make_window(sg.theme())

    if args.use_system_python:
        python_exe = SYSTEM_PYTHON
    else:
        python_exe = BUNDLED_PYTHON

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

            if values[KEY_ENABLE_DEBUGMODE]:
                enable_debug = True
            else:
                enable_debug = False

            out = run_fgogachacnt(python_exe, targetFolder, enable_debug)
            result = run_csv2report(python_exe, out)

            window[KEY_EXEC_RESULT_OUTPUT].update(result.decode("cp932"))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--use-system-python", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
