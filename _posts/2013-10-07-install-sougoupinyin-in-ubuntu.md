---
title: Ubuntu下安装搜狗输入法(fcitx)
category: linux
---

在ubuntu下可以使用搜狗拼音输入法了，这真是个令人振奋的消息。本文讲述怎样在Ubuntu系统下安装搜狗拼音输入法。
<!--more-->

## 1.删除系统原有的输入法

Ubuntu下默认安装了`ibus`，因此先删除它。并且对已经安装的老版fcitx同时也要删掉再重新安装。

``` bash
$ sudo apt-get remove ibus
$ sudo apt-get remove fcitx*
```

删除依赖库并检查fcitx是否已经删除：

``` bash
$ sudo apt-get autoremove
$ dpkg --get-selections | grep fcitx
```

## 2.添加fcitx的ppa

添加`fcitx`的`ppa`然后刷新软件源:


``` bash
$ sudo add-apt-repository ppa:fcitx-team/nightly
$ sudo apt-get update
```

## 3.安装搜狗输入法


``` bash
$ sudo apt-get install fcitx-sogoupinyin
```

## 4.安装所需要的依赖库(17个)

**sudo apt-get install ******

> `fcitx`
> `fcitx-bin`
> `fcitx-config-common`
> `fcitx-config-gtk`
> `fcitx-data`
> `fcitx-frontend-gtk2`
> `fcitx-frontend-gtk3`
> `fcitx-frontend-qt4`
> `fcitx-googlepinyin`
> `fcitx-libs`
> `fcitx-module-dbus`
> `fcitx-module-x11`
> `fcitx-modules`
> `fcitx-pinyin`
> `fcitx-table`
> `fcitx-table-wubi`
> `fcitx-ui-classic`

## 5.设置`fcitx`为默认输入法


``` bash
$ im-switch -s fcitx -z default
$ sudo im-switch -s fcitx -z default
```

如果没有`im-switch`命令请自行安装：`sudo apt-get install im-switch`。

## 6.注销或者重启使设置生效
