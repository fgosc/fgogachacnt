import subprocess
from pathlib import Path

import PySimpleGUIWx as sg

KEY_TARGET_FOLDER = "TargetFolder"
KEY_EXEC_BUTTON = "ExecButton"
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


def run_fgogachacnt(folder, enable_debug):
    cmd = [
        "gui\\python\\python",
        "fgogachacnt.py",
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

            if values[KEY_ENABLE_DEBUGMODE]:
                enable_debug = True
            else:
                enable_debug = False

            out = run_fgogachacnt(targetFolder, enable_debug)
            result = run_csv2report(out, report_option)

            window[KEY_EXEC_RESULT_OUTPUT].update(result.decode("cp932"))


if __name__ == "__main__":
    main()
