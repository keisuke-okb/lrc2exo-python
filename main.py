import json
import os
import argparse
import chardet
from tqdm import tqdm

import lrc_tools
import text_tools
import time_tools
import exo_tools
from settings import DotDict

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
    
    encoding = result['encoding']
    return encoding

def run_generate_exo(
        input_lrc_path,
        settings_path,
        exo_output_path,
        json_output_path=None,
    ):
    with open(settings_path, "r", encoding=detect_encoding(settings_path)) as f:
        settings = json.load(f, object_hook=DotDict)

    output_dir = f"./output/{os.path.splitext(os.path.basename(input_lrc_path))[0]}/"
    os.makedirs(output_dir, exist_ok=True)

    data = lrc_tools.parse_lrc_texts(open(input_lrc_path, "r", encoding=detect_encoding(input_lrc_path)).readlines())

    for i, seg in enumerate(tqdm(data)):
        d = text_tools.draw_lyric_image_with_ruby(
            data=seg,
            settings=settings,
            output_path_1=os.path.join(output_dir, f"{i:04d}_1.png"),
            output_path_2=os.path.join(output_dir, f"{i:04d}_2.png"),
        )
        data[i] = d
    
    data = time_tools.calc_display_time(data, settings=settings)

    if json_output_path is not None:
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    output_exo = exo_tools.generate_exo(data, settings=settings)

    os.makedirs(os.path.dirname(exo_output_path), exist_ok=True)
    with open(exo_output_path, 'w', encoding="cp932") as f:
        print(output_exo, file=f)

def run_generate_exo_manually():
    run_generate_exo(
        input_lrc_path="./sample.kra",
        settings_path="settings.json",
        exo_output_path="./exo/sample.exo",
        json_output_path="output.json"
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='LRC2EXO-Python')
    parser.add_argument('--input_lrc_path', type=str, required=True, help='歌詞ファイルのパス')
    parser.add_argument('--settings_path', type=str, default='settings.json', help='設定ファイルのパス')
    parser.add_argument('--exo_output_path', type=str, required=True, help='出力するEXOファイルのパス')
    parser.add_argument('--json_output_path', type=str, default=None, help='分析後の歌詞データの保存パス')

    args = parser.parse_args()
    run_generate_exo(**vars(args))
    