- tags: [java](/tags.md#java)
- date: 2016-08-21

# Effective Java - 异常

Java 中的异常机制保证了程序在不正常状态下尽可能自我矫正，同时异常机制也为程序的调试提供了更加丰富的信息。异常是程序在不正常状态下的一种保护机制，对异常的约束通常是靠文档的进行的。但是一套优秀设计的 API 会尽可能详细的将程序运行错误的关键信息有效的传递给客户端代码。

- [只有在发生异常时才使用异常](#%E5%8F%AA%E6%9C%89%E5%9C%A8%E5%8F%91%E7%94%9F%E5%BC%82%E5%B8%B8%E6%97%B6%E6%89%8D%E4%BD%BF%E7%94%A8%E5%BC%82%E5%B8%B8)
- [对可恢复的情况使用受检异常，对编程错误使用运行时异常](#%E5%AF%B9%E5%8F%AF%E6%81%A2%E5%A4%8D%E7%9A%84%E6%83%85%E5%86%B5%E4%BD%BF%E7%94%A8%E5%8F%97%E6%A3%80%E5%BC%82%E5%B8%B8%EF%BC%8C%E5%AF%B9%E7%BC%96%E7%A8%8B%E9%94%99%E8%AF%AF%E4%BD%BF%E7%94%A8%E8%BF%90%E8%A1%8C%E6%97%B6%E5%BC%82%E5%B8%B8)
- [避免不必要地使用受检的异常](#%E9%81%BF%E5%85%8D%E4%B8%8D%E5%BF%85%E8%A6%81%E5%9C%B0%E4%BD%BF%E7%94%A8%E5%8F%97%E6%A3%80%E7%9A%84%E5%BC%82%E5%B8%B8)
- [优先使用标准的异常](#%E4%BC%98%E5%85%88%E4%BD%BF%E7%94%A8%E6%A0%87%E5%87%86%E7%9A%84%E5%BC%82%E5%B8%B8)
- [抛出尽可能能够描述异常状态的异常](#%E6%8A%9B%E5%87%BA%E5%B0%BD%E5%8F%AF%E8%83%BD%E8%83%BD%E5%A4%9F%E6%8F%8F%E8%BF%B0%E5%BC%82%E5%B8%B8%E7%8A%B6%E6%80%81%E7%9A%84%E5%BC%82%E5%B8%B8)
- [每个方法抛出的异常都要有文档](#%E6%AF%8F%E4%B8%AA%E6%96%B9%E6%B3%95%E6%8A%9B%E5%87%BA%E7%9A%84%E5%BC%82%E5%B8%B8%E9%83%BD%E8%A6%81%E6%9C%89%E6%96%87%E6%A1%A3)
- [在细 Exception 的 message 中尽可能描述出错误信息](#%E5%9C%A8%E7%BB%86-Exception-%E7%9A%84-message-%E4%B8%AD%E5%B0%BD%E5%8F%AF%E8%83%BD%E6%8F%8F%E8%BF%B0%E5%87%BA%E9%94%99%E8%AF%AF%E4%BF%A1%E6%81%AF)
- [尽量保证失败的原子性，恢复错误现场](#%E5%B0%BD%E9%87%8F%E4%BF%9D%E8%AF%81%E5%A4%B1%E8%B4%A5%E7%9A%84%E5%8E%9F%E5%AD%90%E6%80%A7%EF%BC%8C%E6%81%A2%E5%A4%8D%E9%94%99%E8%AF%AF%E7%8E%B0%E5%9C%BA)
- [不要忽略异常](#%E4%B8%8D%E8%A6%81%E5%BF%BD%E7%95%A5%E5%BC%82%E5%B8%B8)

## 只有在发生异常时才使用异常

```java
// Horrible abuse of exceptions. Don't ever do this!
try {
	int i = 0;
	while(true)
	range[i++].climb();
} catch(ArrayIndexOutOfBoundsException e) {
}

```

如上一段代码，使用异常进行流程控制显然是不合适的。相比使用 for-each 循环，上面代码的性能是非常差的。一般当代 jvm 虚拟机对 try-catch 中的代码不但没有什么优化，而且还关闭了通用场景下的优化操作，增加了很多不必要的边界条件检查，影响性能。

**异常处理是很长不适合用于程序流程控制的，同样的，一套优秀设计的 API 也不会让它的客户端代码陷于使用异常的流程控制之中。**

比如如果 Iterator 中没有 hasNext 方法，那么 Iterator 的遍历操作很可能回事这样:

```java
// Do not use this hideous code for iteration over a collection!
try {
	Iterator<Foo> i = collection.iterator();
	while(true) {
		Foo foo = i.next();
		...
	}
} catch (NoSuchElementException e) {
}

```

上述代码很显然是不合适的，为了避免这样的流程控制，我们通常会提供一个 state-testing 方法来测试保证对象的合法性来避免产生异常，比如 Iterator 的 hasNext 方法就是一个 state-testing 方法。

## 对可恢复的情况使用受检异常，对编程错误使用运行时异常

Java 中提供了三中 throwables：受检异常，运行时异常，和错误异常。对于什么情况下使用那一类异常是个不好说的问题，本条提供几种常见情况下使用异常的原则。

对可恢复的情况使用受检异常，这点很好理解。而不受检异常有两种：运行时异常，错误异常。对于程序错误使用运行时异常，所有的不受检 throwables 都需要继承自 RuntimeException，通常受检异常都继承自 Exception，当然 Java 语言对这没有明确要求。

## 避免不必要地使用受检的异常

受检异常通常强制客户端程序处理，这使得客户端程序逻辑变得复杂。通常我们可以提供状态检查工具来保证客户端在正确的情况调用 API 来避免异常的产生，比如 Iterator 的 hashNext 方法

## 优先使用标准的异常

使用标准异常能够让程序员快速意识到问题所在，减少了 API 的学习成本，一些常用的标准异常有：

[常用异常](/Users/qiqi/go/src/github.com/timqi/Blog/i/2016-08-21-1.png)

## 抛出尽可能能够描述异常状态的异常

我们暴露给用户的 API 应该是尽可能简单易懂的。对于 API 内部 产生的异常可能需要经过解释再重新抛出给客户端程序，如：

[java.util.AbstractSequentialList](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/util/AbstractSequentialList.java#L86)

```java
/**
* Returns the element at the specified position in this list. * @throws IndexOutOfBoundsException if the index is out of range * ({@code index < 0 || index >= size()}).
*/
public E get(int index) {
	ListIterator<E> i = listIterator(index);
	try {
		return i.next();
	} catch(NoSuchElementException e) {
		throw new IndexOutOfBoundsException("Index: " + index);
	}
}

```

将 NoSuchElementException 转化为 IndexOutOfBoundsException 更易于客户端的理解。

## 每个方法抛出的异常都要有文档

使用 @throws 标签在 javadoc 中注明方法所抛出的每一种异常，以及什么场景会产生这样的异常，客户端程序应该注意什么是非常有必要的。当然如果一个类中多处地方都有可能抛出同一样异常比如 NullPointerException，我们可以将这个异常的文档添加在类的 javadoc 中

## 在细 Exception 的 message 中尽可能描述出错误信息

在 Exception 中提供详尽的错误信息有助于客户端程序排查错误所在。这个错误标识信息首先要包含在 Exception 的输出字符串中，其次尤其是对于受检异常要提供错误信息的 get 函数来获取相关内容，如 IndexOutOfBoundsException，

```java
/**
 * Construct an IndexOutOfBoundsException.
 *
 * @param lowerBound the lowest legal index value.
 * @param upperBound the highest legal index value plus one.
 * @param index      the actual index value.
 */
public IndexOutOfBoundsException(int lowerBound, int upperBound, int index) {
	// Generate a detail message that captures the failure
	super("Lower bound: "   + lowerBound +
		", Upper bound: " + upperBound +
		", Index: "       + index);
	// Save failure information for programmatic access
	this.lowerBound = lowerBound;
	this.upperBound = upperBound;
	this.index = index;
}

```

## 尽量保证失败的原子性，恢复错误现场

这条是指当调用一个方法时，如果这个方法中抛出了异常，那么需将所有元素对象的状态恢复到调用这个方法之前的状态。尽可能少的后续及其他代码的运行环境。

为了恢复错误现场通常有以下几个方法：

- 在执行语句前执行异常检查，如果存在异常则抛出异常，不执行逻辑代码：

```java
public Object pop() {
	if (size == 0)
		throw new EmptyStackException();
	Object result = elements[--size];
	elements[size] = null; // Eliminate obsolete reference
	return result;
}

```

- 在 catch 语句中通过代码将对象状态恢复到函数调用之前
- 在函数进行操作之前先进行防御性复制，对复制的副本对象进行相关操作，如果成功则将操作结果替换为原数据，如果失败则直接丢弃

我们通常希望能够恢复出错误现场，但是有些情况下很难做到，尤其对于那些非受检异常。非受检异常一般会直接造成程序退出，通常情况下我们也没有必要去花费资源做错误现场恢复。

## 不要忽略异常

```java
// Empty catch block ignores exception - Highly suspect!
try {
	...
} catch (SomeException e) {
}

```

如上代码，完全忽略异常是不可取的。抛出异常说明程序运行过程中检测到了不正常状态，应该及时处理，将损失降到最低。至少，需要在 catch 中添加一条日志输出利于将来的错误排插。