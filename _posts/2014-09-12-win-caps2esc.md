---
title: Win 平台交换 capslock 与 escape
category: other
---

新建一个文本文件 `caps2esc.reg`，写入内容如下：
<!--more-->

``` bash
Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Keyboard Layout]
"Scancode Map"=hex:00,00,00,00,00,00,00,00,03,00,00,00,3a,00,01,00,01,00,3a,00,00,00,00,00
```

保存文件双击运行后重新登录系统即可生效
