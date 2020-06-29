---
title: Effective Py - Metaclasses 与 Attribute
category: python
---

Metaclasses 为 Python 语言提供了有关类本身运行时的信息，学习 Metaclasses 的使用也能够让我们更好的理解 Python 的运行机理。本文涉及的 `@property`, `__get__`, `__set__`, `__getattr__`, `__setattr__`, `__getattribute__`, `__new__` 等方法的运行机制。
<!--more-->


- [直接使用属性而不是 get,set 方法](#直接使用属性而不是-get-set-方法)
- [使用 @property 避免重构](#使用-@property-避免重构)
- [对复用的 @property 使用 Descriptor](#对复用的-@property-使用-Descriptor)
- [懒加载 __getattr__,__getattribute__,__setattr__](#懒加载-__getattr__-__getattribute__-__setattr__)
- [使用 Metaclass 验证子类](#使用-Metaclass-验证子类)
- [使用 Metaclasses 注册现有类](#使用-Metaclasses-注册现有类)
- [通过 Metaclasses 获取类的属性信息](#通过-Metaclasses-获取类的属性信息)


## 直接使用属性而不是 get,set 方法

像 Java 语言建议使用 getter，setter 对属性进行封装，但是 Pythonic 的方式建议直接使用公有 property。随着迭代的进行发现真的需要 setter 方法逻辑来限制值的范围、类型时可以0成本将代码迁移到 @property, @property.setter 的方法，调用相应属性处的代码依然不用修改。

```python
class BoundedResistance(object):
    def __init__(self, ohms):
        self._ohms = ohms
        
    @property
    def ohms(self):
        return self._ohms
        
    @ohms.setter
    def ohms(self, ohms):
        if ohms <= 0:
            raise ValueError
        self._ohms = ohms
```

使用 @property.setter 也可以使类的某个属性变得只读不可写。使用 @property 时要注意在相关 getter、setter 方法中不要修改或影响其他变量以免产生误解。

## 使用 @property 避免重构

上节我们介绍了 @property 的使用方法。通常在早期写程序时我们直接使用 attribute 的方式完成逻辑，然后需要在对 attribute 赋值或获取时添加业务逻辑，此时可以用 @property 加函数的方式达到目的，不必重构业代码。

## 对复用的 @property 使用 Descriptor

如果同一个类中多个 attribute 都有相同的 @property 方法限制他们的存取逻辑，为了 @property 的代码重用可以使用 Descriptor 的方式。descriptor 类提供了 `__get__`, `__set__` 方法来限制 attribute 。

```python
class Grade(object):
	def __init__(self):
		self._value = 0

    def __get__(self, instance, instance_type):
        return self._value
        
    def __set__(self, instance, value):
        if not (0 <= value <= 100):
        	raise ValueError
        self._value = value
        
class Exam(object):
    math_grade = Grade()
    english_grade = Grade()
    science_grade = Grade()
```

这样便不用对 math_grade,english_grade,science_grade 分别使用 property 属性了。但是上面的代码有个问题，math_grade,english_grade 等是在 Exam 类中共享的，新创的 e2 修改了 math_grade 会影响 e1 的值也收影响。

```python
e1 = Exam()
e1.math_grade =  80
e1.english_grade = 90
print('e1 Math: ', e1.math_grade)
print('e1 English: ', e1.english_grade)

e2 = Exam()
e2.math_grade = 82
print('e2 Math: ', e2.math_grade)
print('e1 Math: ', e1.math_grade)
# e1 Math:  80
# e1 English:  90
# e2 Math:  82
# e1 Math:  82	<-- Error
```

为解决上面的问题，需要在 Grade 中保存一个对每个 instance 的引用来存储他们的值，同时这里需要注意使用 WeakKeyDictionary 避免内存泄露。

```python
class Grade(object):
    def __init__(self):
	    self._value = WeakKeyDictionary()

    def __get__(self, instance, instance_type):
        if instance is None: return self
        return self._value.get(instance, 0)
        
    def __set__(self, instance, value):
        if not (0 <= value <= 100):
        	raise ValueError
        self._value[instance] = value
```

## 懒加载 __getattr__,__getattribute__,__setattr__

Python 语言提供了很多 hook。其中当每次访问类的 attribute（类中 `__dict__`字典）**无法找到**的时候变会调用 `__getattr__` 方法，这种模式非常适合懒加载。

```python
class LazyDB(object):
    def __init__(self):
        self.exists = 5
        
    def __getattr__(self, name):
        value = 'Value for %s' % name
        setattr(self, name, value)
        return value
        
data = LazyDB()
print('Before: ', data.__dict__)
print('foo:    ', data.foo)
print('After:  ', data.__dict__)
# Before:  {'exists': 5}
# foo:     Value for foo
# After:   {'exists': 5, 'foo': 'Value for foo'}
```

Python 语言的另一个 hook `__getattribute__` 会在**每次**访问类属性时调用。

```python
class ValidatingDB(object):
    def __init__(self):
        self.exists = 5
        
    def __getattribute__(self, name):
        print('Called __getattribute__(%s)' % name)
        try:
            return super().__getattribute__(name)
        except AttributeError:
            value = 'Value for %s' % name
            setattr(self, name, value)
            return value
        
data = ValidatingDB()
print('Before: ', data.exists)
print('foo:    ', data.foo)
print('After:  ', data.foo)
# Called __getattribute__(exists)
# Before:  5
# Called __getattribute__(foo)
# foo:     Value for foo
# Called __getattribute__(foo)
# After:   Value for foo
```

系统内建的的 `hasattr`,`getattr` 方法也是同样的机制，每次调用这些方法都会调用到 `__getattribute__` ，查询 instance 内建的 `__dict__` 中如果没有相关键值时会调用 `__getattr__`。

同样的，每次为属性赋值时都会调用 `__setattr__` 方法， 这里没有必要区分对待。

```Python 
class SavingDB(object):
    def __setattr__(self, name, value):
        super().__setattr__(name, value)
```

注意使用 `__getattribute__`,`__setattr__` 时要使用 super() 为类的属性赋值，否则会引起循环调用。

## 使用 Metaclass 验证子类

首先，Metaclasses 是继承自 `type` 的类，他有 `__new__` 方法，当与他关联的类被创建的时候会触发 `__new__`。

```python
class MetaClass(type):
    def __new__(meta, name, bases, class_dict):
        print(meta, name, bases, class_dict)
        return type.__new__(meta, name, bases, class_dict)
        
class MyClass(object, metaclass=MetaClass):
    stuff = 123
    
    def __init__(self, value):
        print(self, 'Run in __init__')
        self._value = value
        print(self, 'Called __init__')
    
t = MyClass(1)
# <class '__main__.MetaClass'> MyClass (<class 'object'>,) {'__module__': '__main__', '__qualname__': 'MyClass', 'stuff': 123, '__init__': <function MyClass.__init__ at 0x7f226d97ae18>}
# <__main__.MyClass object at 0x7f226dc10780> Run in __init__
# <__main__.MyClass object at 0x7f226dc10780> Called __init__
```

上面是 Python3 的写法，在 Python2 中使用 `__metaclass__` attribute 来表示与他关联的 MetaClasses。

```python
class MyClassInPython2(object):
	__metaclass__ = MetaClass
```

由于 Metaclass 的特殊调用时间，我们可以想到在 `__new__` 中检查创建类的参数是否合法。

```python
class ValidateSomeClass(type):
    def __new__(meta, name, bases, class_dict):
        if bases != (object, ):
            if not class_dict['some_attr_wrong']:
                raise ValueError
        return type.__new__(meta, name, bases, class_dict)
```

## 使用 Metaclasses 注册现有类

如果想用 json 来对对象进行序列化与反序列化，试想序列化很简单直接使用 json.dumps 即可，但是反序列化的时候便不知道要将 json 字符反序列化成什么类型了。我们想到可以在系列化的时候讲类的类型作为字段写入 json 中，反序列化时根据这个字段生成相应对象。

```python
def register_clss(target_class):
	target_class.register[target_class.__name__] = target_class

class Meta(type):
    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        register_class(cls)
        return cls
        
class RegisteredSerializable(Serializable, metaclass=Meta):
    pass

class SomeClass(RegisteredSerializable):
    pass
```

## 通过 Metaclasses 获取类的属性信息

假设你想用了一类来映射数据库中的一行，你可能会写

```python
class Field(object):
    def __init__(self, name):
	    self.name = name
	    self.internal_name = '_' + self.name;

    def __get__(self, instance, instance_type):
        if instance is None: return self
        return getattr(instance, self.internal_name, '')
        
    def __set__(self, instance, value):
        setattr(instance, internal_name, value)
        

class Customer():
    first_name = Field('first_name')
    last_name = Field('last_name')
```

上面例子中 Field 类可以很好的操作 Customer 对象中的属性，也就是 `__dict__`，但是定义 Customer 的属性时 first_name 要写两遍，显得很繁琐，使用 MetaClass 修改如下：

```python
class Meta(type):
    def __new__(meta, name, bases, class_dict):
        for key, value in class_dict.items():
            if isinstance(value, Field):
                value.name = key
                value.internal_name = '_' + key
        cls = type.__new__(meta, name, bases, class_dict)
        return cls

class Field(object):
    def __init__(self, name):
	    self.name = None
	    self.internal_name = None

class DBRow(object, metaclass=Meta):
    pass

class Customer(DBRow):
    first_name = Field('first_name')
    last_name = Field('last_name')
```

MetaClass 结合 Descriptor 很好的解决了问题，同时避免内存泄露。