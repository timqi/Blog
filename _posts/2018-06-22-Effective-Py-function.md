---
title: Effective Py - 函数
category: python
---

函数是 Python 开发者组织代码逻辑的第一个强力工具，函数能够把大块逻辑拆分成小片，提高代码的可读性、可维护性，同时也利用代码复用与重构。Python 语言中的函数拥有一些其他语言中没有的特性，显著的增加了开发效率降低了 bug 率。
<!--more-->

- [使用 Exception 而不是返回 None](#使用-Exception-而不是返回-None)
- [了解闭包相关变量的作用域](#了解闭包相关变量的作用域)
- [考虑使用 Generator 而不是 List](#考虑使用-Generator-而不是-List)
- [迭代函数参数时要做防御性措施](#迭代函数参数时要做防御性措施)
- [减少位置参数的干扰](#减少位置参数的干扰)
- [使用关键字参数提供可选动作](#使用关键字参数提供可选动作)
- [使用 None 和文档指定说明动态参数默认值](#使用-None-和文档指定说明动态参数默认值)
- [强制调用者指明关键字参数的 key](#强制调用者指明关键字参数的-key)


## 使用 Exception 而不是返回 None

当编写工具函数的时候**不要赋予 None 某个特殊含义**，二要直接返回相应的 Exception，看下面例子：

```python
def divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None

result = divide(x, y)
if not result:
    print('Invalid!')
```

如果 x, y 相除的结果是 0 会怎样，if 判断的时候无论 result 是 0 还是 None，`not result` 的结果都是 True，会造成误解。修复这个问题的一个方法是直接 raise 相应的 Exception 而不是 None；另一方法方法是返回一个元组 `return False, None`，一个值表示是否出现错误，另一个值表示实际的结果，实际开发中不推荐这种方法。

## 了解闭包相关变量的作用域

我们看下面的例子，使用 helper 函数来对一个数组排序：

```python
def sort_priority(numbers, group):
    found = False
    def helper(x):
        if x in group:
            found = True
            return (0, x)
        return (1, x)
    numbers.sort(key=helper)
    return found

numbers = [8, 3, 1, 2, 5, 4, 7, 6]
group = {2, 3, 5, 7}

found = sort_priority(numbers, group)
print(found)
print(numbers)

#False
#[2, 3, 5, 7, 1, 4, 6, 8]
```

numbers 排序过的结果是正确的，但是 found 的值与我们预想的可能不太一样，这是为什么呢？我们来看一下 Python 解释器会依次从以下作用域中查找一个符号：

1. 当前函数范围
2. 更高一级的作用域单元（这里是 sort_priority 函数）
3. 模块作用域（glabal 域）
4. 解释器内建符号（如 str，len）

如果以上环境中都无法找到这个符号就会触发 NameError。

但是赋值一个变量（符号）就不一样了。**如果在当前作用域下存在这个符号那么就把这个符号赋成新值，如果当前作用域中不存在这个符号那么就将该语句视为声明语句并为该符号赋值。**

helper 函数中的 `found = True` 被解释成了声明语句， 在 helper 函数作用域内声明了变量 found，并赋值为 True，并不会影响到外层变量 found。因此我们便能理解上述代码的运行逻辑。

在 Python3 中引入了 `nonlocal` 关键词，它表示在解释符号的时候应该优先向上层作用域中查找是否存在这个变量而不是优先将语句解释为复制语句。nonlocal 的限制是不会向上溯源的 module 级别（global）。 `nonlocal` 的引入方便了闭包程序的编写，但是一定要注意避免在内部环境中污染外部变量。同样的 `global` 关键字也具有相同作用，只不过 `global` 将变量的查找域上升到模块级别。

出了使用 nonlocal 方法外，我们还可以用 class 封装出变量的作用域，虽然代码长一点但更容易理解，class 的 `__call__` 方法会在 class 作为函数调用是调用：

```python
class Sorter(object):
    def __init__(self, group):
        self.group = group
        self.found = False

    def __call__(self, x):
        if x in group:
            self.found = True
            return (0, x)
        return (1, x)

sorter = Sorter(group)
numbers.sort(key=sorter)
assert sorter.found is True
```

但是再 Python2 中并不支持 nonlocal 关键字，为了实现相同的效果，我们可以使用一个 tricky 的手段，代码也很简单

```python
def sort_priority(numbers, group):
    found = [False]
    def helper(x):
        if x in group:
            found[0] = True
            return (0, x)
        return (1, x)
    numbers.sort(key=helper)
    return found[0]
```

其中 found 是一个可变 list，`found[0] = True` 不会被解释为复制语句，那么解释器像上层寻找符号便索引到了 found 变量。同样的，使用字典或者集合也能实现相同的效果

## 考虑使用 Generator 而不是 List

运算结果是一个序列的最方便的方法就是返回一个 list，比如下面代码计算一长串字符中每个单词起始位置的索引

```python
def index_words(text):
    result = []
    if text:
        result.append(0)
    for index, letter in enumerate(text):
        if letter == ' ':
            result.append(index + 1)
    return result
```

相面的代码相比使用 Generator 的方式有两个问题，一个是每次计算出结果都要进行 append 使代码看上去冗余，另外一个问题是如果 text 数据特别大的话一次读入内存为产生运行时错误。

Generator 是使用 yield 表达式的函数，当这个函数被调用是不是立即运行而是返回一个 iterator，当每次对 iterator 调用内建的 next 函数时，iterator 会执行到 Generator 的下一个 yield 表达式的地方，每次调用 yield 的参数作为 iterator 的返回值。

我们使用 Generator 优化代码：

```python
def index_file(handle):
    offset = 0
    for line in handle:
        if line:
            yield offset
        for letter in line:
            offset += 1
            if letter == '':
                yield offset
```

这样便能应付数据量特别巨大的情况。

## 迭代函数参数时要做防御性措施

上文说到 Generator 的好处，但是 Generator 也很明显，就是函数的调用者必须要意识到他们正在使用 Generator，因为 Generator 只能在第一次遍历时返回正确结果，当第一次遍历完成时再次调用 next 会触发 StopIteration 错误。

```python
def normalize(numbers):
    total = sum(numbers)
    #total = list(sum(numbers))
    result = []
    for value in numbers:
        percent = 100 * value / total
        result.append(percent)
    return result

visits = [15, 35, 80]
percentages = normalize(visits)
print(percentages)
#[11.538461538461538, 26.923076923076923, 61.53846153846154]
```

如上代码计算 list 中每个元素占百分比，但是如果 numbers 是一个 Generator 的话就会产生错误，因为 Generator 只能在 sum 的时候遍历一次，下面的 for 循环中便会异常。解决这个问题的方法就是在需要不止一次遍历序列时防御性的将 numbers 转化为 list。

但是如果数据量非常大，必须要使用 Generator 怎么办呢，我们有两种办法解决，一个是使用返回值为 Iterator 函数的函数作为参数，为了方法使用 lambda 方式：

```python
def read_visits(data_path):
	with open(data_path) as f:
		for line in f:
			yield int(line)

def normalize_func(get_iter):
    total = sum(get_iter())
    result = []
    for value in get_iter():
        percent = 100 * value / total
        result.append(percent)
    return result

percentages = normalize_func(lambda: read_visits(path))
```

另一种方式是构造一个可以 iterate 的 class。Python 中，for 循环或者其他任何需要遍历的地方，遇到 `for x in foo` 的语法真正调用的是 `iter(foo)`, iter 内建函数会调用返回了一个 iterator 对象的 `foo.__iter__` 方法。而 iterator 对象就是实现了 `__next__` 方法的类，然后 for 循环户连续调用 next 内建函数直到遍历完成。

听上去步骤很复杂，但其实就是实现 class 的 `__iter__` 方法作为 Generator:

```python
class ReadVisits(object):
    def __init__(self, data_path):
        self.data_path = data_path

    def __iter__(self):
        with open(data_path) as f:
            for line in f:
                yield line

visits = ReadVisits(path)
percentages = normalize(visits)
```

sum 方法会调用 `ReadVisits.__iter__`  产生一个生成器，然后 for 循环中会再产生一个生成器用来遍历。

## 减少位置参数的干扰

首先介绍一下函数中的 \*args 指 positional argument 列表，\*\*kwargs 指 keywords argument 列表。并且 \*args 必须位于 \*\*kwargs 前面，positional argument 需要位于 keywords argument 之前。

当函数中用到 \*arg 时，比如你需要记录日志：

```python
def log(message, *values):
    if not values:
        print(message)
    else:
        value_str = ', '.join(str(x) for x in values)
        print('%s: %s' % (message, value_str))
        
favorates = [7, 33, 99]
log('Favorate: ', *favorates)
#Favorate: : 7, 33, 99
```

上面的代码可能引起的问题一个是如果 values 是一个生成器的话，\* 操作会直接遍历这个序列导致内存耗尽，使用这种模式时要保证你清楚 \*args 的数量级别。可能引起的另外一个问题是如果将来要增加 log 的传入。

这种方式带来的第二个问题是如果将来修改函数声明添加了新的位置参数那么需要在每个调用该函数的地方做修改，否则可能造成逻辑错误，而且很难排查。

## 使用关键字参数提供可选动作

与其他编程语言一样，Python 可以根据位置调用函数。同时，Python 也可以通过制定关键字以任意顺序调用参数。注意，调用函数时，位置参数必须放在关键字参数的前面，且每个参数只能指定一次。


```python
def reminder(number, divisor):
    return number % divisor
    
reminder(20, 7)
reminder(20, divisor=7)
reminder(number=20, divisor=7)
reminder(divisor=7, number=20)

reminder(number=20, 7)
#SyntaxError: positional argument follows keyword argument
reminder(20, number=7)
#TypeError: reminder() got multiple values for argument 'number'
```

关键字参数虽然需要多写一个字母，但是他的好处也是很明显的。第一在调用函数时参数的意义很明确；第二可以为改参数指定一个默认值提供默认行为；第三使得函数原型的声明可以灵活修改而不影响原来使用关键字调用函数的地方。

## 使用 None 和文档指定说明动态参数默认值

```python
def log(message, when=datetime.now()):
    print("%s: %s" % (when, message))
    
log('log 1')
time.sleep(1)
log('log 2')

#2018-06-23 00:22:18.273427: log 1
#2018-06-23 00:22:18.273427: log 2
```

上面的例子中两次调用 log 函数虽然相隔1秒钟，但是输出的 when  却是相同的。这是因为 Python 中关键字参数的默认值只有在函数被解释器加载时评估一次，随后一直使用。解决这位问题最方便的做法是指定 when 的默认值为 None，并且在文档中说明 when 的默认逻辑

```python
def log(message, when=None):
    """Log message with a timestamp
    
    Args:
        message: Message to print
        when: datetime for when the message occurred
            Default to the present time.
    """
    when = datetime.now() if when is not None else when
    print("%s: %s" % (when, message))
```

于此同时，**对于可变类型的关键字参数也一定要使用 None 和文档来描述改参数的默认值**，否则当默认值被返回时有可能被主程序逻辑修改，在下一次需要返回默认值的情况下造成错误

```python
def decode(data, default={}):
    try:
        return json.loads(data)
    except ValueError:
        return default
        
foo = decode('bad data')
foo['new_key'] = 1
bar = decode('also bad')
bar['another_key'] = 2
print(foo)
print(bar)
#{'new_key': 1, 'another_key': 2}
#{'new_key': 1, 'another_key': 2}
```

## 强制调用者指明关键字参数的 key

Python 对关键字参数的支持使得程序非常灵活易懂。甚至有些情况需要在编写函数时强制调用者明确指明关键字来避免一些误解。比如下面例子：

```python
def safe_division(number, divisor,
                  ignore_overflow=False,
                  ignore_zero_division=False):
    try:
        return number / divisor
    except OverflowError:
        if ignore_overflow:
            return 0
        else:
            raise
    except ZeroDivisionError:
        if ignore_zero_division:
            return float('inf')
        else:
            raise

safe_division(1, 10**500, ignore_overflow=True)
safe_division(1, 10**500, True, False)
```

可以看到函数声明是时使用了关键字参数，但是并没有强制调用者在使用函数时必须指明关键字，上面两种方法都能成功调用函数，但是显然下面直接使用位置参数的方式容易产生混淆，尤其是在参数非常多而且都是一些布尔值的情况下，非常容易出错。面对这种情况要强制调用者指明参数的关键字

在 Python3 中函数声明时使用 \* 可以指明位置参数与关键字参数的分隔位置，\* 之后的关键字参数要求在调用时必须明确指出

```python
def safe_division(number, divisor, *,
                  ignore_overflow=False,
                  ignore_zero_division=False):
    ...
```

但是 Python2 中没有这种语法，我们可以通过 `**` 操作符配合 TypeErrors 指定参数。

```python
def safe_division(number, divisor, **kwargs):
    ignore_overflow = kwargs.pop('ignore_overflow', False)
    ignore_zero_div = kwargs.pop('ignore_zero_div', False)
    if kwargs:
        raise TypeError('Unexpected **kwargs: %r' % kwargs)
    ...
```
