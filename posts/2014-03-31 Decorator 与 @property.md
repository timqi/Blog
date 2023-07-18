- tags: [python](/tags.md#python)
- date: 2014-03-31

# Decorator 与 @property

装饰器 (Decorator) 在 Python 中使用 @ 表示，可以将函数作为参数传递给装饰器调用。@property 装饰器用于类中把函数修饰为类的一个属性而不是方法。

## 装饰器的基本知识

- 装饰器分为**带参数的装饰器**与**不带参数的装饰器**
- 不带参数的装饰器：是一个把被它装饰的函数作为参数调用的函数
- 带参数的装饰器：返回值是一个不带参数的装饰器，使用这个返回的装饰器来装饰函数
- 不管带不带参数，都要返回一个函数。在调用被装饰的函数的时候实际上得到的就是装饰器函数以被装饰函数为参数的返回值

## 不带参数的装饰器：

```python
def deco(func):
    pass

@deco
def foo():
    pass

# 等价于
foo = deco(foo)

```

## 带参数的装饰器

```python
def deco(args):
    pass

@deco(args)
def foo():
    pass

# 等价于
foo = deco(args)(foo)

```

## 使用多个装饰器

不带参数：

```python
@deco1
@deco2
def foo():
    pass

# 等价于
foo = deco1(deco2(foo))

```

带参数:

```python
@deco1
@deco2(args)
def foo():
    pass

# 等价于
foo = deco1(deco2(args)(foo))

```

## 关于 @property

@property 的主要功能是将一个函数作为类的属性访问,如：

```python
class Parrot(object):
    def __init__(self):
        self._voltage = 100000

    @property
    def voltage(self):
        """Get the current voltage."""
        return self._voltage

```

这样就为类 Parro t定义了一个只读属性 voltage， 如果 p 是 Parrot 的一个实例，那我我们就可以通过 p.voltage 来访问到 voltage 函数的返回值。这个属性默认是只读的，如果想让该属性可以这样写：

```python
@voltage.setter
def voltage(self, value):
    self._voltage = value

```

**注意：** 在 Python3 中规定只有继承自 Object 的类才能使用 @property