---
title: Android App Lifecycle
category: android
---

Linux 系统将使用唯一的ID来标记每个用户，并且通过ID来管理不用用户的权限。除了 `root` 用户级具有超级权限的用户，每个用户只能访问自己进程内的私有资源。在 Android 系统中，每一个 App 拥有一个独自的 ID，这样便很好的将每个 app 的运行时沙箱环境隔离开。而每个 App 的声明周期便被封装在它对应的 Linux 进程中。
<!--more-->

在 Java 代码中，App 的类影射为 `android.app.Application`。App 将在被调用 `onCreate()` 和 `onTerminate()` 时开始创建和结束。但是这也不是完全可靠的，一个进程可能被 kill 掉在执行 onTerminate() 之前

## App 的创建

当一个 App 的某个组件（activity、service、broadcast receiver、content provider）被触发创建初始化时，Linux 进程将被创建，无论它是否已经正在执行，都会导致系统进行如下工作：

1. 创建并开始执行 Linux 进程
2. 创建运行时环境（divik 或 art）
3. 创建 Application 实例
4. 创建 Application 的入口组件

创建新的进程和运行时换件是笔较大的开销，这会降低系统性能明显影响用户体验。因此，系统为了缩短创建 App 的时间，在系统启动的时候创建了一个特殊的进程 `Zygote`， 它预先加载了所有核心库的集合，所有的 App 便由此进程 fork 出新进程而不用拷贝核心库。

## App 的结束

由于用户可能在不久重新切回运行的程序，所以系统会避免销毁 App 的所有资源直到系统确实需要更多资源来运行其它程序。一个 App 在它的所有组件都被销毁之后仍然不会被自动销毁。

系统需要回收资源时才会真正的销毁一些 App，按照进程的排名，靠后的会被先回收。

- 前台进程：可以看见的activity，与可见的activity绑定的service，正在运行的broadcast receiver
- 可见进程：某些透明半可见的进程
- 服务进程：在后台执行并且没有和可见组件绑定的service
- 后台进程：一些不可见的activity
- 空进程：没有任何组件的进程，保留他们的存在是为了加快启动，但是当系统需要回收资源时会最先销毁

