# auto_bili_recorder

## 前言

想要一个能自动录制B站直播并且上传百度云的程序。

功能很简单，但苦于找不到合适的程序，于是自己编写一个。

## LICENSE

MIT

## requirements

- requests
- urllib3
- bypy

## 功能

以下功能请自行编辑 `config.py` 开启/关闭

- [x] 开播通知（[server酱](https://sct.ftqq.com/)）
- [x] 多个直播间同时录制
- [x] 可选择只录制音频（全局设置）
- [x] 录制质量配置
- [x] 自动上传百度云后删除源文件

## 使用说明

1. 首先你得会 `Python` 的一些基本使用
2. 然后准备一个**百度网盘**账号
3. 在 `我的网盘/我的应用数据` 文件夹中新建一个文件夹 `bypy`
4. 运行 `auth.py` ，绑定网盘账号
5. 根据你的需求编辑 `config.py`
6. 运行 `run.py`
7. 遇到bug，提交issue或pull request

## 支持我

如果有好的想法，请**提交issue**或**pull request**贡献出你的代码
