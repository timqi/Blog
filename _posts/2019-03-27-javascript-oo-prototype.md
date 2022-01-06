---
title: JavaScript的面向对象与原型链
category: web
---

面向对象是一种常见的编程思想，Java、C++都非常卓越的实现了面向对象编程。对这些语言少有熟悉的同学都知道Java、C++中存在`类型`,`实例`这两个重要概念来描述面向对象的特性。但是JavaScript并没有特别清晰的类型与实例的概念，JavaScript通过原型链的方法实现面向对象编程的特性，本文就来聊聊相关知识与历史。
<!--more-->

我们知道面向对象是一种思想，它并没有要求能够面向对象的编程语言具体怎样实现，只是规定了一些特性集，如：

- 对象具有唯一性，即使两个相同的对象也不是同一个
- 对象拥有描述它的状态（属性）和行为（方法）
- 对象的状态和行为可以继承

我们的知道Java、C++很好的通过类型与实例的概念成功的实现了面向对象，接下来我们看看JavaScript通过原型链是怎样实现面向对象的。

## 创建对象

JavaScript中没有类型，只有实例，但是我们可以创建原型对象。

```javascript
var Student = {
    name: 'Qi Qi',
    height: 1.8,
    say: function() {
        console.log(this.name + ' is saying...');
    }
}
var allen = {
    name: 'allen'
}
allen.__proto__ = Student;
allen.say()
//allen is saying...
```

JavaScript中`__proto__`属性指向对象的原型，当访问对象的属性或方法会查看当前对象是否含有该元素，如果没有的话去它的原型对象上继续查找，由此我们可以实现原型对象，可以用它来充当类型。

我们从[上文](/2019/03/25/javascript-trap)中了解到JavaScript的设计与开发时间紧任务重，老板还要求与Java相似，这就造成了为什么两种不同的面向对象的实现思路都有诸如`new`,`this`这些概念。new关键字可以调用函数，并且返回一个对象：

```javascript
function Student(name) {
    this.name = name;
    this.say = function() {
        console.log(this.name + ' is saying...');
    }
}

var qiqi = new Student('qiqi');
qiqi.name //"qiqi"
qiqi.say() //qiqi is saying...
```

new用在函数前可以看作类的构造函数，与不使用new的普通函数调用的区别就是这里this绑定了新创建的对象，并且在函数尾添加了`return this;`逻辑，否则函数返回`undefined`。这里原型链的关系是：

```
qiqi/xiaoming/... --> Student.prototype --> Object.prototype --> null
```

同时`new Student()`创建的对象还从原型链上获取了一个`constuctor`属性指向Student函数本身

```javascript
qiqi.constructor === Student.prototype.constructor; // true
Student.prototype.constructor === Student; // true
Object.getPrototypeOf(qiqi) === Student.prototype; // true
qiqi instanceof Student; // true
```

如果上述代码忘了写new直接调用函数会发生错误。如果在strict模式下`this.name`会报错，因为this绑定的是undefined。如果在非strict模式下，this绑定的事window对象，那么`this.name`相当于创建了name全局对象。为避免这种情况发生我们可以使用工厂函数把new封装为内部操作。

```javascript
function Student(props) {
    this.name = props.name || '匿名'; // 默认值为'匿名'
    this.grade = props.grade || 1; // 默认值为1
}
Student.prototype.say = function () {
    alert(this.name + ' is say... ');
};
function createStudent(props) {
    return new Student(props || {})
}
```

## 原型继承

继承是面向对象的一大特点，如果我们需要HighStudent继承Student，自然想到需要的原型链关系。

```
qiqi/xiaoming/... --> HighStudent.prototype --> Student.prototype --> Object.prototype --> null
```

要实现上面的原型链我们可以通过：

1. 在HighStudent构造函数中调用Student函数以初始化继承来的元素
2. 封装inherits函数实现继承，函数中需要一个中间函数F，F的prototype指向Student.prototype，HighStudent的prototype指向F
3. 继续在HighStudent的prototype上完成后续逻辑

```javascript
function inherits(Child, Parent) {
    var F = function(){};
    F.prototype = Parent.prototype;
    Child.prototype = new F();
    Child.prototype.constructor = Child;
}
function Student(props) {
    this.name = props.name || '匿名';
}
Student.prototype.say = function() {
    console.log(this.name + ' is saying...');
}
function HighStudent(props) {
    Student.call(this, props);
    this.grade = props.grade || 1;
}

inherits(HighStudent, Student)

HighStudent.prototype.getGrade = function() {
    console.log(this.name + '\'s grade is ' + this.grade);
}
var qiqi = new HighStudent({name:'qiqi', grade: 10})
qiqi.getGrade() //qiqi's grade is 10
```

在JavaScript中的内置类型，原始类型的包装对象，函数，也是对象，它们也满足原型链的逻辑：

```javascript
var arr = [1, 2, 3];
//arr ----> Array.prototype ----> Object.prototype ----> null
function foo() {
    return 0;
}
//foo ----> Function.prototype ----> Object.prototype ----> null
```

## class继承

ES6中引入了 `class`, `extends`, `constructor` 方法来定义类相关的关系结构，但JavaScript本质上还是通过原型链来实现面向对象的一系列特性的，在此可以理解成对prototype写法的语法包装不做赘述。