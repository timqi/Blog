- tags: [web](/tags.md#web)
- date: 2019-04-01

# JavaScript线程与异步语法进化

我们知道JavaScript运行环境通常都是单线程的。在浏览器中，JavaScript代码主要运行在主线程，也就是UI线程中，为避免阻塞页面，语言层面提供了异步执行的能力，在浏览器实现的时候会将这些异步任务放到特定的线程去执行如ajax，setTimeout等。同时库支持层面上JavaScript的异步语法也经历了几次重大变化。

单线程是JavaScript的一大特点，也就是说在同一时刻只能做一件事，这使得做DOM操作、图形渲染等工作时不用加锁且行为可以预期，但是单线程运行使得JavaScript在CPU密集型计算领域表现不佳。在JavaScript的线程模型中有一个`函数调用栈`和`任务队列`。调用栈实现了编程语言通常意义上的流程控制，如果循环，函数调用等。对于那些不需要等待后续处理结果的任务可以交由任务队列处理，对于任务又有了正常的即时任务和setTimeout为代表添加的定时任务。然后事件循环处理队列中的任务。

Nodejs环境中同样，可以使用`process.nextTick`向事件循环中添加任务。

基于事件循环的异步模型使JavaScript有处理高吞吐量IO的能力。对于编程开发人员要使用这一特性最直观的接触就是编程语言，JavaScript的异步写法先后经历了Callback,Promise,Generator,Aysnc/Await几个阶段。

## Callback

```jsx
$.ajax({
  url: "type",
  data:1,
  success: function (a) {
    $.ajax({
      url: "list",
      data:a,
      success: function (b) {
        $.ajax({
          url: "content",
          data:b,
          success: function (c) {
            console.log(c)
          }
        })
      }
    })
  }
})

```

最早期，JavaScript使用Callback的方式实现异步。单纯的代码嵌套，加上如果业务逻辑复杂会使得代码难以维护，陷入回调地狱。

## Promise

为了解决“回调地狱”的问题，在ES6中正式引入了Promise对象。Promise本质是JavaScript的对象，封装了异步任务的控制流程，存储着异步执行任务的运算结果，暴露统一的API，用看似同步代码的写法来获取异步消息。

Promise对象有JavaScript引擎提供，它接收两个参数resolve、reject，他们的类型都是函数，供异步任务执行完成后回调使用。其中resolve将任务状态由pending转为resolved，reject将任务状态转为rejected。然后调用Promise的then方法可以触发任务执行，并使用catch方法捕获错误。

```jsx
const promise = new Promise(function(resolve, reject) {
  // ... some code
  if (/* 异步操作成功 */){
    resolve(value);
  } else {
    reject(error);
  }
});

promise.then(function(value) {
  // success
}).catch(function(error) {
  // failure
});

var readFile = require('fs-readfile-promise');

readFile(fileA)
.then(function (data) {
  console.log(data.toString());
})
.then(function () {
  return readFile(fileB);
})
.then(function (data) {
  console.log(data.toString());
})
.catch(function (err) {
  console.log(err);
});

```

## Generator

Promise写法比callback直观易懂的多，但是Generator的出现比Promise更方便处理异步任务。声明一个Generator函数需要使用`*`表示，`yield`表示函数执行暂停，先将yield的值返回给`next`接收函数。Generator的以上特性非常适合处理一些懒加载任务。

```jsx
function* read() {
    console.log(1);
    let a = yield '123';
    console.log(a);
    let b = yield 9
    console.log(b);
    return b;
}
let it = read();
console.log(it.next('213')); // {value:'123',done:false}
console.log(it.next('100')); // {value:9,done:false}
console.log(it.next('200')); // {value:200,done:true}
console.log(it.next('200')); // {value:200,done:true}

```

Promise与可以与Generator搭配使用

```jsx
var bluebird = require('bluebird');
var fs = require('fs');
var read = bluebird.promisify(fs.readFile);
function* r() {
  var content1 = yield read('./2.promise/1.txt', 'utf8');
  var content2 = yield read(content1, 'utf8');
  return content2;
}

```

此时要得到r函数的结果，我们需要对它做一些包装，这里面包装代码做的比较好的有tj大神著名的[co](https://github.com/tj/co)库，具体代码可以参考，非常简单。我们这里简单实现以下：

```jsx
function co(it) {
  return new Promise(function (resolve, reject) {
    function next(d) {
      let { value, done } = it.next(d);
      if (!done) {
        value.then(function (data) { // 2,txt
          next(data)
        }, reject)
      } else {
        resolve(value);
      }
    }
    next();
  });
}
co(r()).then(function (data) {
    console.log(data)//得到r()的执行结果
})

```

## Async、Await

ES2017引入了async函数，使异步函数的声明与调用更加方便，但是本质上async-await还是JavaScript在语言层面上对Generator封装的语法糖。async就是将Generator的`*`替换成了`async`，将`yield`替换成了`await`。async-wait支持在同步写法中捕获错误栈。

```jsx
let bluebird = require('bluebird');
let fs = require('fs');
let read = bluebird.promisify(fs.readFile);

async function r(){
  try{
    let content1 = await read('./2.promise/100.txt','utf8');
    let content2 = await read(content1,'utf8');
    return content2;
  }catch(e){ // 如果出错会catch
    console.log('err',e)
  }
}

```

在Python3语言中很早就引入了Generator和async-await的概念，与JavaScript在语法上有很多相似之处。我们可以发现各种编程语言也存在相互借鉴之处。

## 最终还是Promise

async-await是对Generator写法封装的语法糖，而Generator也是基于Promise实现的，所以JavaScript的异步本质上还是还是基于Promise实现的。那么Promise到底是什么呢。

Promise首先是个JavaScript对象，内部封装了如下字段

- `status`: pending初始，fulfilled成功，rejected失败
- `value`: 异步任务成功的结果
- `reason`: 异步任务失败的原因
- `onResolvedCallbacks`: 异步任务成功的回调函数
- `onRejectedCallbacks`: 异步任务失败的回调函数

Promise的构造参数resolve会处理将Promise转为成功状态，reject会处理将Promise转为失败状态。then函数将回调Promise的各个回调函数并返回对应的Promise对象以支持链式调用。catch，finally也将执行逻辑转到对应的控制流。

至此我们对JavaScript中的单线程、异步模型有了一个宏观的认识。借助Promise的逻辑我们简单窥探了JavaScript异步的控制流程。要更深入的理解Promise的相关原理可以研究一个 [V8中有关Promise的源码](https://github.com/v8/v8/blob/4b9b23521e6fd42373ebbcb20ebe03bf445494f9/src/objects/promise.h)。