# krkr cg extractor
# Is a part of wlkz scripts https://github.com/wlkz/wlkz_scripts
# Author: wlkz
# Dependency: tlg2png (https://github.com/vn-tools/tlg2png), PIL
# License: WTFPL
# Last update: 2020-04-28

import json
import os
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

from PIL import Image

evimage_path = Path('evimage')
tlg2png_path = Path('3rdparty') / 'tlg2png.exe'
output_path = Path('output')

output_path.mkdir(exist_ok=True)


def process(source_path):
    base_name = source_path.stem

    img_json_path = evimage_path / f'{base_name}.json'
    if not img_json_path.exists():
        return
    with img_json_path.open('r') as fp:
        img_json = json.load(fp)

    source_path = evimage_path / base_name

    for tlg_path in source_path.glob('*.tlg'):
        png_path = tlg_path.with_suffix('.png')
        if png_path.exists():
            continue
        os.system(f'{tlg2png_path} {tlg_path} {png_path}')

    base_layer = img_json['layers'][-1]
    assert base_layer['top'] == base_layer['left'] == 0

    cur_output_path = output_path / base_name
    cur_output_path.mkdir(exist_ok=True)

    base_path = None

    for layer in img_json['layers'][::-1]:
        assert layer['opacity'] == 255 and layer['type'] == 13 and layer['layer_type'] == 0
        # layer['visible'] == 0 貌似是在不在界面显示？
        if layer['visible'] == 0:
            print('layer[\'visible\'] == 0')

        output_target = cur_output_path / f'{base_name}_{layer["name"]}.png'
        new_layer_path = source_path / f'{layer["layer_id"]}.png'

        new_layer_img = Image.open(new_layer_path)
        if new_layer_img.width != layer['width'] or new_layer_img.height != layer['height']:
            # 意义不明的 0 * 0 图片，还是每组图的第 k 张，我也不知道哪出问题了
            print(f'Bad layer: {output_target}')
            continue

        if layer["name"].endswith('a') or len(layer["name"]) == 1:
            base_path = new_layer_path

        if not output_target.exists():
            if base_path == new_layer_path:
                shutil.copy(base_path, output_target)
            else:
                base_img = Image.open(base_path)

                base_img.paste(
                    new_layer_img, (layer['left'], layer['top']), new_layer_img)
                base_img.save(output_target)
            print(f'Output: {output_target}')
        else:
            print(f'Ignore: {output_target}')
            continue


def main():
    source_paths = [path for path in evimage_path.iterdir() if path.is_dir()]
    # for source_path in source_paths:
    #     process(source_path)

    with ThreadPoolExecutor() as t:
        tasks = [t.submit(process, source_path) for source_path in source_paths]
        wait(tasks, return_when=ALL_COMPLETED)


main()
