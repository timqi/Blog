- tags: [android](/tags.md#android)
- date: 2016-03-20

# Context in Android

Context 非常常见，经常会使用到 Context 来完成一些需求。比如：

1. 加载资源文件
2. 启动一个新 Activity
3. 获得系统服务
4. 或取内部文件存储路径
5. 创建新的 View
6. ...

在 Android 系统文档中是这样介绍的：

> Interface to global information about an application environment. This is an abstract class whose implementation is provided by the Android system. It allows access to application-specific resources and classes, as well as up-calls for application-level operations such as launching activities, broadcasting and receiving intents, etc.
> 

这个类是一个抽象类，提供了程序运行的基本环境。作为抽象类，他的实现并不总是相同的，具体实现依赖于不同的 Android 换件组件。比如 Application, Activity/Service, BroadcastReceiver, 等等

### Application

Application 类是一个运行在应用程序进程空间中的单例对象，你可以在 Activity/Service 中通过 getApplication() 方法或者其他继承自 Context 的类的 getApplicationContext() 方法中得到 Application 对象，所有得到的对象都是进程中的同一个对象。

### Activity/Service

他们继承自 ContextWrapper，实现了相同的有关 Context 的 API，但是都把这些方法调用代理到了他们内部的 Context 实例上，这就是我们所知的 base Context。当系统创建新的 Activity 或 Service 实例的时候也同时创建了一个新的 ContextImpl 实例来实现特定的服务需求。每个 Activity 或 Service 内部的 Context 实例都是唯一了，不会在不同对象间共享。

### BroadcastReceiver

BroadcastReceiver 本身并没有实现 Context 的相关方法，但是系统在 BR 收到通知事件的时候会将 Context 传入 onReceive() 方法中。这时在 onReceive 方法中的 Context 实例的 registerReceiver() 和 bindService() 方法是没有权限访问的，每次 BroadcastReceiver 收到的都是新的 Context 实例

### ContentProvider

ContentProvider 本身也不是 Context，但是 CP 在创建完成的时候会被传入一个 Context，我们可以通过 getContext() 方法来获取这个 Context 实例。如果此时 CP 与调用者运行在同一个进程中，那么这时获取的 Context 就是本地 Application 的单例划对象；如果此时的 CP 与调用者进程运行不同的进程中，那么获取的 Context 就是此时 CP 运行进程的包信息。

## Context 的引用

我们首先需要注意的是每个 Context 都有它自己独特的生命周期，如果你在一个对象中引用了相关 Context，例如你创建了一个单例工具类，需要通过 Context 引用来加载资源文件或访问 ContentProvider 而把当前 Actiity 或 Service 的 Context 保存在这个工具类中。

```java
public class CustomManager {
    private static CustomManager sInstance;

    public static CustomManager getInstance(Context context) {
        if (sInstance == null) {
            sInstance = new CustomManager(context);
        }

        return sInstance;
    }

    private Context mContext;

    private CustomManager(Context context) {
        mContext = context;
    }
}

```

这个例子中不安全的地方是我们不知道传入的 Contex 到底来自哪里，如果这个 Context 是一个 Activity 或者 Service，那么这时保存的 Context 引用就会造成 Activity 以及与它相关的 View 等组件不能顺利被垃圾回收，从而造成内存泄露问题。

为了解决这个问题我们通常在工具类中使用 Application 的 Context：

```java
public class CustomManager {
    private static CustomManager sInstance;

    public static CustomManager getInstance(Context context) {
        if (sInstance == null) {
            //Always pass in the Application Context
            sInstance = new CustomManager(context.getApplicationContext());
        }

        return sInstance;
    }

    private Context mContext;

    private CustomManager(Context context) {
        mContext = context;
    }
}

```

Application 的 Context 本身就是单例的，这样我们就不用担心传入不同的 Context 会造成的内存泄露问题。但是**为什么我们不能直接使用** Application 的 Context 而是从 Context 的 getApplicationContext() 方法中获取呢，这是因为 Application Context 也不是唯一的，可能不有不同。

另外可能会因为 Context 造成内存泄露的原因可能是在后台线程或者 Handler 中静态保存了 Context 的引用。

## Conext 的适用范围

[Untitled Database](2016%2003%2020%20Context%20in%20Android%20%5Bandroid%5D%20fc2397b2309d408d9ae1e468fddb5c7f/Untitled%20Database%207838484722c84475bfca63c02fbf58d9.csv)

- N1: 事实上 Application 的 Context 可以启动一个 Activity，但是这个启动的过程会为 Activyt 创建新的任务站，这样的启动逻辑可能并不是你预想的那样
- N2: 这样的操作是合法的，但是此时 inflate 出来的 UI 组件不会包含你提前设置好的主题，因为只有 Activity 组件在加载的时候才会载入主题相关的配置
- N3: 如果 receiver 为 null 的话那么这个操作是被允许的，这通常用在 Android 4.2 及以上系统中来保存 stricky broadcast 的值

## 矛盾

当我们需要长时间保存一个 Context 引用并且这个引用需要用到 UI 相关函数 的时候似乎只能够保存 Activity 的引用。但是这样是不合理的，如果必须要这样做说明很有可能 app 的某些地方需要重新设计了。

最佳实践的经验是一般情况下你可以保存你正在使用的组件的引用，但是这个引用的生命周期不能超过系统相关组件的周期，如果在你的系统组件将要被回收的时候仍要需要保存 Context 的应用那么你需要将这个引用切换为 Application 的 Context。