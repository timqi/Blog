---
title: Python中的正则表达式
category: python
---

正则表达式是用于处理字符串的强大工具，它并不是Python的一部分。其他编程语言中也有正则表达式的概念，区别只在于不用编程语言实现支持的语法数量不同。
<!--more-->

Python拥有自己独特的语法以及一个独立的处理引擎，在提供了正则表达式的语言里，正则表达式的语法都是一样的。

下图展示了使用正则表达式进行匹配的流程：

![正则表达式匹配流程](/i//2013-12-03-1.png) <center>*正则表达式匹配流程*</center>

正则表达式的匹配过程大致是：

1. 依次拿出表达式和文本中的字符比较
2. 如果每一个字符都能匹配成功则匹配成功，一旦有字符匹配不成功字符匹配失败
3. 如果表达式中有量词活边界，这个过程会稍有些不同

下图列出了Python支持的正则表达式的元字符和语法：

![Python支持的正则表达式的元字符和语法](/i//2013-12-03-2.png) <center>*Python支持的正则表达式的元字符和语法*</center>

#### 数量词的贪婪模式和非贪婪模式

**贪婪模式**：总是尝试匹配尽可能多的字符串<br/>
**非贪婪模式**：总是尝试匹配尽可能少的字符串

**Python里的数量词默认是贪婪的**

EG：正则表达式`ab*`如果用于查找`abbbc`将找到`abbb`而如果使用非贪婪的数量词`ab*?`将找到`a`

#### 反斜杠的问题

正则表达式中使用反斜杠`\`作为转义字符，这就有可能造成反斜杠困扰

如果你需要匹配文本中的字符`\`，那么使用编程语言的的正则表达式需将需要4个反斜杠`\\\\`：

第一个和第三个用于在编程语言里将第二个和第四个转移成反斜杠，转换成两个反斜杠`\\`后再在正则表达式中里转义成一个反斜杠用力啊匹配

这显然是非常麻烦的，Python中的原生字符串很好的解决了这个问题，这个例子中的正则表达式可以使用`r"\\"`表示，同样匹配一个数字`\\d`也可以写成`r"\d"`

### Python中的re模块

Python中的re模块提供对正则表达式的支持

使用re模块的一般步骤是：

1. 现将正则表达式的字符串形式编译为Pattern实例
2. 然后使用Pattern实例处理文本并获得匹配结果(一个Match实例)
3. 最后使用Match实例获得信息进行其他操作

re应用试验：

``` python
# -*- coding: utf-8 -*-
#一个简单的re实例，匹配字符串中的hello字符串

#导入re模块
import re

# 将正则表达式编译成Pattern对象，注意hello前面的r的意思是“原生字符串”
pattern = re.compile(r'hello')

# 使用Pattern匹配文本，获得匹配结果，无法匹配时将返回None
match1 = pattern.match('hello world!')
match2 = pattern.match('helloo world!')
match3 = pattern.match('helllo world!')

#如果match1匹配成功
if match1:
    # 使用Match获得分组信息
    print match1.group()
else:
    print 'match1匹配失败！'


#如果match2匹配成功
if match2:
    # 使用Match获得分组信息
    print match2.group()
else:
    print 'match2匹配失败！'


#如果match3匹配成功
if match3:
    # 使用Match获得分组信息
    print match3.group()
else:
    print 'match3匹配失败！'
```


