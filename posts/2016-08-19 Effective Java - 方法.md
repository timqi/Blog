- tags: [java](/tags.md#java)
- date: 2016-08-19

# Effective Java - 方法

在设计 API 方法的时候也有很多需要注意的地方，比如在必要的地方检查方法参数的合法性；进行防御性拷贝以保证类内部数据的不可变性；谨慎的设计方法签名；小心使用重载和可变参数；返回空集合而不是Null；为方法编写文档等。

- [检查参数合法性](#%E6%A3%80%E6%9F%A5%E5%8F%82%E6%95%B0%E5%90%88%E6%B3%95%E6%80%A7)
- [当需要的时候要进行防御性复制](#%E5%BD%93%E9%9C%80%E8%A6%81%E7%9A%84%E6%97%B6%E5%80%99%E8%A6%81%E8%BF%9B%E8%A1%8C%E9%98%B2%E5%BE%A1%E6%80%A7%E5%A4%8D%E5%88%B6)
- [谨慎的设计方法签名](#%E8%B0%A8%E6%85%8E%E7%9A%84%E8%AE%BE%E8%AE%A1%E6%96%B9%E6%B3%95%E7%AD%BE%E5%90%8D)
- [小心使用方法重载](#%E5%B0%8F%E5%BF%83%E4%BD%BF%E7%94%A8%E6%96%B9%E6%B3%95%E9%87%8D%E8%BD%BD)
- [小心的使用可变参数](#%E5%B0%8F%E5%BF%83%E7%9A%84%E4%BD%BF%E7%94%A8%E5%8F%AF%E5%8F%98%E5%8F%82%E6%95%B0)
- [返回空数组或集合而不是 null](#%E8%BF%94%E5%9B%9E%E7%A9%BA%E6%95%B0%E7%BB%84%E6%88%96%E9%9B%86%E5%90%88%E8%80%8C%E4%B8%8D%E6%98%AF-null)
- [为暴露的 API 元素编写文档](#%E4%B8%BA%E6%9A%B4%E9%9C%B2%E7%9A%84-API-%E5%85%83%E7%B4%A0%E7%BC%96%E5%86%99%E6%96%87%E6%A1%A3)

## 检查参数合法性

很多情况下对于某个方法的参数取值是有一定要求的，否则会引发方法异常。通常的，对于公有方法，需要在 javadoc 文档中用 @throws 指明该方法什么情况下会抛出什么异常，如 IllegalArgumentException，IndexOutOfBoundsException，NullPointerException

```java
/**
 * Returns a BigInteger whose value is (this mod m). This method
 * differs from the remainder method in that it always returns a * non-negative BigInteger.
 *
 * @param m the modulus, which must be positive
 * @return this mod m
 * @throws ArithmeticException if m is less than or equal to 0 */
public BigInteger mod(BigInteger m) { if (m.signum() <= 0)
	throw new ArithmeticException("Modulus <= 0: " + m);
	... // Do the computation
}

```

对于内部方法，活着包内的方法，不会暴露出的内部函数，我们可以使用断言来做合法性检查，这些检查只有在编译时加入 `-ea (or -enableassertions)` 标识会触发，否则不影响程序性能：

```java
// Private helper function for a recursive sort
private static void sort(long a[], int offset, int length) {
	assert a != null;
	assert offset >= 0 && offset <= a.length;
	assert length >= 0 && length <= a.length - offset; 		... // Do the computation
}

```

当 assert 条件不满足时，会抛出 AssertionError。

## 当需要的时候要进行防御性复制

Java 语言相对与传统的 C，C++ 一个很大的优势在于它的安全性，不像 C，C++ 中一样可以随意获取指针并改变内存中的数据，但是虽然 Java 语言层面对这样的操作有一定保护，它仍然不能保证绝对的安全性，如下假如你要实现一个不可变类：

```java
// Broken "immutable" time period class

import java.util.Date;

public final class Period {
	private final Date start;
	private final Date end;

	/**
	 * @param start
	 *            the beginning of the period
	 * @param end
	 *            the end of the period; must not precede start
	 * @throws IllegalArgumentException
	 *             if start is after end
	 * @throws NullPointerException
	 *             if start or end is null
	 */
	public Period(Date start, Date end) {
		if (start.compareTo(end) > 0)
			throw new IllegalArgumentException(start + " after " + end);
		this.start = start;
		this.end = end;
	}

	public Date start() {
		return start;
	}

	public Date end() {
		return end;
	}

	public String toString() {
		return start + " - " + end;
	}

	// Remainder omitted
}

```

乍一看这个不可变类貌似没什么问题，但是仔细分析以下虽然 start，end 是 final 声明的，但是 Date 本身是个可变类，下面一段代码便可改变 Date 的数据：

```java
// Attack the internals of a Period instance
Date start = new Date();
Date end = new Date();
Period p = new Period(start, end); end.setYear(78); // Modifies internals of p!

```

因此在类的构建函数中需要做防御性复制，

```java
// Repaired constructor - makes defensive copies of parameters
public Period(Date start, Date end) {
	this.start = new Date(start.getTime());
	this.end   = new Date(end.getTime());

	if (this.start.compareTo(this.end) > 0)
		throw new IllegalArgumentException(start +" after "+ end);
}

```

这里注意，要对拷贝后的数据进行合法性校验来避免线程攻击。考虑如果程序在另外一个线程中改变了 Date 的数据而此时已经通过的参数校验，那么便会产生一个错误的 Period 对象。

此外下面的代码也能够改变 Date 的数据：

```java
// Second attack on the internals of a Period instance
Date start = new Date();
Date end = new Date();
Period p = new Period(start, end); p.end().setYear(78); // Modifies internals of p!

```

为了保证类的不可变性需要将 get 函数修改为：

```java
// Repaired accessors - make defensive copies of internal fields
public Date start() {
	return new Date(start.getTime());
}
public Date end() {
	return new Date(end.getTime());
}

```

任何时候考虑到你不希望你的客户程序改变类中的数据时都要做防御性拷贝。

## 谨慎的设计方法签名

设计好每个方法接口是一套优雅 API 的基础，在设计方法时首先要注意方法的命名，要尽可能的表达出方法的含义；不要为了提供方便而设计非常极端的方法；不要设计有很长参数列表的方法，尤其是那些参数列表很长而且类型也一样的方法；尽量使用接口作为参数类型而不是类，这样为重构留下了足够的空间；尽量使用两个值的枚举型而不是布尔变量作为参数；

## 小心使用方法重载

重载能够在很多方面为程序提供便捷，但有时也会产生很多迷惑，尤其是函数名相同，参数类型存在继承关系，函数行为不一致的情景

```java
// Broken! - What does this program print?

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class CollectionClassifier {
	public static String classify(Set<?> s) {
		return "Set";
	}

	public static String classify(List<?> lst) {
		return "List";
	}

	public static String classify(Collection<?> c) {
		return "Unknown Collection";
	}

	public static void main(String[] args) {
		Collection<?>[] collections = { new HashSet<String>(),
				new ArrayList<BigInteger>(),
				new HashMap<String, String>().values() };

		for (Collection<?> c : collections)
			System.out.println(classify(c));
	}
}

```

上面的程序会三次输出 `Unknown Collection` 而不是 `Set List Unknown Collection`。因为此时对重载函数的选择实在编译时完成的，对于构建的三个测试集合都满足 Collection 类，所以函数调用都讲指向 public static String classify(Collection<?> c) 。

但是对于重写函数的选择实在编译时进行的：

```java
// Overriding demonstration - Page 192
package org.effectivejava.examples.chapter07.item41;

class Wine {
	String name() {
		return "wine";
	}
}

class SparklingWine extends Wine {
	@Override
	String name() {
		return "sparkling wine";
	}
}

class Champagne extends SparklingWine {
	@Override
	String name() {
		return "champagne";
	}
}

public class Overriding {
	public static void main(String[] args) {
		Wine[] wines = { new Wine(), new SparklingWine(), new Champagne() };
		for (Wine wine : wines)
			System.out.println(wine.name());
	}
}

```

上述程序的输出为

```
wine
sparkling wine
champagne

```

为了 CollectionClassifier 达到既定目的，我们应该这样修改：

```java
public static String classify(Collection<?> c) {
	return c instanceof Set  ? "Set" :
		c instanceof List ? "List" : "Unknown Collection";
}

```

一个保守的避免上面这种错误的方法是不要设计两个参数个数一样的函数。

考虑下面一段代码的输出

```java
public class SetList {
	public static void main(String[] args) {
		Set<Integer> set = new TreeSet<Integer>();
		List<Integer> list = new ArrayList<Integer>();

		for (int i = -3; i < 3; i++) {
			set.add(i);
			list.add(i);
		}

		for (int i = 0; i < 3; i++) {
			set.remove(i);
			list.remove(i);
		}

		System.out.println(set + " " + list);
	}
}

```

上面代码的输出为 [-3, -2, -1] [-2, 0, 2] 而不是 [-3, -2, -1] [-3, -2, -1] 因为 List 重载了 remove 方法：

```java
remove(E e)
remove(int i)

```

这样便引起来客户端程序的疑惑，如果将循环移除的代码改为就会得到相同的结果：

```java
for (int i = 0; i < 3; i++) {
	set.remove(i);
	list.remove((Integer) i); // or remove(Integer.valueOf(i)) }
}

```

在 jdk 中也存在这样的误解，比如 [java.lang.String](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/lang/String.java#L2901) 中的 valueOf(char[]) 和 valueOf(Object)

## 小心的使用可变参数

```java
int sum(int... args) {
	int sum = 0;
	for (int arg : args)
	sum += arg;
	return sum;
}

```

如上所示为可变参数的使用方法，实际上 Java 语言内部会将可变参数包装成一个数组传入程序内部。对于那些对参数个数有要求的方法，我们可以将可变参数分开传递：

```java
// The right way to use varargs to pass one or more arguments
static int min(int firstArg, int... remainingArgs) {
	int min = firstArg;
	for (int arg : remainingArgs)
		if (arg < min)
			min = arg;
	return min;
}

```

可变参数让一些集合的构建变得非常简单，

```java
List<String> homophones = Arrays.asList("to", "too", "two");

public static <T> List<T> gather(T... args) {
	return Arrays.asList(args);
}

```

对于 Java 自动将可变参数包装为数组的方法还是会存在一定性能损耗的，为了优化性能我们可以在判断少量参数个数为多数使用场景的情况下优化为：

```java
public void foo() { }
public void foo(int a1) { }
public void foo(int a1, int a2) { }
public void foo(int a1, int a2, int a3) { }
public void foo(int a1, int a2, int a3, int... rest) { }

```

## 返回空数组或集合而不是 null

返回 null 会在客户端造成很大困扰，增加非 null 判断成本，为此我们最好返回一个空数组或集合，同时为了提高程序性能我们可以直接返回 jdk 中提供的空集合如 Collections.emptySet, emptyList, and emptyMap

## 为暴露的 API 元素编写文档

编写 javadoc 能够帮助客户端程序更好的理解你的代码，增强代码的可维护性，有关如何编写 javadoc 参看： [Sun’s How to Write Doc Comments Web page](http://www.oracle.com/technetwork/articles/java/index-137868.html)

实际上 javadoc 会被编译为 html，我们要尽可能保证 html 与代码注释的可读性，如果不能同时保证两者那么优先考虑 html 的可读性。由于 javadoc 终将会被编译未 html，所以在代码注释中使用 html 标签也是非常方便的，如 p, i 。同事一些 html 中的元素也将被转意，比如大于号，小于号

为了不转意这些符号可以使用 {@literal } 比如

```
{@literal |x + y| < |x| + |y|}

// |x + y| < |x| + |y|

```

同时为了在 javadoc 中插入代码，可以使用 {@code}:

```
{@code index < 0 || index >= this.size()}

// 多行代码
<pre>{@code and follow it with the characters }</pre>

```