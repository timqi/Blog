---
title: JavaScript中可能的一些坑
category: web
---

众所周知 JavaScript如今已广泛应用在Web编程领域，但它的诞生却是在 10 天之内，虽然操刀设计的大神很牛，但也难免留下了不少的后遗症，同时在应用领域为保证兼容很多问题也没有得到很好的解决，此时就要求开发者在程序开发的过程中注意避免错误。首先让人迷惑的就是JavaScript标准规范的命名，为了让JavaScript成为全球标准，几个公司联合ECMA（European Computer Manufacturers Association）组织定制了JavaScript语言的标准，被称为ECMAScript标准。由于JavaScript是网景的注册商标所以标准就以ECMAScript（简称ES）保留下来。
<!--more-->

## 变量作用域

JavaScript设计之初变量可以直接使用，不需要var声明，而且作用域都是全局的，也就是挂在window变量上的。这显然是不合适的，尤其是在多个js文件中声明了形同变量名的情况下。因此ECMA推出了strict模式，要求使用变量前需要var关键字声明，否则会提示错误。

如果var在函数内部声明，则变量的作用域在整体函数。同时JavaScript函数会扫描函数内所有语句将变量声明语句提到最前，称为**变量提升**。

```javascript
'use strict';
function foo() {
    var x = 'Hello, ' + y;
    console.log(x);
    var y = 'Bob';
}
foo();
```

虽然是strict模式，但上面的代码不会报错，console会输出`Hello, undefined`。

ES6中引入了let关键字用于声明块级作用域，如在for循环中的变量：

```javascript
'use strict';
function foo() {
    var sum = 0;
    for (let i=0; i<100; i++) {
        sum += i;
    }
    // SyntaxError:
    i += 1;
}
```

## 对象的key与Map结构

JavaScript中对象的key都是字符串类型，如果字符串满足变量命名条件（只包含字母 $, _, 数字，且不能数字打头）则可以直接写成key值，否则需要写成字符串形式如`middle-school`。

```javascript
var xiaohong = {
    name: '小红',
    'middle-school': 'No.1 Middle School'
};
```

JavaScript对象简单的可以简单的用于Map数据结构，但它的key只能是字符，这是个问题，所以ES6中引入了Map类型，Map类型的key可以是任意类型的对象元素。

```javascript
var m = new Map([['Michael', 95], ['Bob', 75], ['Tracy', 85]]);
m.get('Michael'); // 95
```

## for...in 与 for...of

for...in 循环会取出对象中所有属性逐一遍历，包括对象继承来的属性。**对Array对象除了会遍历列表的index（整型）外还会遍历对象的其他赋值属性**。

```javascript
var a = ['A', 'B', 'C'];
a.field = 'Haha';
for (var i in a) {
    console.log(i); // '0', '1', '2', 'field'
    console.log(a[i]); // 'A', 'B', 'C', 'HaHa'
}
```

**for...of** 是ES6中引入的语法，解决了 for...in 循环会带上所有field的问题，for...of 用于iterable遍历。只循环数组，Map，或Set集合中的元素。forEach是ES5.1中引入的Array，Set，Map等数据结构的一个遍历方法：

```javascript
var a = ['A', 'B', 'C'];
或 var s = new Set(['A', 'B', 'C']);
或 var m = new Map([[1, 'x'], [2, 'y'], [3, 'z']]);
a.forEach(function (element) {
    console.log(element);
});
```

## undefined与null

`undefined`并不是JavaScript的关键字，而是一个全局变量，表示某个变量没有定义。而null表示某个变量定义了，但是没有值。

因为undefined是一个变量，为了避免变量无意中被篡改等情况，有些规范要求使用`void 0`来替代undefined，其中void操作是将任意变量转换为undefined。

## 反引字符串

JavaScript使用`\``来方便声明**多行字符串**或**模板字符串**。

```javascript
var message =
`这是一个
多行
字符串`;
var message = `你好, ${name}, 你今年${age}岁了!`;
```

## 行末分号

JavaScript引擎有一个自动在行末添加`;`的机制。这可能会导致问题，需要开发的时候时刻留心分号问题，建议手动写好分号位置。

```javascript
function foo() {
    return
        { name: 'foo' };
}
//将被转成如下代码引发问题
function foo() {
    return; // 自动添加了分号，相当于return undefined;
        { name: 'foo' }; // 这行语句已经没法执行到了
}
```

## arguments

arguments是JavaScript的关键字，用在函数中引用函数的传入参数。

```javascript
function foo(x) {
    console.log('x = ' + x); // 10
    for (var i=0; i<arguments.length; i++) {
        console.log('arg ' + i + ' = ' + arguments[i]); // 10, 20, 30
    }
}
foo(10, 20, 30);
```


## sort高阶函数

sort是数组类型的一个方法，但是sort默认会将数组元素转化为字符串类型然后排序，同时会根据ASCII码区分大小写，这容易引发一些误解：

```javascript
['Google', 'Apple', 'Microsoft'].sort(); // ['Apple', 'Google', 'Microsoft'];
['Google', 'apple', 'Microsoft'].sort(); // ['Google', 'Microsoft", 'apple']
[10, 20, 1, 2].sort(); // [1, 10, 2, 20]

//正确整型数组排序方法
[10, 20, 1, 2].sort(function (x, y) {
    return x - y;
});
```

## 包装对象

我们知道java中int和Integer类型是一组包装对象，JavaScript中也存在这种机制，我们可以结合new关键字和类型如Number、Boolean、String声明一个对象类型的元素，他们的值和原来一样，但是类型是`object`，所以使用`===`比较时会得到false值。

```javascript
typeof new Number(123); // 'object'
new Number(123) === 123; // false

typeof new Boolean(true); // 'object'
new Boolean(true) === true; // false

typeof new String('str'); // 'object'
new String('str') === 'str'; // false
```

所以尽量不要特意使用包装对象，另外`null`的类型也是object。但是，如果使用Number、Boolean、String直接声明变量不适用`new`关键字那么变量则不是包装对象，这是非常梦幻的地方。

```javascript
var n = Number('123'); // 123，相当于parseInt()或parseFloat()
typeof n; // 'number'

var b = Boolean('true'); // true
typeof b; // 'boolean'

var b2 = Boolean('false'); // true! 'false'字符串转换结果为true！因为它是非空字符串！
var b3 = Boolean(''); // false

var s = String(123.45); // '123.45'
typeof s; // 'string'
```

所以总结如下规则：

- 不使用`new Number()`, `new Boolean()`, `new String()`创建对象
- 使用 `parseInt()`, `parseFloat()`将类型转换为number
- `String()`或对象`toString()`方法将类型转为string，null对象或undefined类型没有toString方法
- 使用`Array.isArray(myVar)`判断数组类型，`myVar===null` 判断是否为null
- 使用`typeof myVar === 'undefined'`判断变量是否存在

## 关于Date

JavaScript的月份范围是`0~11`，这绝对是设计者当时蒙圈搞出来的。同样如果使用`Date.parse('')`解析出来的日期如果getMonth()的取值范围依然是`0~11`，这点一定要注意。

```javascript
var d = new Date(2015, 5, 19, 20, 15, 30, 123);
d; // Fri Jun 19 2015 20:15:30 GMT+0800 (CST)

var d = Date.parse('2015-06-24T19:49:22.875+08:00');
d; // 1435146562875

var d = new Date(1435146562875);
d; // Wed Jun 24 2015 19:49:22 GMT+0800 (CST)
d.getMonth(); // 5
```

## JSON规范

ECMA标准规定JSON中字符串必须使用双引号`""`，utf8字符集，Object的键也必须用双引号括起来。

## 错误处理

我们知道JavaScript使用 try...catch...finally 语法来捕获错误信息，如果当前发生错误但没有编写 try...catch 代码，被抛出的错误会向上层传递。但是如果是在回调函数中抛出的错误那么很有可能该错误无法被捕获处理

```javascript
function printTime() {
    throw new Error();
}
//无法捕获运行错误
try {
    setTimeout(printTime, 1000);
    console.log('done');
} catch (e) {
    console.log('error');
}
```

因此要在printTime内部填在try...catch错误处理函数。