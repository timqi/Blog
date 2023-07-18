- tags: [android](/tags.md#android)
- date: 2016-12-05

# Android 开发中的 Architecture

移动应用开发的复杂度越来越高，为了应对复杂度的增涨，相应的移动端 architecture 的概念也随之产生。本文就以 android 开发为例谈谈我对移动端复杂单应用架构的看法，其中我们需要先了解为什么需要 architecture，什么情况下需要什么形式的 architecture，然后介绍下当今比较流行的 MVP 是怎样的思路，它解决了什么问题，最后结合现在目前 android 开发的实际情况谈谈在架构上面临着哪些问题。

## Architecture 与 Framework

我们知道 "复用", "解耦" 在软件工程领域是最为锋利的两大武器，在 Android 开发中，Framework 做了很多工作，比如四大组件，比如 View 绘制体系，事件分发体系。在 Framework 的基础上我们可以非常轻松的完成简单应用的开发，就是因为我们高效的重用了 Framework 的代码，如果还不明白什么是 Framework，想想如果你在 android 上写一个使用 NativeActivity 的 pure C/C++ 应用会遇到哪些问题应该就会明白 Java Framework 的优势了，当然 NativeActivity 也是 Android Framework 的一部分，这个话题就另说了。

那么什么是 Architecture，Architecture 在 Web 的中的应用更为广泛一些，比如 php 的 laravel，python 的 django，nodejs 的 express 等等，通常不使用这些 Architecture 时开发一些简单的应用问题也不大，但是使用这些 Architecture 会让业务逻辑表达的更清晰，不同功能的代码合理的分布在他们应该在的地方。这样做的优势也很明显，不同工程师之间合作起来更加容易，每个单元更加容易测试，当你需要搜索相关代码的时候能够快速定位到正确的位置，易于维护。使用这些 Architecture 的优势得益于它做了一件事，解耦。

移动应用开发复杂度越来越高，单纯的靠 Framework 已经很难支撑大团队的并行合作与可扩展性问题。这时候就有了 Architecture 的概念，把业务逻辑解耦出来提高开发效率。

当然 Architecture 与 Framework 的界限并没有特别清晰，Architecture 也包含复用，Framework 也有解耦，其中 Framework 的侵入性更大一点。引入这些词是为了更说明 Architecture 的主要作用：**解耦**。

## MVP

Android 端 Architecture 也不是最近才产生的思想，相信很多同学都有了解，基本的概念我就不再重复了。上面说了为什么需要 Architecture，这段谈谈我对 Architecture 中应用相对广泛的 MVP 的一些见解。

### 什么是 MVP

我们都清楚 MVC，MVP 就是从 MVC 继承发展而来的。那么两者之间有什么区别呢，其实区别不大，如果硬要说的话就是 V 和 P 的通信是双向的。听起来还是比较晦涩，我举个例子，我们知道 Web 开发大多是 MVC，通常你在 V 中进行一个交互比如点了一个连接那么就会定向到一个新的 url 对应一个新的 C，而在 Android 呢，你与 V 发生了一个交互比如点击一个按钮，那个这个事件是会重新转给这个 V 对应的原来的 P 来处理，V 与 P 之间的通信是双向进行的。

### MVP 是怎么样做的

我认为实现 MVP 并没有固定的模式，根据架构师的理解完全可以根据不同业务自行规划。上面说到 Architecture 的主要目的在于解耦。**通常来讲在 Android 的 MVP 中核心思路是把界面展示与数据分割开**。做到数据的改动不会影响到界面展示相关的代码，而且更换不同的 UI 展示也不会影响你数据部分的代码，那么这样的架构基本上是合格的，具体实现上可以有多种方法，不同场景下粒度划分也可能不相同。后面附有一些示例代码。接下来先说说应该怎样实现一个 MVP，比如弹出吐司应该放在 V 还是 P？由谁来控制 ActionBar 的隐藏与展示？

- Presenter

Presenter 更像是 View 与 Model 的中间件。Presenter 需要从 Model 中取出数据并格式化为 View 所需要的形式交由 View 处理。同时 Presenter 也要响应 View 中发来的交互事件，这一点也是 MVP 与 MVC 不太相同的地方

- View

View 通常由 Activity，Fragment，各种 Window 等实现，它从 Presenter 得到了格式化的数据后借助 Android Framework 提供的功能将数据展示出来。View 会持有 Presenter 的句柄，在监听到来自系统交互的消息后将交互消息传递给 Presenter。

- Model

通常 Model 是外界通信与业务逻辑的代理，建立不同的 Model 来描述不同的业务逻辑。在 clean 架构中每个 Model 可能就是一个不同的 interactor 用例。Model 的工作就是提供 View 展示所需要的相关数据。

### 实现：

[MVP 先驱 antoniolg 的 ‘antoniolg/androidmvp’](https://github.com/antoniolg/androidmvp)

例子很简单，通过接口定义了 MVP 各自的行为并分别实现，这里不做过多介绍。

重点推荐：[googlesamples/android-architecture](https://github.com/googlesamples/android-architecture)

这个仓库是 Google 官方提供的模板工程，文档中介绍你甚至可以直接 clone 下来并以此为基础开发你的 App。代码讲述了 mvp 怎样配合 loader 加载数据，怎样结合 databinding，dagger，怎样配合 rxjava 等。实现比较简单，这里不做过多讲解。

## 问题

当然，我认为当今公司遇到的最大问题并不在于怎样采用 MVP，是否采用 MVP。对于小团队，通常一两个人，MVP 的架构反而可能显得拖沓，业务没有进展反而先搞出来一堆的接口。

对于大公司面临的更重要的可能是整合多个产品线的挑战。这不仅仅是面对单一应用进行架构的问题。业务发展到一定阶段，产品线过于复杂，但是很多基础的东西都是通用的，比如日志，灰度，用户系统甚至 IM，地图，怎样把这些模块合理的抽出来并高效的为每个应用服务才是 Android 应用开发在现实中面临的更为迫切的问题。

其次，由于 Android 碎片化历史原因以及不同厂商对 ROM 的更改，造成很多 API 的坑，通过统一的架构工程屏蔽掉这些区别更好的服务于业务开发团队也是非常有必要的。