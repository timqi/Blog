---
title: Python2.7 的一些编码问题
category: python
---

Python2.7 系统内部是以 `Unicode` 编码处理数据的。但是我们需要使用中文或者处理其他一些编码的时候我们需要先对它调用 `decode()` 方法转化成 `Unicode` 编码。本文就具体讨论一些其中的内容。
<!--more-->

查看 Python 对象的编码类型可以使用 `chardet.detect()`

``` python
import chardet
chardet.detect('\x86')
```

如果需要使用中文我们就在 Python 源文件头部声明:

``` python
# -*- coding:utf-8 -*-
```

![](/i//2014-03-23-1.png) <center>*Python 中编码解码演示*</center>

**Python 中的标准编码： [官方文档](http://docs.python.org/2/library/codecs.html#standard-encodings)**

一种编码可以包含很多种语言，同样一种语言也可以使用多种编码。这里主要说一下这几个：

- `ascii`：别名：646, us-ascii 支持的语言：English
- `gb2312`：别名：chinese, csiso58gb231280, euc- cn, euccn, eucgb2312-cn, gb2312-1980, gb2312-80, iso- ir-58 支持的语言：简体中文
- `gbk`：别名：936, cp936, ms936 支持的语言：Unified Chinese （包含繁体中文）
- `utf-8`：别名：U8, UTF, utf8 支持的语言：所有语言

还有一些 Python 内部处理字符串使用的编码：

- **`string_escape`**：将字符串当作字节码对待，不转义 `\`
- `unicode_internal`: 作用与 `string-escape` 相似，但是返回 unicode 码，即 Python 内部处理使用的编码

 ![](/i//2014-03-23-2.png)

