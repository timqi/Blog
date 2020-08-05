---
title: Android Service
category: android
---

本文相关代码：[Github timqi](https://github.com/timqi/android-code-samples/tree/master/Service)
<!--more-->

Service 是 Android 系统的重要组件之一，与 Activity 不同的是它通常不处理与用户的交互部分，而是为 Activity 等其他组件提供后台数据支持。Service 有它独特的生命周期，可以长时间运行于后台，这也使得 Service 能够处理需要长连接的情况。

## 生命周期

一个 Service 的 java 类需要继承自 android.app.Service 然后重写 onCreate,onStart,onDestroy,onBind,onUnbind 方法，启动 Service 的两种方法：

- **startService()**：即使调用 startService 的线程结束了 Service 仍然存在，直到有线程调用 stopService 或者 Service 调用 stopSelf() 时服务才会结束
- **bindService()**：Service 与调用 bindService() 的线程具有相同的生命周期，也就是说调用 bindService() 的线程结束时 Service 线程也会跟着结束。当然如果主线程调用 unbindService() 时服务也会结束
- **混合使用以上两者**：只有 stopService 后并且也没有与 Service 绑定的线程后它才会被结束

**多次调用 startService() 方法并不会导致多次执行 onCreate 方法创建服务，但是可以多次执行 onStart 方法，也就是说一个 Service 只能会被创建一次**

## 启动 Service

Service 分为本地服务与远程服务，区分这两种服务的方法是看服务的客户端与服务端是否在同一个进程中，如果在同一进程中则是本地服务，不在同一进程中的是远程服务。

开启服务的方式也有两种：startService、bindService

#### startService

当客户端Client调用 startService() 开启服务时，这个服务和 client 已经没有联系了，Server 与 Client 的运行时独立的

#### bindService

bindService 开启一个服务时，这个服务于开启它的 client 存在一种联系，他们可以通过一个 Binder 的对象进行通信

## bindService

客户端 Client 可以调用 bindService() 方法绑定到一个 Service，之后系统会调用系统的 onBind() 方法（如果服务没有被创建还会调用 onCreate）方法，它返回一个用来与 service 交互的 IBinder。

这期间的绑定是异步的，bindService 会立即返回，而且它不会返回 IBinder 对象给客户端，客户端必须创建一个 ServiceConnection 对象的实例并传给 bindService，ServiceConnection 中包含一个回调方法，系统调用这个方法来传递要返回的 IBinder。

**只有 activities, services, 和c ontentproviders 可以绑定到一个 service 不能从一个 broadcastreceiver 绑定到service。**

将客户端与一个 Service 绑定时需要：

1. 实现一个 ServiceConnection 接口，重写两个回调方法：
	- onServiceConnected()：系统调用这个函数来传送在 service 的 onBind() 中返回的 IBinder。
	- OnServiceDisconnected()：系统在同 service 的连接意外丢失时调用这个函数。比如当 service 崩溃了或被强杀了．当客户端解除绑定时，这个方法不会被调用。
2. 调用 bindService()，传给它 ServiceConnection 的实现
3. 当系统调用 onServiceConnected() 方法时，就可以使用接口定义的方法们开始调用 service 了。
4. 要与 service 断开连接，调用 unbindService()。

### 注意事项

- 对象引用的计数是跨进程进行的
- 应该在客户端的生命周期内是绑定与接触绑定配对的进行
	- 如果需要在 Activity 可见是使用 Service，则需要在 onStart 中绑定在 onStop 中解绑
	- 如果需要 Activity 即使停止也能使用 Service 则需要在 onCreate 与 onDestroy 中绑定与解绑，这需要 Activity 整个运行周期使用 Service，如果 Service 在另一个进程中，这增加了 Service 的负担容易被系统杀死
	- 一般不要在 onResume 与 onStop 中进行绑定与解绑
