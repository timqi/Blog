---
title: Effective Py - Pythonic 思考方式
category: python
---

编程语言的优雅用法通常是它的用户日渐定义积累的，这么多年以来 Python 社区发明了 Pythonic 一词用来形容遵循最佳风格的编程方法。这些风格通常没有在编译器中严格的限制，但都是广大用户多年积累的宝贵经验，遵循这些原则能够让你更好的与人合作，编写更加易懂易维护的代码。了解 Python 禅学，`import this` 试试。本篇简单介绍几条 Pythonic 的思考方式
<!--more-->

- [明确你正在使用的 Python 版本](#明确你正在使用的-Python-版本)
- [遵循 PEP8](#遵循-PEP8)
- [了解 bytes,str,unicode 之间的不同](#了解-bytes-str-unicode-之间的不同)
- [使用帮助函数而不是复杂的表达式](#使用帮助函数而不是复杂的表达式)
- [了解怎样切分序列](#了解怎样切分序列)
- [避免在一次切分中使用 start,end,stride](#避免在一次切分中使用-start-end-stride)
- [使用 list comprehensions 而不是 map,filter](#使用-list-comprehensions-而不是-map-filter)
- [使用 enumerate 而不是 range](#使用-enumerate-而不是-range)
- [使用 zip 来并行处理 iterators](#使用-zip-来并行处理-iterators)

## 明确你正在使用的 Python 版本

系统中的 `python` 命令通常是 python2.7 的一个别名，但是它背后也有能是 python2.6,python2.5 或者 3.x 的某一个版本。 时刻明确你的代码运行在什么环境里。可以使用 `python --version` 查看当前 python 的版本。

python2 与 python3 目前社区都在维护，但是 python2 中已经不会再加入新特性，主要以 bug 修复，增强安全性，增强 python2 到 3 的自动转换兼容性为主。python3 仍会持续加入新的语言特性，如果你要上一个新项目，建议使用 python3。

## 遵循 PEP8

PEP8(Python Enhancement Proposal #8) 是一套代码样式规范，完整条目可以在 [https://www.python.org/dev/peps/pep-0008/](https://www.python.org/dev/peps/pep-0008/) 查看，你应该使用 PEP8 来格式化你的代码以更加愉悦的与其他程序员合作交流，也使你自己的代码更有可维护性。使用 Pylint [https://www.pylint.org](https://www.pylint.org) 检查你的代码是否符合 PEP8。以下简要列举几点 PEP8要求：

**空白字符**

- 使用4个`空格`而不是~~制表符~~作为你代码的层级缩进
- 长表达式的换行需要在原缩进基础上再加一个层级（也就是4个空格）
- 文件中，函数与类定义需要空两行；类中，方法之间需要空一行
- 不要在`列表索引`,`函数调用`,`函数参数赋值`时使用空格；在`变量赋值`时使用一个空格

**命名**

- 函数，变量，和类属性使用 `lowercase_underscore` 格式
- 类实例的保护属性使用 `_leading_underscore` 格式；私有属性使用 `__double_leading_underscore` 格式
- 类和异常(Exception)使用 CapitalizedWord 格式；模块级的变量使用 ALL_CAPS 格式
- 类的实例方法使用 self 作为第一个参数名；类属方法使用 cls 作为第一个参数名

**表达式和语句**

- 使用行内否定 **if a is not b**  ~~if not a is b~~
- 使用表达式判断 list 是否空 **if not somelist**	~~if len(somelist) == 0~~
- 避免一行内使用 if，for, while，except 语句
- 在文件头部 import，并且使用绝对名称 **from bar import foo** ~~import foo~~，如果要使用相对名称 **from . import foo**。库的 import 顺序依次为：标准库，第三方模块，你自己编写的模块。并且这三部分内按字母排序

## 了解 bytes,str,unicode 之间的不同

Python3 中，有两种方式表达字符序列的方式 bytes,str。bytes 指 8 位的二进制值，str 的实例包含了 unicode 编码的字符。而 Python2 中也有两种方法表示字符序列：str,unicode。但是与 Python3 不同，这里的 str 实例是指 8 位的二进制值，unicode 是 unicode 字符。

有很多种把 Unicode 表示为二进制数据（8位二进制值）的方法，最常见的就是 utf8 编码。Python3 中的 str 实例和 Python2 中的 unicode 实例都与二进制编码方式没有关系。要把 unicdoe 字符实例转成二进制编码，需要使用 encode 方法，要把二进制数据转成 unicode 字符需要使用 decode 方法。

编写 Python 代码时，你需要在尽可能远的边界接口上使用 encode 和 decode 处理好编码问题。在核心程序中只处理 Unicode 类型（Python3中的str，Python2中的unicode）并且不要假设任何编码方式，同事严格限制代码输出使用 utf8 编码，这样能够使你的代码能够更好的处理各种文本编码（比如Latin-1，Shift JIS，或者 Big5）。

但是事实上这里仍有两个大坑，一个是在 Python2 中，当字符为 7 位的 ASCII 字符时，unicode 和 str 是一种类型，那么这就意味着：

- 可以使用 `+` 连接 str 和 unicode
- 用等号或者不等号比较 str 和 unicode
- 可以使用 unicode 格式化字符串中的 "%s"

但是再 Python3 中 bytes和 str 完全不同，即使只有 ASCII 字符

另一个坑是在 Python3 中打开的文件默认是 utf8 编码，但是在 Python2 中默认以二进制方式打开，所以下面的代码在 Python3 中运行会报错：

```python
with open("/tmp/random.bin", "w") as f:
	f.write(os.urandom(10))
>>>
TypeError: must be str, not bytes
```

要在 Python3 中解决这个问题，就要在 open 的时候指定以二进制的方式打开文件，即 `open("/tmp/random.bin", "wb")`

## 使用帮助函数而不是复杂的表达式

Python 的语法让它很容易写出在单行并且逻辑复杂难以阅读的代码，把这些复杂的逻辑封装到帮助函数中是一个很好的选择，尤其是这些逻辑可以冲用的情况下。同时 `if/else` 表达式比 `or`，`and`表达式更易于理解。

我们来看一个例子，你需要从一个 queryString 中解析出 rgb 的值，并要求结果为整形以便于后续运算，如果 queryString 中不包含的值默认使用 0，代码或许可以写成这样：

```python
from urllib.parse import parse_qs
my_values = parse_qs("red=5&blue=0&green=",
					 keep_blank_values=True)
red = int(my_values.get("red", [""])[0] or 0)
...

# 使用 if/else 表达式优化
red = my_values.get("red", [""])
red = int(red[0]) if red[0] else 0
...
```

上述代码显然不好理解，我们可以使用函数封装这个逻辑：

```python
def get_first_int(values, key, default=0):
	found = values.get(key, [""])
	if found[0]:
		found = int(found[0])
	else:
		found = default
	return found
red = get_first_int(my_values, "red")
...
```

## 了解怎样切分序列

序列切分可以获得一个序列的子序列，内建的 list,str,bytes 都支持切分，广义上实现了 `__getitem__` 和 `__setitem__` 方法的类都支持切分。基础的切分语法是 `somelist[start:end]	` 。有关切分有几条规则：

- 切分出的序列是 deepcopy 的，修改新序列内的额元素不会影响老序列中的元素
- start 位置上的元素被包含在切分结果中，而 end 上的元素不被包含
- start 置空表示 0，end 置空表示 len(somelist)
- start,end 可以为负数 -n，表示序列倒数第 n 个元素，但如果 n 为 0 时仍表示序列第一个元素
- start,end 都置空时会得到原序列的 copy，b = a[:] `assert b == a and b is not a`
- start,end 在切分语法中没有越界的概念
- 使用切分语法给某个序列赋值会将原序列相应区间替换为右值，即使他们长度不相等

```python
print("Before ", a)
a[2:7] = [99, 22, 14]
print("After ", a)
>>>
Before ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
After ['a', 'b', 99, 22, 14, 'h']
```

## 避免在一次切分中使用 start,end,stride

Python 标准的步长切分语法是 somelist[start:end:stride]，表示 list 中每 stride 个元素取出一个。stride 大于 0 时，切分的顺序从 start 到 end，如果 stride 小于 0，切分的顺序从 end 到 start。stride 的一个常用 trick 是用 -1 比序列倒序	。

```python
>>> x = b'mongoose'
>>> x[::2]
b'mnos'
>>> x[1::2]
b'ogoe'
>>> x[::-1]
b'esoognom'
```

我们可以看到在一次切分中同时使用 start,end,stride 会造成迷惑。`::2` 表示从开始每隔两个选择一个元素，`::-2`表示从最后往前每隔两个选择一个元素还好理解，但是 `2::2`,`-2::-2`,`-2:2:-2`,`2:2:-2` 就会很迷惑了。同时 stride 语法对 utf8 编码的 Unicode 字符的 binary string 可能会产生问题。

如果你确实需要三个参数，那么希望能分两行写，或者是使用 itertools 中的 islice 方式。

```python
b = a[::2] #['a', 'c', 'e', 'g']
c = b[1:-1] #['c', 'e']
```

## 使用 list comprehensions 而不是 map,filter

Python 提供了根据一个 list 生成另外一个 list 的方法，叫做 list comprehension。相比于 map, filter 加 lambda 的方式，使用 list comprehensions 会使程序更加易读

```python
a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
even_squares = [x**2 for x in a if x % 2 == 0]
#[4, 16, 36, 64, 100]

alt = map(lambda x: x**2, filter(lambda x: x % 2 == 0, a))
assert even_squares == list(alt)
```

Dictionary，Set 类型也有自己的 list comprehension 方法

```python
chile_ranks = {"Alice": 1, "Bob": 2, "John": 3}
rank_dict = {rank: name for name,rank in chile_ranks.items()}
#{1: 'Alice', 2: 'Bob', 3: 'John'}
chile_len_set = {len(name) for name in rank_dict.values()}
#{3, 4, 5}
```

同时，除非必要应该避免一次使用两个或两个以上 list comprehension 表达式，否则会使程序变得不易理解。如果需要完成更逻辑复杂的转换，你应该考虑使用帮助函数。

如果序列非常大，应该使用 Generator 表达式，而不是直接使用 list comprehension。比如一个场景是打开一个文件，获得文件每行的长度，如果文件比较小我们使用 list comprehension 把数据读进内存没有问题，

```python
value = [len(x) for x in open("/tmp/my_file.txt")]
```

但是如果文件特别大的情况下这就会产生问题。这时我们应该使用 Generator 来生成列表，没次使用列表数据是挨个加载而不是全部一次加载到内存中。Generator 的语法与 list comprehension 相同，不同的事 Generator 使用 () 而不是 []

```python
it = (len(x) for x in open("/tmp/my_file.txt"))
print(it)
#<generator object <genexpr> at 0x8342583>
print(next(it))
print(next(it))
...
```

Generator 同时也可以用在新的 Generator 中：

```python
roots = ((x, x**2) for x in it)
print(next(roots))
#(16, 4)
```

Generator 的执行效率非常高，你可以放心的使用它，只是需要留心避免嵌套过多层级导致代码难以理解

## 使用 enumerate 而不是 range

```python
for i in range(len(somelist)):
	...

for i, item in enumerate(somelist):
	...

for i, item in enumerate(somelist, 1):
	...
```

enumerate 提供了遍历 iterator 时获取（并指定初始） index 的能力。

## 使用 zip 来并行处理 iterators

Python3 中，zip 使用懒加载的方式并行的从两个或者多个 iterator 中每次取出一个返回:

```python
a = ["a", "b", "c"]
b = [1, 2, 3]
for (ia, ib) in zip(a, b):
    print("{}, {}".format(ia, ib))
#a, 1
#b, 2
#c, 3
```

但是在 Python2 中 zip 会将列表所有数据读入内存，并没有懒加载，如果要在 Python2 中使用懒加载你需要使用 itertools 模块的 izip 功能。

zip 的另外一个问题是如果 a，b 长度不相同的情况下，zip 加载到最短的那个列表结束时便结束循环，如果需要持续到最长列表结束时你需要使用 zip_longest 或者 izip_longest 方法。







