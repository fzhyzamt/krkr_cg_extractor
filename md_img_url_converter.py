# md img url converter.py
# Is a part of wlkz scripts https://github.com/wlkz/wlkz_scripts
# Author: wlkz
# Dependency: requests
# License: WTFPL
# Last update: 2020-04-28

import datetime
import os
import posixpath
import random
import re
import uuid
from pathlib import Path, PurePosixPath

import requests


class WebEndpoint:
    def __init__(self):
        pass

    def get(self, url):
        return requests.get(url).content

    def save(self):
        raise NotImplementedError()


class SMMSEndpoint:
    base_endpoint = 'https://sm.ms/api/v2/'

    def __init__(self, token):
        self.token = token

    @classmethod
    def login(cls, username, passwd):
        data = {
            'username': username,
            'password': passwd
        }
        url = cls.base_endpoint + 'token'
        res_json = requests.post(url, data).json()
        return res_json['data']['token']

    @classmethod
    def from_login(cls, username, passwd):
        token = cls.login(username, passwd)
        return cls(token)

    def get(self, url):
        return requests.get(url).content

    def save(self, content):
        files = {'smfile': content}
        url = self.base_endpoint + 'upload'
        res_json = requests.post(url, files=files, headers={
                                 'Authorization': self.token}).json()
        return res_json['data']['url']


class LocalEndpoint:
    def __init__(self, img_path=Path.cwd(), start_path=Path.cwd()):
        self.img_path = Path(img_path).resolve()
        self.start_path = Path(start_path).resolve()

    def get(self, url):
        path = self.start_path / url
        with path.open('rb') as fp:
            out = fp.read()
        return out

    def save(self, content, filename=None):
        if filename is None:
            filename = f'{datetime.datetime.now():%Y%m%d%H%M%S}_{random.randint(0, 1000):0>4}.jpg'
        file_path = self.img_path / filename
        with open(file_path, 'wb') as fp:
            fp.write(content)
        return posixpath.relpath(file_path.as_posix(), self.start_path.as_posix())


class ImageConverter:
    compiled_get_img_regex = re.compile(r'(^!\[.*\]\()(.*)(\)$)')

    def __init__(self, src_endpoint, dst_endpoint):
        self.src_endpoint = src_endpoint
        self.dst_endpoint = dst_endpoint
        self.src2dst = {}

    def process_thumbnail_url(self, line):
        img = re.match(r'(thumbnail: *)(.*)', line)

        if not img:
            return line

        img_url = img.group(2)

        v = self.src2dst.get(img_url)
        if v:
            new_img_url = v
        else:
            img_content = self.src_endpoint.get(img_url)
            new_img_url = self.dst_endpoint.save(img_content)
            self.src2dst[img_url] = new_img_url

        new_line = re.sub(r'(thumbnail: *)(.*)',
                          rf'thumbnail: {new_img_url}', line)
        return new_line

    def process_img_tag_url(self, line):
        img = self.compiled_get_img_regex.match(line)

        if img is None:
            return line

        img_url = img.group(2)
        v = self.src2dst.get(img_url)

        if v:
            new_img_url = v
        else:
            img_content = self.src_endpoint.get(img_url)
            new_img_url = self.dst_endpoint.save(img_content)
            self.src2dst[img_url] = new_img_url

        new_line = self.compiled_get_img_regex.sub(
            rf'\g<1>{new_img_url}\g<3>', line)

        return new_line

    def save_src2dst(self):
        path = (
            Path.cwd() / f'{self.src_endpoint.__class__.__name__}_{self.dst_endpoint.__class__.__name__}.txt')

        out = '\n'.join([f'{k} {v}' for k, v in self.src2dst.items()])

        with path.open('w', encoding='utf-8') as fp:
            fp.write(out)

    def load_src2dst(self):
        self.src2dst = {}
        path = (
            Path.cwd() / f'{self.src_endpoint.__class__.__name__}_{self.dst_endpoint.__class__.__name__}.txt')
        with path.open('r', encoding='utf-8') as fp:
            for line in fp:
                line = line.strip()
                k, v = line.split(' ')
                self.src2dst[k] = v

    def process(self, text):
        text_lines = text.splitlines()
        out = []
        for line in text_lines:
            new_line = self.process_thumbnail_url(line)
            new_line = self.process_img_tag_url(new_line)
            out.append(new_line)

        return '\n'.join(out)


def remote2local():
    old_post_path = Path('post')
    new_post_path = Path('source/posts')
    new_img_path = Path('source/img')

    c = ImageConverter(WebEndpoint(), LocalEndpoint(
        new_img_path, new_post_path))

    for file_path in old_post_path.glob('7.md'):
        with file_path.open('r', encoding='utf-8') as fp:
            text = fp.read()

        new_text = c.process(text)

        new_file_path = new_post_path / file_path.name

        with new_file_path.open('w', encoding='utf-8') as fp:
            fp.write(new_text)


def local2remote():
    u = 'sm.ms username'
    p = 'sm.ms password'

    old_post_path = Path('source/posts')
    new_post_path = Path('source/_posts')

    c = ImageConverter(LocalEndpoint(start_path=old_post_path),
                       SMMSEndpoint.from_login(u, p))
    c.load_src2dst()
    for file_path in old_post_path.glob('*.md'):
        with file_path.open('r', encoding='utf-8') as fp:
            text = fp.read()

        new_text = c.process(text)

        new_file_path = new_post_path / file_path.name

        with new_file_path.open('w', encoding='utf-8') as fp:
            fp.write(new_text)

    c.save_src2dst()


if __name__ == "__main__":
    local2remote()
