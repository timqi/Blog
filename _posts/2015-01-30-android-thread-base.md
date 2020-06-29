---
title: Android 线程基础
category: android
---

在 Java 环境总提供了管道、共享内存、阻塞队列等机制来实现线程间通信。但是在安卓环境下通常是 UI 线程与和它相关的后台线程通信，同时不能使用任何可能造成 UI 线程阻塞的机制
<!--more-->

![](/i//2015-01-30-1.png)

- android.os.Looper
	A message dispatcher associated with the one and only consumer thread.
- android.os.Handler
	Consumer thread message processor, and the interface for a producer thread to
- insert messages into the queue. A  Looper can have many associated handlers, but
	they all insert messages into the same queue.
- android.os.MessageQueue
	Unbounded linked list of messages to be processed on the consumer thread. EveryLooper —and  Thread —has at most one  MessageQueue .
- android.os.Message
	Message to be executed on the consumer thread.

其中要完成的工作：

1. Insert: The producer thread inserts messages in the queue by using the  Handler connected to the consumer thread.
2. Retrieve: The  Looper , discussed in “Looper” on page 58, runs in the consumer thread and retrieves messages from the queue in a sequential order.
3. Dispatch: The handlers are responsible for processing the messages on the consumer thread. A thread may have multiple  Handler instances for processing messages; the  Looper ensures that messages are dispatched to the correct  Handler

![](/i//2015-01-30-2.png)

## 例子

``` java
public class LooperActivity extends Activity {
	LooperThread mLooperThread;

	private static class LooperThread extends Thread {
		public Handler mHandler;
		public void run() {
			Looper.prepare();
			mHandler = new Handler() {

				public void handleMessage(Message msg) {
						if(msg.what == 0) {
						doLongRunningOperation();
					}
				}
			};
		Looper.loop();
		}
	}

	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		mLooperThread = new LooperThread();
		mLooperThread.start();
	}

	public void onClick(View v) {
		if (mLooperThread.mHandler != null) {
			Message msg = mLooperThread.mHandler.obtainMessage(0);
			mLooperThread.mHandler.sendMessage(msg);
		}
	}

	private void doLongRunningOperation() {
		// Add long running operation here.
	}

	protected void onDestroy() {
		mLooperThread.mHandler.getLooper().quit();
	}
}
```

## 消息传递中用到的类：

#### MessageQueue

#### MessageQueue.IdleHandler

#### Message

消息分为数据消息和任务消息，其中的数据包含：

![](/i//2015-01-30-3.png)

消息对象通常被存放在整个App范围内的消息池中重复利用：

![](/i//2015-01-30-4.png)

#### Looper

每个线程只能关联一个 Looper，而一个 Looper 只能关联一个消息队列，将这个消息队列中的消息分发给线程去执行。所以，一个线程对应一个消息队列，但是可以有很多线程向这个消息队列中加入任务

默认情况只有只有 UI 线程拥有 Looper，他在 App 的所有组件创建前被创建。这个 Looper 的终止或者关联到其他线程都会产生运行时错误。

#### Handler

Handler 是具有插入消息与处理消息的双向功能。无论生产者或消费者线程都会使用 Handler 做一下典型的工作：

- 创建消息
- 将消息插入队列
- 在消费者线程处理消息
- 管理队列中的消息

每个 Handler 必须要关联到 Looper 才能正常完成工作。一个线程可以拥有多个 Handler。

![](/i//2015-01-30-5.png)

