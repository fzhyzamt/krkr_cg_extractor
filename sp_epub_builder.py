# sp epub builder
# Is a part of wlkz scripts https://github.com/wlkz/wlkz_scripts
# Author: wlkz
# Dependency: requests
# License: WTFPL
# Last update: 2020-04-28

import os
import shutil
import xml.etree.ElementTree as ET
import zipfile

import requests

books = ['ss_ao', 'ss_mizuori', 'ss_tenzen', 'ss_tsumugi', 'ss_inari', 'ss_shiroha', 'ss_nomiki',
         'ss_kobato', 'ss_ryoichi', 'ss_kamome', 'ss_kyouko', 'ss_umi']

base_url = 'http://key.visualarts.gr.jp/summer/bib/bookshelf'
output_base_path = 'out'

container_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/standard.opf" media-type="application/oebps-package+xml"/>
   </rootfiles>
</container>
'''


def get(book_name):
    output_path = f'{output_base_path}/{book_name}'

    os.makedirs(output_path, exist_ok=True)

    book_url = f'{base_url}/{book_name}'
    book_item_url = f'{base_url}/{book_name}/item'

    conn_timeout = 6
    read_timeout = 60
    timeouts = (conn_timeout, read_timeout)

    def save_file_from_remote(url):
        output_url = f'{output_path}/{url}'
        if os.path.exists(output_url):
            return
        while True:
            try:
                content = requests.get(
                    f'{book_item_url}/{url}', timeout=timeouts).content
                break
            except (requests.ConnectionError, requests.exceptions.Timeout):
                print('gg, try again')

        write_file(output_url, content)

    # container_url = f'{book_url}/META-INF/container.xml'
    # container_xml = requests.get(container_url).text
    # root = ET.fromstring(container_xml)
    # namespace = '{urn:oasis:names:tc:opendocument:xmlns:container}'

    standard_opf_url = f'{book_item_url}/standard.opf'

    save_file_from_remote('standard.opf')

    root = ET.parse(f'{output_path}/standard.opf')

    for f in root.findall('.//{http://www.idpf.org/2007/opf}item'):
        url = f.get('href')
        save_file_from_remote(url)


def write_file(path, content):
    print(path)
    new_path = '/'.join(path.split('/')[:-1])
    os.makedirs(new_path, exist_ok=True)
    with open(path, 'wb') as fp:
        fp.write(content)


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), f'{root[7:]}/{file}')


def epub_builder(book_name, i):
    output_path = f'{output_base_path}/{book_name}'
    temp_path = f'{output_base_path}/tmp'
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)
    os.mkdir(temp_path)
    os.mkdir(f'{temp_path}/META-INF')
    write_file(f'{temp_path}/mimetype', b'application/epub+zip')
    write_file(f'{temp_path}/META-INF/container.xml',
               bytes(container_xml, encoding='utf-8'))
    shutil.copytree(output_path, f'{temp_path}/OEBPS')

    root = ET.parse(f'{output_path}/standard.opf')

    title = root.find('.//{http://purl.org/dc/elements/1.1/}title').text
    creator = root.find('.//{http://purl.org/dc/elements/1.1/}creator').text

    filename = f'{i:0>2}[{creator}].{title}.epub'

    with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipdir(temp_path, zipf)


if __name__ == "__main__":
    os.makedirs(output_base_path, exist_ok=True)
    for i, b in enumerate(books, 1):
        get(b)
        epub_builder(b, i)
