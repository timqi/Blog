- tags: [android](/tags.md#android)
- date: 2014-11-15

# Activities 生命周期

Android 系统中，每个 Activity 指定了一个用户交互的屏幕单位，然而这些 Activities 都存在他们各自不同的生命周期，也就是他们各自执行创建、暂停、销毁等动作的时机，本文就此展开讨论。

![2014 11 15 Activities 生命周期 [android] c2f1026e183844168fb5c739d030875b/2014-11-15-1.png](/images/2014-11-15-1.png)

上图是官方文档中对生命周期的描述，可以很清晰的看到 Activities 的各种状态之间的转化关系，与其对应的方法。其中每个 Activity 只能在 **Resumed**、**Paused**、**Stopped** 这三种状态下停留，当 Activity 执行 `onCreate` 函数被创建进入 Created 状态后系统会立即执行 `onStart` 与 `onResume` 是其进入 Resumed 状态。

## 暂停与恢复

系统调用 `onPause` 方法进入 Paused 状态，Paused 状态下 Activity 本身是处于半可见状态，比如一下情况会导致 Activity 进入 Paused 状态：

- 下滑半透明的通知栏
- 弹出系统对话框

总之就是该 Activity 不是处在最前但是也能被看到的状态就是 Paused，**这个状态下不执行任何代码**，通常在`onPaused` 函数中要做以下处理：

- 停止动画和一些其他正在进行的活动以释放CPU资源
- 提交一些没有保存的更改，但是不要太重量型的
- 释放系统资源，比如相机、GPS等

在 Paused 状态下系统执行 `onResum` 回复运行状态，onResume 函数与 onPause 相对应。

## 停止与重启

在 Paused 状态下执行 `onStop` 方法会进入 Stopped 状态，此时的 Activity 完全不可见，下列情况会导致进入 Stopped 状态：

- 用户导航到其它app
- 此时有来电接入
- 从app启动了一个新的activity

在 `onStop` 方法中应该进行用户的数据保护，为系统执行 onDestroy 彻底销毁 ACtivity 做准备，同时 `onRestart` 方法与 `onStop` 想对应共同维护好状态转换。

## Activity 的重新创建

在一些特殊情况下系统会直接由 Resumed 状态转换到 Destroyed，比如系统内存不足需要销毁运行的程序与提供内存空间、或者应用进行横屏与竖屏转换需要重新设置相应布局等都需要销毁应用并重新创建。

![2014 11 15 Activities 生命周期 [android] c2f1026e183844168fb5c739d030875b/2014-11-15-2.png](/images/2014-11-15-2.png)

上图介绍了这种状态转换主要依靠 `onSaveInstanceState`、`onRestoreInstanceState` 两个函数进行。