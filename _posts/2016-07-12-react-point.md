---
title: 如何快速掌握 React
category: web
---

React 在前端工程化方面具有很多优势特性，然而这里面仍存在很多坑。如果单纯的认为使用了 React 框架很多问题就自然解决了，那是不可能的。本文将阐述我对 React 框架的一些见解和使用 React 过程中要重点注意的几个坑。
<!--more-->

首先，要想顺畅的使用 React，前端开发环境如 webpack，babel 等的配置及架构可能就会让你研究很长一段时间。本文假设在读者对这些基本环境有一定的了解的情况下。

## 数据流管理，FLUX 架构

FLUX 是 Facebook 提出的一种构建客户端 WebApp 的架构（当然在 Android，iOS 中也有相关理论），FLUX 的核心观点认为一个优秀的架构中数据流向应该是单向的，这样可以将页面视图的展现与操作逻辑解耦，最终使逻辑操作编程对数据的操作而不是对视图的操作。

![FLUX 数据流向](/i/2016-07-12-1.png)

**一个例子**

在一个 Web 聊天页面中，此时有新的消息进来反应到页面上一方面是顶栏未读消息数加一，另一方面是下面页面展示新进的消息具体内容并高亮显示

我们有几种实现思路：

1. js 面向 DOM 编程

  由 jQuery 直接操作相关 DOM，设置顶栏显示未读消息数 DOM 内容并赋予相关样式，在下面聊天页面添加 DOM 并设置高亮样式

2. MVC

  新消息进入触发 Controller 获取新消息的 Model 模型，通过一些模板框架将 Model 数据灌入 DOM 完成页面展示

3. FLUX

  先定义 store 的结构，这个结构中含有未读消息相关的描述，然后根据这个数据结构编写页面展示部分，新消息进来触发 store 部分内容的改变，从而自动触发页面的更新，这样我们页面的逻辑部分实际上就是对数据 store 的操作并不涉及视图管理

那么，如果需求变为需要在页面种新增一个位置比如侧边栏也显示这个信息：

1. js 面向 DOM 编程

  同样需要寻找到相关 DOM 结构设置内容和样式，逻辑的复杂导致代码越来越难以维护

2. MVC

  在灌入 Model 数据到 View 的时候需要重新考虑新进消息的逻辑，同样逻辑的复杂度导致代码编写的复杂度

3. FLUX

  面对这一需求的变化我们只需要考虑，我们只需求修改根据数据结构编写页面展示部分的代码，完全不用考虑逻辑相关的问题

## React 的 FLUX 思路

```js
var Input = React.createClass({

  getInitialState: function() {
    return {value: 'Hello!'};
  },

  handleChange: function(event) {
    this.setState({value: event.target.value});
  },

  render: function () {
    var value = this.state.value;
    return (
      <div>
        <input type="text" value={value} onChange={this.handleChange} />
        <p>{value}</p>
      </div>
    );
  }
});
```

state 是 React 的每个 Component 中都维护的一个数据结构。我们可以自定义这个结构，在 render 方法根据 state 的数据来编写 Component 的展示形式，同时，可以通过 setState 方法轻松的改变 state 中的数据，而 state 的改变会触发 render 函数进而更新 Component 展现。

在上面的例子中有一个 input 输入框，下方有一个文本能够实时显示输入的内容。

页面的展现是在 render 中对 state 数据的展示，文本变化的逻辑实际上就是对 state 种数据的操作，这样逻辑与页面的解构大大降低了大型业务页面逻辑的复杂度

## React 的优势

1. 结构化

  结构化是 React 在前段工程化推进的重要里程碑，React 中 Component 引入使得前段代码很大程度上可以复用，我们可以借助一些优秀的库比如 materia-ui 快速构建出非常惊艳的 UI

2. 解构

  上文已经说了很多

3. 性能优势

  借助于 Virtual DOM 与 React diff 算法使得 React 能够运行的很快。当然，这个快的速度不是你什么都不用做就能够获得的，这里面有很多坑，需要很多手动优化，比如是否更新 Component ，下文中会稍作介绍。另外在首屏加载速度方面 React 表现的不如原生的性能好，即使我们可以使用 server render 等手段进行优化，但是 React 的首屏加载时间紧紧是逼近原生，无法超越。

## React Component 生命周期

Component 的生命周期管理很容易联想到 Android 中各种组件的生命周期，对组建生命周期的管理是一个优秀的 Framwork 必须要做好的，对 Component 的生命周期的理解让我们知道什么事应该什么时候做。

![React Component 生命周期](/i/2016-07-12-5.png)

其中大部分生命周期回调是很好理解的，我重点说下面这个回掉：

```js
boolean shouldComponentUpdate(
  object nextProps, object nextState
)
```

上文说到 React 性能的优化，重写 shouldComponentUpdate 是很重要的一点，默认情况下 shouldComponentUpdate 返回 true，通过比较 nextProps 和 nextState 我们手动判断是否需要重新刷新组件，避免不必要的组件刷新能够避免很多性能开销。

## React 缺点

使用 React 并不能解决所有问题，事实上，这里仍有很多问题疑难杂症，比如多级 Component 间通信会造成非常混乱的回掉，当然官方也不推荐这样的方法，未解决这个问题，官方推荐采用另外一个 FLUX 框架来管理多层级 Component 的通信，这个逻辑看起来像这样。

![使用 Redux 进行组件间通信](/i/2016-07-12-2.png)

另外在性能优化方面，有很有需要开发者注意的方面，只有注意这些优化点才能达到 Facebook 所称的性能标准，默认情况下框架所做的优化不足以符合预期的性能要求，在移动端。

而且由于前端类库发展过快，很多现在代码可能在下周就不能用了，不能平滑升级带来的开发成本也是比较头疼的问题。
