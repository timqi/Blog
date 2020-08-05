---
title: Effective Java - 并发
category: java
---

为了提高程序的性能，尤其是当下多核 CPU 环境下，使用多线程技术是很好的选择。Java 1.5 后在多线程编程方面提供了很多简化工具，比如各种集合如 List，Set，Map 的线程安全版实现，CountDownLatch 等待唤醒等，使多线程编程的难度大大降低。但是这里我们仍然要注意一些问题与技巧如要同步访问共享的可变数据等。
<!--more-->

- [同步访问共享的可变数据](#同步访问共享的可变数据)
- [避免过度同步](#避免过度同步)
- [优先使用 Executor 和 Task 而不是线程](#优先使用-Executor-和-Task-而不是线程)
- [优先使用并发工具而不是 wait 和 notify](#优先使用并发工具而不是-wait-和-notify)
- [将程序的线程安全性记录到文档中](#将程序的线程安全性记录到文档中)
- [小心的使用延时初始化](#小心的使用延时初始化)
- [不要依赖于线程调度器](#不要依赖于线程调度器)
- [避免使用线程组](#避免使用线程组)

## 同步访问共享的可变数据

**synchronized** 关键字保证了只有一个方法能够执行否则就将它阻塞。如果不进行同步，不仅会造成变量被随机修改的问题，同时也可能变量的改变对其他线程也不可见。Java 语言保证了除了 long 和 double 类型之外的数据的读或写操作是原子的，也是就是说你即使不添加同步机制，只要不实用 long 或 double 类型数据就可以多线程并发的修改变量。

由于 Java 的内存模型，如果需要在多线程间通信也需要进行同步，比如我们编写一个程序从一个线程结束另外一个线程：

```java
public class StopThread {
	private static boolean stopRequested;

	public static void main(String[] args) throws InterruptedException {
		Thread backgroundThread = new Thread(new Runnable() {
			public void run() {
				int i = 0;
				while (!stopRequested)
					i++;
			}
		});
		backgroundThread.start();

		TimeUnit.SECONDS.sleep(1);
		stopRequested = true;
	}
}
```

上述程序中的 backgroudThread 不会停止运行，因为没有同步机制，backgroudThread 无法检测到 stopRequested 变量值的改变，jvm 虚拟机会进行下面的优化：

```java
while (!done)
	i++;

// compile to:
if (!done)
	while (true)
		i++;
```

进行同步化优化：

```java
public class StopThread {
	private static boolean stopRequested;

	private static synchronized void requestStop() {
		stopRequested = true;
	}

	private static synchronized boolean stopRequested() {
		return stopRequested;
	}

	public static void main(String[] args) throws InterruptedException {
		Thread backgroundThread = new Thread(new Runnable() {
			public void run() {
				int i = 0;
				while (!stopRequested())
					i++;
			}
		});
		backgroundThread.start();

		TimeUnit.SECONDS.sleep(1);
		requestStop();
	}
}
```

读方法与写方法都要进行 synchronized。事实上不对 stopRequested 同步它的读与写操作也是同步的，这里的 synchronized 仅仅是为了在不同线程之间通信使用。然而这方方法每次读写 stopRequested 时都要进行加锁解锁操作影响程序性能，我们可以使用下面的方法优化：

```java
public class StopThread {
	private static volatile boolean stopRequested;

	public static void main(String[] args) throws InterruptedException {
		Thread backgroundThread = new Thread(new Runnable() {
			public void run() {
				int i = 0;
				while (!stopRequested)
					i++;
			}
		});
		backgroundThread.start();

		TimeUnit.SECONDS.sleep(1);
		stopRequested = true;
	}
}
```

使用 **volatile** 关键字保证了任何线程获取相关对象值的时候获取到的都是最新的。但是也不能随意的使用 volatile，比如下面例子，不能保证并发操作的原子性：

```java
// Broken - requires synchronization!
private static volatile int nextSerialNumber = 0;
public static int generateSerialNumber() {
	return nextSerialNumber++;
}
```

为了解决上面的问题，我们使用同步的方法，幸运的是 jdk 为我们提供了丰富的用于并发的工具，如 [java.util.concurrent.atomic](https://github.com/openjdk-mirror/jdk7u-jdk/tree/master/src/share/classes/java/util/concurrent/atomic)

```java
private static final AtomicLong nextSerialNum = new AtomicLong();
public static long generateSerialNumber() {
	return nextSerialNum.getAndIncrement();
}
```

但是最好的避免上面提到的问题的方法就是不在不同线程之间共享可变数据，只在单一进程中处理可变数据。但是很多时候我们需要在不同线程之间共享可变数据，那么一定要保证这些数据是同步访问的，或者使用 volatile 保证数据的改变能够及时被发现。

## 避免过度同步

频繁的加锁解锁操作不但会影响程序性能，而且过多锁还可能会产生死锁和很多不可测问题。

为了避免由于同步造成的线程保活与安全问题，永远不要将你的客户端程序置于同步的代码中，考虑下面的观察者模式：

```java
public class ObservableSet<E> extends ForwardingSet<E> {
	public ObservableSet(Set<E> set) {
		super(set);
	}

	private final List<SetObserver<E>> observers = new ArrayList<SetObserver<E>>();

	public void addObserver(SetObserver<E> observer) {
		synchronized (observers) {
			observers.add(observer);
		}
	}

	public boolean removeObserver(SetObserver<E> observer) {
		synchronized (observers) {
			return observers.remove(observer);
		}
	}

	// This method is the culprit
	private void notifyElementAdded(E element) {
		synchronized (observers) {
			for (SetObserver<E> observer : observers)
				observer.added(this, element);
		}
	}

	@Override
	public boolean add(E element) {
		boolean added = super.add(element);
		if (added)
			notifyElementAdded(element);
		return added;
	}

	@Override
	public boolean addAll(Collection<? extends E> c) {
		boolean result = false;
		for (E element : c)
			result |= add(element); // calls notifyElementAdded
		return result;
	}
}
```

Observers 通过 addObserver 方法订阅，通过  removeObserv 取消订阅。SetObserver<E> 生明为：

```java
public interface SetObserver<E> {
// Invoked when an element is added to the observable set
	void added(ObservableSet<E> set, E element);
}
```

通常情况下，上述模式是能够正常工作的，但是考虑一些极端的情况，比如要在 addObserver 中删除这个观察者本身：

```java
set.addObserver(new SetObserver<Integer>() {
	public void added(ObservableSet<Integer> s, Integer e) {
		System.out.println(e);
		if (e == 23) s.removeObserver(this);
	}
});
```

如果上述代码在同一线程中运行，将会得到 0 到 23 的输入，然后抛出异常 CocurrentModificationException，因为我们在遍历一个列表的过程中试图修改移除这个列表中的元素。此外，假设我们在其他的线程中执行这个移除操作：

```java
public class Test {
	public static void main(String[] args) {
		ObservableSet<Integer> set = new ObservableSet<Integer>(
				new HashSet<Integer>());

		// Observer that uses a background thread needlessly
		set.addObserver(new SetObserver<Integer>() {
			public void added(final ObservableSet<Integer> s, Integer e) {
				System.out.println(e);
				if (e == 23) {
					ExecutorService executor = Executors
							.newSingleThreadExecutor();
					final SetObserver<Integer> observer = this;
					try {
						executor.submit(new Runnable() {
							public void run() {
								s.removeObserver(observer);
							}
						}).get();
					} catch (ExecutionException ex) {
						throw new AssertionError(ex.getCause());
					} catch (InterruptedException ex) {
						throw new AssertionError(ex.getCause());
					} finally {
						executor.shutdown();
					}
				}
			}
		});

		for (int i = 0; i < 100; i++)
			set.add(i);
	}
}
```

我们不会得到异常，因为我们将陷入死锁。s.removeObserver 视图获取锁，而主线程中已经获取了这个锁正等待 s.removeObserver 完成，从而两者陷入等待，产生死锁。

虽然上述例子只是为了说明，在生产环境中很难看到。但是这也足够引起重视，不要将客户端代码置于同步环境中。对于上面的代码产生的问题也很容易修复，比如我们可以进行防御性复制，将 observers 的快照返回给观察者：

```java
// Alien method moved outside of synchronized block - open calls
private void notifyElementAdded(E element) {
	List<SetObserver<E>> snapshot = null;
	synchronized(observers) {
		snapshot = new ArrayList<SetObserver<E>>(observers);
	}

	for (SetObserver<E> observer : snapshot)
		observer.added(this, element);
}
```

此外，我们还能使用 Java 1.5 中提供的并发集合如 [java.util.concurrent.CopyOnWriteArrayList](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/util/concurrent/CopyOnWriteArrayList.java)，CopyOnWriteArrayList 集合数据的改变都会引发集合中数据的复制，通常这样看起来可能很消耗系统资源，但是在当下情况非常合适：

```java
// Thread-safe observable set with CopyOnWriteArrayList
private final List<SetObserver<E>> observers =
	new CopyOnWriteArrayList<SetObserver<E>>();

public void addObserver(SetObserver<E> observer) {
	observers.add(observer);
}
public boolean removeObserver(SetObserver<E> observer) {
	return observers.remove(observer);
}
private void notifyElementAdded(E element) {
	for (SetObserver<E> observer : observers)
		observer.added(this, element);
}
```

此外，同步带来的性能问题也不容忽视，我们可以分为提供并发与非并发场景下的 API 来提高性能，比如 StringBuffer 与 StringBuilder。

## 优先使用 Executor 和 Task 而不是线程

[java.utils.concurrent.Executors](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/util/concurrent/Executors.java#L71) 为我们封装了几个常用的线程池模型，和配套的任务队列来组织任务调度，我们要做的就是根据需要来创建线程池与任务队列并编写 Runnable 放入线程池中去执行即可。

同时 [java.util.concurrent.ScheduledThreadPoolExecutor](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/util/concurrent/ScheduledThreadPoolExecutor.java) 具备替代 [java.util.Timer](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/util/Timer.java) 的功能。如果 Exectors 中没有需要的线程池类型，我们可以使用 [java.util.concurrent.ThreadPoolExecutor](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/util/concurrent/ThreadPoolExecutor.java#L315) 定制特定的线程池类型。有关线程池的相关知识本文不做过多讲述。

## 优先使用并发工具而不是 wait 和 notify

Java 1.5 后为了们提供了强大的并发编程工具，我们要利用好这些工具来降低并发编程的难度而不是使用最原始的 wait 和 notify。

[java.util.concurrent](https://github.com/openjdk-mirror/jdk7u-jdk/tree/master/src/share/classes/java/util/concurrent) 包中提供了 Executor 框架，并发访问集合，和 synchronizers。

jdk 中提供了支持并发访问的 List, Queue, and Map。他们内部处理了并发问题，编程期间不用对它们做同步化，即使做了外部同步化对它们来讲也没有什么效果，只是增加了性能负担而已。对于 Map 集合，优先使用并发性能更好的 ConcurrentHashMap 而不是 Collections.synchro- nizedMap 或 Hashtable。

Synchronizers 为一个线程等待另一个线程提供了可能，最常用的 Synchronizers 有 [java.util.concurrent.CountDownLatch](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/util/concurrent/CountDownLatch.java)，它大大降低了并发编程的复杂度，假设我们需要编写：所有的工作线程要在秒表开始计时前进行准备，当最后一个工作线程准备好了秒表线程开始计时，然后工作线程开始工作，等待最后一个工作线程完成任务后完成及时，

```java
public class ConcurrentTimer {
	private ConcurrentTimer() {
	} // Noninstantiable

	public static long time(Executor executor, int concurrency,
			final Runnable action) throws InterruptedException {
		final CountDownLatch ready = new CountDownLatch(concurrency);
		final CountDownLatch start = new CountDownLatch(1);
		final CountDownLatch done = new CountDownLatch(concurrency);

		for (int i = 0; i < concurrency; i++) {
			executor.execute(new Runnable() {
				public void run() {
					ready.countDown(); // Tell timer we're ready
					try {
						start.await(); // Wait till peers are ready
						action.run();
					} catch (InterruptedException e) {
						Thread.currentThread().interrupt();
					} finally {
						done.countDown(); // Tell timer we're done
					}
				}
			});
		}

		ready.await(); // Wait for all workers to be ready
		long startNanos = System.nanoTime();
		start.countDown(); // And they're off!
		done.await(); // Wait for all workers to finish
		return System.nanoTime() - startNanos;
	}
}
```

上述示例中使用了三个 CountDownLatch：ready，start，done 分别来使秒表等待准备结束，使工作线程等待开始工作，使秒表等待工作结束。上面的逻辑如果使用 wait 与 notify 实现会非常繁琐。

**尽可能使用并发工具而不是 wait 和 notify 来处理并发**

但是对于 wait 和 notify，这里有一点需要注意，**所有 wait 调用需要放在 while 循环中，对于唤醒操作使用 notifyAll 而不是 notify，因为 notify 很难保证能够唤醒目标线程**

wait 的一个模式，

```java
// The standard idiom for using the wait method
synchronized (obj) {
	while (<condition does not hold>)
		obj.wait(); // (Releases lock, and reacquires on wakeup)
	... // Perform action appropriate to condition
}
```

## 将程序的线程安全性记录到文档中

synchronized 关键字并不会被 javadoc 自动记录到文档中，而且 synchronized 并不能决定代码是否线程安全。因为我们要在文档中详细说明代码是否线程安全。

线程安全性有几个级别：

- immutable，不可变类，如 String，Long，都是线程安全的
- unconditionally thread-safe，对象的内部虽然有可变对象，但是在对象内部维护了锁，对于客户端来讲是线程安全的
- conditionally thread-safe，相比于上一条的来讲，这种情况指类的某些方法是线程安全的而另外一些是线程不安全的
- notthread-safe，类本身是线程不全的，但是可以通过客户端程序来维护线程安全性
- thread-hostile，完全线程不安全的

对于线程安全性，我们要详细记录客户端应该怎样使用来保证安全，具体到某个类，某个方法用了那个锁，应该怎样获取锁等。

## 小心的使用延时初始化

我们可以使用延时初始化的方法优化程序性能，但是延时初始化在面对并发问题时可能会产生很多错误。为了进一步提高程序性能并且避免并发引起的错误，通常我们有两种延迟初始化方法

- 如果你需要初始化一个静态域变量，那么可以为这个变量包裹一层类

```java
// Lazy initialization holder class idiom for static fields
private static class FieldHolder {
	static final FieldType field = computeFieldValue();
}
static FieldType getField() { return FieldHolder.field; }
```
因为 Java 语言保证了类的静态域初始化是同步的。

- 使用二次校验发来延迟初始化类的属性域

```java
// Double-check idiom for lazy initialization of instance fields private volatile FieldType field;
FieldType getField() {
	FieldType result = field;
	if (result == null) {  // First check (no locking)
		synchronized(this) {
			result = field;
			if (result == null)  // Second check (with locking)
				field = result = computeFieldValue();
		}
	}
	return result;
}
```

二次校验的延迟初始化类保证程序性能的同时将锁的作用域最小化，如果你能够接受变量初始化代码可能被调用多次，那么可以使用 volatile 结合一次校验来完成延时初始化

```java
// Single-check idiom - can cause repeated initialization! private volatile FieldType field;
private FieldType getField() {
	FieldType result = field;
	if (result == null)
		field = result = computeFieldValue();
	return result;
}
```

## 不要依赖于线程调度器

通常线程调度是由操作系统来实现的，Java 程序不可控，如果此时依赖线程调度，优先级类似的方案来保证线程的安全性和执行状态的是不合适的。

## 避免使用线程组

线程组对象 ThreadGroup 已经在 jdk 中逐渐被放弃，应该避免使用。

[Thread’s setUncaughtExceptionHandler](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/lang/Thread.java#L1954) 提供了监听线程错误方法。
