---
title: Effective Py - 类与继承
category: python
---

Python 作为一门面向对象的编程语言，支持继承、多态、封装全部特性。Python 中的类和继承可以简洁明了的表述对象行为，为复杂环境快速改变需求提供了有利支持，知道它们是如何工作的会让你的代码可维护性更强。
<!--more-->

- [使用字典和元组编写工具类](#使用字典和元组编写工具类)
- [简单的接口使用函数而不是类](#简单的接口使用函数而不是类)
- [使用 @classmethod 多态的构造对象](#使用-@classmethod-多态的构造对象)
- [使用 super 初始化父类](#使用-super-初始化父类)
- [只在 mixin 场景中使用多重集成](#只在-mixin-场景中使用多重集成)
- [倾向于使用公有属性而不是私有的](#倾向于使用公有属性而不是私有的)
- [继承自 collections.abc 来自定义容器类型](#继承自-collections-abc-来自定义容器类型)

## 使用字典和元组编写工具类

Python 内建的字典类型可以很好的维护类的声明周期中的状态。比如你想记录一些学生的成绩，并且事前你不知道他们的名字：

```python
class SimpleGradeBook(object):
	def __init__(self):
		self._grades = {}

	def add_student(self, name):
		self._grades[name] = []

	def report_grade(self, name, score):
		self._grades[name].append(score)

	def average_grade(self, name):
		grades = self._grades[name]
		return sum(grades) / len(grades)
```

此时如果需求变了，需要你记录每个学生每个学科的成绩，可能你会把学科名作为 \_grades 字典的值的序列的 key，成绩作为 value:

```python
def report_grade(self, name, subject, score):
	by_subject = self._grades[name]
	grade_list = by_subject.setdefault(subject, [])
	grade_list.append(score)
```

如果这是需求又变了，需要你在计算平均分是需要为每个学科加权，那么你可能会想直接在 grade_list 中 append 一个二元数组:

```python
def report_grade(self, name, subject, score):
	by_subject = self._grades[name]
	grade_list = by_subject.setdefault(subject, [])
	grade_list.append((score, weight))
```

最开始，你不知道这套系统要支持加权，所以最开始使用一个帮助类似乎并不紧急，Python 内建的字典就可以很好的维护这些状态。但是随着逻辑复杂度增加，内建字典可能并不足以管理这些状态，尤其是用字典作为字典的值这种方式，会使程序晦涩难懂。

当你意识到问题的时候，你应该编写工具类重构这些代码以更好的封装数据，同时这样也将类的接口与实现解耦开了。类的重构需要自下而上仔细分析，此例中首先是 Grade 对象，如果封装成类显得有些重了，使用元组可能是个不错的选择，因为 grades 数据都是不可修改的，使用 (score, weight) 元组来描述 grades。


但是如果需求想要附加一个字段来存储老师对成绩的点评，可能你会想扩充元组为 (score, weight, notes) 来表示 grade，同时修改每处使用到 grade 的地方，用 `_` 占位（`_` 符号在 Python 中便利的表示没用的变量）

```python
total = sum(score * weight for score, weight, _ in grades)
total_weight = sum(weight for _, weight, _ in grades)
```

使用这种方法扩充 grade 的问题是如果将来继续增加字段将使程序不易维护，这时你可以考虑使用 namedtuple,

```python
import collections
Grade = collections.namedtuple('Grade', ('score', 'weight'))
```

构建函数中可以使用位置参数或者关键字参数来构建这个类，同时可以通过 name 访问相应字段的值，并且随着复杂度上升可以随时将 namedtuple 重构为类。但是 namedtuple 同样存在问题，一个是不能为 nametuple 指定默认值，这在某些情况下会造成困扰；另一个问题是即使 namedtuple 可以通过 name 访问值，但是也可以通过 index 的索引方式访问，如果在程序中使用了 index 方式同样会使程序不易维护。

好了，我们确定了 Grade，那么就可以编写一个类表示一门学科了，一个类表示一个学生了，然后一个类表示所有学生的成绩了

```python
class Subject(object):
	def __init__(self):
		self._grades = []

	def report_grade(self, score, weight):
		self._grades.append(Grade(score, weight))

	def average_grade(self):
		total, total_weight = 0, 0
		for grade in self._grades:
			total += grade.score * grade.weight
			total_weight += grade.weight
		return total / total_weight

class Student(object):
	def __init__(self):
		self._subjects = {}

	def subject(self, name):
		if name not in self._subjects:
			self._subjects[name] = Subject()
		return self._subjects[name]

	def average_grade(self):
		total, count = 0, 0
		for subject in self._subjects.values():
			total += subject.average_grade()
			count += 1
		return total / count

class Gradebook(object):
	def __init__(self):
		self._students = {}

	def student(self, name):
		if name not in self._students:
			self._students[name] = Student()
		return self._students[name]
		
```

## 简单的接口使用函数而不是类

Python 内建的很多 API 使用函数作为接口，比如 list 的 sort 方法能接受一个可选的 key 参数

```python
names = ['Socrates', 'Archimedes', 'Plato', 'Aristotle']
names.sort(key=lambda x: len(x))
```

Python 中函是第一类对象（First-Class object），Python 中一切皆对象，函数也不例外。函数作为一个对象，那么它就可以被返回、被赋值、存储在容器中、被当做参数传递等。

看下面一个例子，defaultdict 是一个数据结构，允许传入一个函数在字段中找不到相应 key 是触发调用，我们编写一个逻辑，在 dict 中找不到 key 时打印日志：

```python
def log_missing():
	print('key added')
	return 0

current = {'green': 12, 'blue': 3}
increments = [('red', 5), ('blue', 17), ('orange', 9)]
result = defaultdict(log_missing, current)
print('Before: ', dict(result))
for key, amount in increments:
	result[key] += amount
print('After: ', dict(result))
#Before:  {'green': 12, 'blue': 3}
#key added
#key added
#After:  {'green': 12, 'blue': 20, 'red': 5, 'orange': 9}
```

上面的代码通俗易懂，逻辑清晰。如果此时需要你在 missing 中记录到底有几个 key 是确实的应该怎么办呢，首先我们想到可以在闭包中存储一个状态：

```python
def increment_with_reporter(current, requirments):
    added_count = 0
    
    def missing():
        nonlocal added_count
        added_count += 1
        return 0
    
    result = defaultdict(log_missing, current)
    for key, amount in increments:
	    result[key] += amount
	    
	return result, added_count
```

这段代码似乎就不太好理解了，涉及到闭包，同时在闭包中存储了一个状态变量。前面*函数*相关的章节我们也说过要避免这种使用，使用类来维护状态变化：

```python
class CountMissing(object):
	def __init__(self):
		self.added = 0

	def missing(self):
		self.added += 1
		return 0

counter = CountMissing()
result = defaultdict(counter.missing, current)
for key, amount in increments:
	result[key] += amount

assert counter.added == 2
```

使用类相比闭包的形式更清楚，但是从类中仍然难以看出代码编写的目的，只有到了 defaultdict 的时候我们才能了解到类的作用。为了避免这种情况，我们使用 Python 类的默认方法 `__call__` 为这个类提供可调用的功能：

```python
class BetterCountMissing(object):
	def __init__(self):
		self.added = 0

	def __call__(self):
		self.added += 1

counter = BetterCountMissing()
counter()
assert callable(counter)
result = defaultdict(counter, current)
```

我们可以看到对于不需要维护状态的工具段代码使用函数是最佳选择，如果需要维护状态那么使用类更加方便，同时类的 `__call__` 方法为类提供了可调用的能力

## 使用 @classmethod 多态的构造对象

Python 语言中不仅对象可以多态，类同样也支持多态。假设我们有如下代码来处理类的集成

```python
class InputData(object):
    def read(self):
        raise NotImplementedError
        
        
class PathInputData(InputData):
    def __init__(self, path):
        super().__init__()
        self.path = path
        
    def read(self):
        return open(self.path).read()
```

如果我们又有一个从网络读取数据的类，此时我们可能会再写一个类继承自 InputData 来处理，然后再 MapReduce worker 中使用这些数据：

```python
class Worker(object):
    def __init__(self, input_data):
        self.input_data = input_data
        self.result = None
        
    def map(self):
        raise NotImplementedError
        
    def reduce(self, other):
        raise NotImplementedError
        
        
class LineCountWorker(Worker):
    def map(self, input_data):
        data = self.input_data.read()
        self.result = data.count('\n')
        
    def reduce(self, other):
        self.result += other.result
 ```

当代码运行起来是看起像想这样：


```python
def generate_inputs(data_dir):
    for name in os.listdir(data_dir):
        yield PathInputData(os.path.join(data_dir, name))
        
def create_workers(input_list):
    workers = []
    for input_data in input_list:
        workers.append(LineCountWorker(input_data))
    return workers
    
def execute(workers):
    threads = [Thread(target=w.map) for w in workers]
    for thread in threads: thread.start()
    for thread in threads: thread.join()
    
    first, rest = workers[0], workers[1:]
    for worker in rest:
        first.reduce(worker)
    return first.result
    
def mapreduce(data_dir):
    inputs = generate_inputs(data_dir)
    workers = create_workers(inputs)
    return execute(workers)
```

我们发现 mapreduce 函数的代码非常不通用，如果我们继承产生新的 InputData 或者 Worker 类时你仍然需要重写 generate_inputs,create_workers 方法然后适配 mapreduce 方法。

原因在于 python 中的 `__init__` 构造方法不能通用多态的调用，我们使用 @classmethod 来实现多态。

```python
class GenericInputData(object):
    def read(self):
        raise NotImplementedError
        
    @classmethod
    def generate_inputs(cls, config):
        raise NotImplementedError
        

class PathInputData(GenericInputData):
    def read(self):
        return open(self.path).read()
        
    def generate_inputs(self, config):
        data_dir = config['data_dir']
        for name in os.listdir(data_dir):
            yield cls(os.path.join(self.data_dir, name))
            
            
class GenericWorker(object):
    def map(self):
        raise NotImplementedError
        
    def reduce(self, other):
        raise NotImplementedError
        
    @classmethod
    def create_workers(self, input_class, config):
        workers = []
        for input_data in input_class.generate_inputs(config['data_dir']):
            workers.append(cls(input_data))
        return workers
```

## 使用 super 初始化父类

传统的我们使用类似 `MyBaseClass.__init__()` 的方法初始化父类。但是这样会产生很多问题，尤其是在多重集成（应该避免）的时候。多重集成使用上面的方法初始化类时会带来初始化顺序不一样，父类拥有共同祖先时会重复执行祖先的 `__init__` 等问题。

Python2.2 之后引入了 super 机制，使用深度优先，从右到左的顺序初始化父类，并且保证祖先类只初始化一次。在 python2 中初始化一个类形如：

```python
class BaseClass(object):
    def __init__(self, value):
        self.value = value
        print(__class__)
        
        
class TimesFive(BaseClass):
    def __init__(self, value):
        super(TimesFive, self).__init__(value)
        self.value *= 5
        print(__class__)
        
        
class PlusTwo(BaseClass):
    def __init__(self, value):
        super(PlusTwo, self).__init__(value)
        self.value += 2
        print(__class__)
        
        
class My(PlusTwo, TimesFive):
    def __init__(self, value):
        super(My, self).__init__(value)
        print(__class__)
        
s = My(1)
print(s.value)

# <class '__main__.BaseClass'>
# <class '__main__.TimesFive'>
# <class '__main__.PlusTwo'>
# <class '__main__.My'>
```

Python2 中的 super 语法比较繁琐，而且如果类名变化 super 调用也要跟着变化。python3 中对这些稍作休整引入了 `__class` 变量索引到当前类	，那么原来的语法就变成了 `super(__init__, self).__init__(value)` ，可以省略不写简略成 `super().__init__(value)`。


## 只在 mixin 场景中使用多重集成

Mixin 是把尽可能通用的方法抽出来做为工具的类。如下 ToDcitMixin 类将内存中的对象序列化为字典

```python
class ToDictMixin(object):
    def to_dict(self):
        return self.__traverse_dict(self.__dict__)
        
    def __traverse_dict(self, dict):
    	...

 class BinaryTree(ToDictMixin):
 	def __init__(self, value, left=None, right=None):
 		self.value = value
 		self.left = left
 		self.right = right
```

## 倾向于使用公有属性而不是私有的

Python 中有 public, protect(以单下划线开头) private(以双下划线开头) 属性。在类外访问类的私有属性 `foo.__private_field` 会产生 `AttributeError: 'Myobject' object has no attr '__private_field'`。

类的私有属性在继承的子类中仍然无法访问。因为他会被转化为如下格式 `_MyChildObject__private_field`。当在类外访问 `__private_field` 属性时自然找不到。在类的继承中尽量使用 protected 属性使子类拥有更自由的访问权限。除非想要明确的避免子类与父类命名空间冲突这类问题，否则不要使用 private 属性。

## 继承自 collections.abc 来自定义容器类型

collections.abc 模块定义了一系列容器类型。为系统中 len,[],count,list 等特殊内建方法提供方便。直接继承 list，dict 会使类变得笨重，但是也不要从头构建某个容器类。

collections.abc 模块提供的一些工具容器文档：[https://docs.python.org/3/library/collections.abc.html](https://docs.python.org/3/library/collections.abc.html)

