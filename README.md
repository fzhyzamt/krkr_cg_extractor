# wlkz_scripts

一些为了实现某些乱七八糟的功能所写的一些 python 脚本集合。

## [bili_music_tagger](https://github.com/wlkz/bili_music_tagger)

一个能自动将 Bilibili 音频上缓存的音乐自动添加元数据（歌曲名称、歌手等）信息的小脚本。

[详细参见](https://github.com/wlkz/bili_music_tagger/blob/master/README_zh.md)

## [onsen_api](https://github.com/wlkz/onsen_api)

对音泉的 API 进行一个封装，可以便捷地下载当期的广播。

不支持付费广播。

<!-- 好像支持付费就没在公网开源过 -->

## [md_img_url_converter.py](md_img_url_converter.py)

当时为了转移博客上炸掉的新浪图库的图片写的，可以：

1. 将 markdown 文件里远端的图片缓存到本地，可以抢救因为新浪防盗链的博客文章。
2. 将 markdown 文件里的本地图片推到远端图床（仅仅实现了 [sm.sm](https://sm.ms) 的 API，其他图床同理），加速部署到静态托管网站上的访问速度。

大概写成比较容易拓展的样子，稍微修改即可实现更多功能。

## [sp_epub_builder.py](sp_epub_builder.py)

将 [Summer Pockets」ショートストーリー～夏の眩しさの中で～](http://key.visualarts.gr.jp/summer/special_ss.html) 小说全部下载，打包成 epub。

这个东东好像是用了个日本那边的一个开源在线 epub 3 浏览器框架 [Bibi](https://bibi.epub.link/)，按道理采用相同框架的应该都可以改改用这个脚本下载下来。

## [krkr_cg_extractor.py](krkr_cg_extractor.py)

合成 [KrkrExtract](https://github.com/xmoeproject/KrkrExtract/releases) 拖出来的差分 tlg 文件到完整的 png 图片。在柚子社游戏上测试通过。

1. 下载依赖
  [Python 3.7+](https://www.python.org/downloads/) 注意，安装过程中，务必勾上 Add Python 3.8 to PATH 选项。
  [tlg2png](https://github.com/vn-tools/tlg2png/releases/download/v1.0/tlg2png-v10-w32.zip)
  [KrkrExtract](https://github.com/xmoeproject/KrkrExtract/releases)
2. 解压游戏
  参见 [KrkrExtract](https://github.com/xmoeproject/KrkrExtract) 的说明，解压游戏。
  务必勾选 `Full Unpack`。
  把 `evimage.xp3` 解压即可。
3. 解压游戏后在游戏目录会有 `KrkrExtract_Output` 的文件，在目录下新建 `3rdparty` 文件夹，将  `tlg2png` 全部文件放进去。
4. 下载该代码，放到目录下。
5. 在空白处 shift + 右键， 点上 “在此处打开 Powershell 窗口”， 运行

  ```shell
  pip install pillow
  python krkr_cg_extractor.py
  ```
