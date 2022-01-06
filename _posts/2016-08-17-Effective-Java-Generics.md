---
title: Effective Java - 泛型
category: java
---

Java 1.5 引入了泛型的概念，随后 jdk 中多数工具了类都支持了泛型，泛型让一些算法能够在类型安全的情况下被复用，大大提高了程序稳定性。文本就使用泛型的过程中需要注意哪些问题展开讨论，比如不要在代码中使用原生类型，消除不受检查的警告，list 优于 array，考虑使用泛型类，考虑使用泛型方法，使用通配符来提高 API 的灵活性，考虑使用类型安全的异构容器等
<!--more-->

- [不要在代码中使用原生类型](#不要在代码中使用原生类型)
- [消除不受检查的警告](#消除不受检查的警告)
- [list 优于 array](#list-优于-array)
- [考虑使用泛型类](#考虑使用泛型类)
- [考虑使用泛型方法](#考虑使用泛型方法)
- [使用通配符来提高 API 的灵活性](#使用通配符来提高-API-的灵活性)
- [考虑使用类型安全的异构容器](#考虑使用类型安全的异构容器)

## 不要在代码中使用原生类型

Java 1.5 引入泛型之前，代码中类型的一致性是要考程序员在程序编写的过程中保证的

```java
// Now a raw collection type - don't do this!
   /**
    * My stamp collection. Contains only Stamp instances.
    */
private final Collection stamps = ... ;

// Erroneous insertion of coin into stamp collection
stamps.add(new Coin( ... ));

// Now a raw iterator type - don't do this!
for (Iterator i = stamps.iterator(); i.hasNext(); ) {
	Stamp s = (Stamp) i.next(); // Throws ClassCastException
	... // Do something with the stamp
}
```

但是引入泛型之后，集合中的元素类型检查前置到了编译阶段，如果存在类型错误，编译时便会及时发现

```java
// Parameterized collection type - typesafe
private final Collection<Stamp> stamps = ... ;

//Test.java:9: add(Stamp) in Collection<Stamp> cannot be applied
//   to (Coin)
//       stamps.add(new Coin());

// for-each loop over a parameterized collection - typesafe
for (Stamp s : stamps) { // No cast
	... // Do something with the stamp
}

// for loop with parameterized iterator declaration - typesafe
for (Iterator<Stamp> i = stamps.iterator(); i.hasNext(); ) {
Stamp s = i.next(); // No cast necessary
	... // Do something with the stamp
}
```

为了保证程序的类型安全，不要在泛型代码中使用原始类型，如果不清楚集合中元素的类型则要用 ？的形式来表示，

```java
static int rawNumElementsInCommon(Set s1, Set s2) {
	int result = 0;
	for (Object o1 : s1)
		if (s2.contains(o1))
			result++;
	return result;
}

// Unbounded wildcard type - typesafe and flexible
static int numElementsInCommon(Set<?> s1, Set<?> s2) {
	int result = 0;
	for (Object o1 : s1)
		if (s2.contains(o1))
			result++;
	return result;
}

// Legitimate use of raw type - instanceof operator
if (o instanceof Set) { // Raw type
	Set<?> m = (Set<?>) o; // Wildcard type
	...
}
```

使用 <?> 的形式开启了编译时运行检查，能够保证集合中所有元素类型的统一。另外，在运行时是不存在泛型的概念的，我们在使用诸如 instanceof 操作符的时候还是要使用原始类型，也就是说 List.class, String[].class 是合法的，而 List<String>.class, List<?>.class 是不合法的。

有关几个泛型中类型的概念：

![有关泛型的几个概念](/i/2016-08-17-1.png)

## 消除不受检查的警告

Java 编译器中包含很多有关类型检查，泛型的警告

- unchecked cast warnings
- unchecked method invocation warnings
- unchecked generic array creation warnings
- unchecked conversion warnings
- ...

在程序编写过程中要尽可能通过改善代码来消除这些警告，如果实在无法消除，在保证程序绝对正确的情况下对相关的声明语句加上 @SuppressWarnings("unchecked") 注解。添加注解时也要遵循让被注释区域代码尽可能少的原则。

## list 优于 array

使用 list 相比与 array 虽然有很一点点性能损失，但是在 list 中存在很多缺点，首先 array 的类型检查是很弱的，类型问题会被后移到运行时才被发现：

```java
// Fails at runtime!
Object[] objectArray = new Long[1];
objectArray[0] = "I don't fit in"; // Throws ArrayStoreException

// Won't compile!
List<Object> ol = new ArrayList<Long>(); // Incompatible types
ol.add("I don't fit in");
```

另外，array 只有在运行时才知道存储元素的类型是什么，如果出现类型错误将会抛出异常，所以创建一个泛型的数组是不合法的，因为这个数组中存储的泛型的类型可能不一样，从而削弱了类型检查的优势

```java
// Why generic array creation is illegal - won't compile!
List<String>[] stringLists = new List<String>[1];
List<Integer> intList = Arrays.asList(42);
Object[] objects = stringLists;
objects[0] = intList;
String s = stringLists[0].get(0);
```

上述代码中最后一行代码中取出的数据应该是 Integer 类型，但是根据泛型的规则被自动转化为 String 类型，会抛出 ClassCastException 异常。因此创建泛型数组是不合法的。

不过对于性能非常敏感的场景，选择 list 来存储数据可以获得更好的性能。

## 考虑使用泛型类

在 API 类中优先声明泛型类型而不是在客户端程序中到处做强制类型转换显然更容易让人接受。有关泛型类的例子很多，jdk 中一般容器类都已支持泛型，可以参看这里不做赘述

[package java.util](https://github.com/openjdk-mirror/jdk7u-jdk/tree/master/src/share/classes/java/util)

## 考虑使用泛型方法

在使用泛型方法的过程中还是有很多套路的，这里举几个常见的例子：

```java
// Generic method
public static <E> Set<E> union(Set<E> s1, Set<E> s2) {
	Set<E> result = new HashSet<E>(s1);
	result.addAll(s2);
	return result;
}

// Generic static factory method
public static <K,V> HashMap<K,V> newHashMap() {
	return new HashMap<K,V>();
}

// Parameterized type instance creation with static factory
Map<String, List<String>> anagrams = newHashMap();
```

另外一个常见情况，假设你有一个泛型接口

```java
public interface UnaryFunction<T> {
	T apply(T arg);
}
```

我们可以通过泛型方法让这个接口更加通用：

```java
// Generic singleton factory method

public class GenericSingletonFactory {
	// Generic singleton factory pattern
	private static UnaryFunction<Object> IDENTITY_FUNCTION = new UnaryFunction<Object>() {
		public Object apply(Object arg) {
			return arg;
		}
	};

	// IDENTITY_FUNCTION is stateless and its type parameter is
	// unbounded so it's safe to share one instance across all types.
	@SuppressWarnings("unchecked")
	public static <T> UnaryFunction<T> identityFunction() {
		return (UnaryFunction<T>) IDENTITY_FUNCTION;
	}

	// Sample program to exercise generic singleton
	public static void main(String[] args) {
		String[] strings = { "jute", "hemp", "nylon" };
		UnaryFunction<String> sameString = identityFunction();
		for (String s : strings)
			System.out.println(sameString.apply(s));

		Number[] numbers = { 1, 2.0, 3L };
		UnaryFunction<Number> sameNumber = identityFunction();
		for (Number n : numbers)
			System.out.println(sameNumber.apply(n));
	}
}
```

另外给泛型方法加上一些修饰限制可以让它变得更通用

```java
// Returns the maximum value in a list - uses recursive type bound
public static <T extends Comparable<T>> T max(List<T> list) {
	Iterator<T> i = list.iterator();
	T result = i.next();
	while (i.hasNext()) {
		T t = i.next();
		if (t.compareTo(result) > 0)
		result = t;
	}
	return result;
}
```

## 使用通配符来提高 API 的灵活性

我们知道 List<Object>, List<String> 不存在继承关系，因此前者只能存储 Object 的对象，后者只能存储 String 的对象，对于下面一段代码

```java
// pushAll method without wildcard type - deficient!
public void pushAll(Iterable<E> src) {
	for (E e : src)
		push(e);
}

Stack<Number> numberStack = new Stack<Number>();
Iterable<Integer> integers = ... ;
numberStack.pushAll(integers);
```

将会报错：

```
StackTest.java:7: pushAll(Iterable<Number>) in Stack<Number>
   cannot be applied to (Iterable<Integer>)
           numberStack.pushAll(integers);
                      ^
```

Integer 是 Number 的子类，上述代码逻辑上是可行的，这显然不是我们想要的结果，然而 Java 语言为我们提供了一个通配符解决这个问题：

```java
// Wildcard type for parameter that serves as an E producer
public void pushAll(Iterable<? extends E> src) {
	for (E e : src)
		push(e);
}
```

同时，通配符还有以下一种形式

```java
// Wildcard type for parameter that serves as an E consumer
public void popAll(Collection<? super E> dst) {
	while (!isEmpty())
		dst.add(pop());
}
```

对于栈的 pop 方法应该使用 super 关键字。至于什么时候使用 extends，什么时候使用 super 可以看类中是生产了元素还是消费了元素，比如 push 中是生产了那么就应该使用 extends，而 pop 中是消费了元素，那么就应该使用 super。

## 考虑使用类型安全的异构容器

通常在容器中元素的类型是一定的，比如 List，Map，一但确定后有的存入元素需要符合这个类型约定。

但是 Java 1.5 后引入了 Class 类，对某个对象的类取值不再是 Class，而是 Class<T>,  比如：

```
String.class => Class<String>
Integer.class => Class<Integer>
```

这样，我们可以借助类型检查来返回我们需要类型对象，比如

```java
// Typesafe heterogeneous container

import java.util.HashMap;
import java.util.Map;

public class Favorites {
	// Typesafe heterogeneous container pattern - implementation
	private Map<Class<?>, Object> favorites = new HashMap<Class<?>, Object>();

	public <T> void putFavorite(Class<T> type, T instance) {
		if (type == null)
			throw new NullPointerException("Type is null");
		favorites.put(type, instance);
	}

	public <T> T getFavorite(Class<T> type) {
		return type.cast(favorites.get(type));
	}

	// Typesafe heterogeneous container pattern - client
	public static void main(String[] args) {
		Favorites f = new Favorites();
		f.putFavorite(String.class, "Java");
		f.putFavorite(Integer.class, 0xcafebabe);
		f.putFavorite(Class.class, Favorites.class);

		String favoriteString = f.getFavorite(String.class);
		int favoriteInteger = f.getFavorite(Integer.class);
		Class<?> favoriteClass = f.getFavorite(Class.class);
		System.out.printf("%s %x %s%n", favoriteString, favoriteInteger,
				favoriteClass.getName());
	}
}
```

Favorite 类中保证了在类型安全的情况下存储不同类型的对象。

当然这个 Favorite 对象仍然存在一些缺陷，比如如果用户恶意传入 Class 类型的对象作为 Key，而且诸如 List<String> 的泛型不能作为 key，因为 List<String>.class 是不合法的。而且为了保证运行时的类型安全，需要在 put 操作中对 instance 做类型转换。
