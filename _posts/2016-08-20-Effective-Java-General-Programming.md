---
title: Effective Java - 通用程序设计
category: java
---

优秀的代码也总是遵循一些通用的规则，比如使局部变量的作用域尽可能小，优先使用 for-each 循环，如果精度要求较高，避免使用 float，double 等，本文就编程过程中需要一些需要注意的通用问题就行总结说明。
<!--more-->

- [使局部变量的作用域尽可能小](#使局部变量的作用域尽可能小)
- [优先使用 for-each 循环](#优先使用-for-each-循环)
- [尽可能了解并使用依赖库](#尽可能了解并使用依赖库)
- [如果精度要求较高，避免使用 float，double](#如果精度要求较高，避免使用-float，double)
- [优先使用原始类型而不是装箱后的类型](#优先使用原始类型而不是装箱后的类型)
- [尽量使用其他类型来代替字符串](#尽量使用其他类型来代替字符串)
- [当心字符串拼接的性能](#当心字符串拼接的性能)
- [通过接口引用对象](#通过接口引用对象)
- [使用接口优先于反射机制](#使用接口优先于反射机制)
- [慎重使用 native 方法](#慎重使用-native-方法)
- [慎重的进行调优](#慎重的进行调优)
- [遵循普遍的命名规范](#遵循普遍的命名规范)

## 使局部变量的作用域尽可能小

使局部变量的作用域尽最小是通常的编程常识，这里不过多介绍，主要说一点 for 循环优于 while 循环，如

```java
Iterator<Element> i = c.iterator();
while (i.hasNext()) {
	doSomething(i.next());
}
...
Iterator<Element> i2 = c2.iterator();
while (i.hasNext()) { // BUG!
	doSomethingElse(i2.next());
}

for (Iterator<Element> i = c.iterator(); i.hasNext(); ) {
	doSomething(i.next());
}
```

## 优先使用 for-each 循环

for-each 循环能够通用的对数组或集合进行遍历而且隐藏了很多内部细节，使程序更加简洁。同时 for-each 循环在编译器内部做了优化使它能够获得更好的性能。在能够使用 for-each 循环的情况尽可能使用它。

## 尽可能了解并使用依赖库

比如要产生某个值域内随机的正整数。你可能会写：

```java
private static final Random rnd = new Random();

// Common but deeply flawed!
static int random(int n) {
	return Math.abs(rnd.nextInt()) % n;
}
```

虽然产生的随机数大小符合值域要求，但是如果统计这些随机数值的分布状况可能并不是平均的，这里设计到很多数学知识，不做详细介绍。幸运的是 jdk 中提供了函数 Random.nextInt(int), 来产生需要的随机数而隐藏了内部实现的细节。

其次使用已有的库函数节省了你编写重复功能代码的时间，而且性能可能比你编写的代码更好。

## 如果精度要求较高，避免使用 float，double

float，double 都是用二进制模拟科学计算的，但二进制是阶跃的，不能标识出每一分数的值，比如 0.1 就不能用任何二进制精确标识。

为了提高精度请使用 BigDecimal，int，或 long，尽管会使程序复杂度，运行时间增加

```java
// Avoid float and double if exact answers are required!!

import java.math.BigDecimal;

public class Arithmetic {
	public static void main(String[] args) {
		System.out.println(1.03 - .42);
		System.out.println();

		System.out.println(1.00 - 9 * .10);
		System.out.println();

		howManyCandies1();
		System.out.println();

		howManyCandies2();
		System.out.println();

		howManyCandies3();
	}

	// Broken - uses floating point for monetary calculation!
	public static void howManyCandies1() {
		double funds = 1.00;
		int itemsBought = 0;
		for (double price = .10; funds >= price; price += .10) {
			funds -= price;
			itemsBought++;
		}
		System.out.println(itemsBought + " items bought.");
		System.out.println("Change: $" + funds);
	}

	public static void howManyCandies2() {
		final BigDecimal TEN_CENTS = new BigDecimal(".10");

		int itemsBought = 0;
		BigDecimal funds = new BigDecimal("1.00");
		for (BigDecimal price = TEN_CENTS; funds.compareTo(price) >= 0; price = price
				.add(TEN_CENTS)) {
			itemsBought++;
			funds = funds.subtract(price);
		}
		System.out.println(itemsBought + " items bought.");
		System.out.println("Money left over: $" + funds);
	}

	public static void howManyCandies3() {
		int itemsBought = 0;
		int funds = 100;
		for (int price = 10; funds >= price; price += 10) {
			itemsBought++;
			funds -= price;
		}
		System.out.println(itemsBought + " items bought.");
		System.out.println("Money left over: " + funds + " cents");
	}
}
```

## 优先使用原始类型而不是装箱后的类型

相比于装箱后的类型，原始类型只有值而且是固定的，这在时间与空间上都具有优势。装箱后的类型不仅继承了 Ojbect 的方法，它还有可能取 null 值，增加了程序复杂度。

考虑下面一个 Comparator：

```java
// Broken comparator - can you spot the flaw?
Comparator<Integer> naturalOrder = new Comparator<Integer>() {
	public int compare(Integer first, Integer second) {
		return first < second ? -1 : (first == second ? 0 : 1);
	}
};
```

当执行 natural- Order.compare(new Integer(42), new Integer(42)) 是的返回值是 1。因为首先进行 first<second 时会对 new Integer(42) 都拆箱为 int 类型，然后 比较结果进入 first==second 阶段，显然这里两个 new Integer(42) 不是引用一个对象，那么 = 测试无法通过返回结果为 1。

**所有对装箱型对象的 == 测试几乎都会引发错误**

上述程序应该修正为：

```java
Comparator<Integer> naturalOrder = new Comparator<Integer>() {
	public int compare(Integer first, Integer second) {
		int f = first;   // Auto-unboxing
		int s = second;  // Auto-unboxing
		return f < s ? -1 : (f == s ? 0 : 1); // No unboxing
	}
};
```

在考虑装箱类型与原生类型进行 == 测试时：

```java
public class Unbelievable {
	static Integer i;
	public static void main(String[] args) {
		if (i == 42)
			System.out.println("Unbelievable");
	}
}
```

对于上面一段程序直接运行会抛出 NullPointerException 异常。因为**所有装箱类型与原始类型需要同事远算时，装箱类型会自动拆箱**。上面程序中对于 i 如果为 null，那么 == 测试便会引发 NullPointerException。只需要将 i 定义为 long 或 int 原始类型就行。

```java
// Hideously slow program! Can you spot the object creation?
public static void main(String[] args) {
	Long sum = 0L;
	for (long i = 0; i < Integer.MAX_VALUE; i++) {
		sum += i;
	}
	System.out.println(sum);
}
```

另外频繁的装箱与拆箱操作会拖慢程序的性能，如上面一段代码运行起来就会很慢。

那么在什么时候应该使用装箱类型呢？在集合中需要，在集合中不允许存在原始类型，其余的任何能够使用原始类型的地方都要使用原始类型来提高性能与安全性，其次在不可避免使用装箱类型的时候要尽量减少自动装箱，拆箱操作，同时要时刻警惕装箱类型与原始类型同时运算时的安全性问题。

## 尽量使用其他类型来代替字符串

字符串变量的使用非常灵活，但是也伴随着很多问题，大多数情况下我们可能并不需要使用字符串，使用其它的如枚举，整型等或许是更好的选择。

由于字符串不受编译检查，所以它能应用的非常灵活，但同时由于不受编译检查很多的类型错误，拼写错误可能都不容易被发现。同时字符串的比较查询等算法性能都不是很好也是不要使用字符串类型的重要原因。

## 当心字符串拼接的性能

使用 + 拼接两个字符串是非常方便的，但是如果循环的进行拼接操作可能会引发性能问题，因为 String 是不可变类，它的值的改变伴随着新对象的创建，具体参看：[使用不可变元素](http://timqi.com/2016/08/16/effective-java-classes-interfaces/#使用不可变元素)

## 通过接口引用对象

[谨慎的设计方法签名](http://timqi.com/2016/08/19/Effective-Java-Method/#谨慎的设计方法签名) 中有提到使用接口而不是类作为方法的参数类型。同样的我们使用接口来引用对象保留了将来重构对象的内部实现而尽可能少改变其余代码的可能。

但是有些情况下需要使用类来引用对象：

- 对象是一个值的类，比如 String 等
- 没有合适的接口能够引用该类，比如 [java.util.TimerTask](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/util/TimerTask.java#L36)
- 接口没有提供实现类所实现的方法，如 [java.util.LinkedHashMap](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/util/LinkedHashMap.java#L147)

## 使用接口优先于反射机制

[java.lang.reflect](https://github.com/openjdk-mirror/jdk7u-jdk/tree/master/src/share/classes/java/lang/reflect) 提供了 Java 语言反射机制的功能。能够让你使用程序动态的获取已经加载的类的信息获得一个 Class 对象，你便可以拿到 [java.lang.reflect.Constructor](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/lang/reflect/Constructor.java)，[java.lang.reflect.Method](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/lang/reflect/Method.java)，[java.lang.reflect.Field](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/lang/reflect/Field.java)，等对象分别代表了改已经加载类的构造函数，方法和属性等。你可以通过这些对象来构建已经加载的类，调用它的方法，修改它的属性等，同时也意味着你可以去调用一个在编译时还不存在的类的某些方法，但是这种便捷是有代价的：

- 失去了所有编译时的类型检查
- 有关反射的代码晦涩难读
- 性能受到严重影响

鉴于反射的诸多缺点，在面对需要调用不存在类的功能这种需求时可以使用定义接口或者父类的方法来解决而不是反射。

## 慎重使用 native 方法

使用 jni 能够让 Java 与 C/C++ 代码进行交互，同常的使用 jni 的场景有：

- 需要编写一些涉及到平台相关的代码，如相关寄存器，文件锁的操作
- 需要重用历史遗留的一些库
- 对性能比较敏感，使用 C、C++ 获得更好的性能

随着 java 的发展，很多平台相关的代码可以用 java 来实现，比如 [java.util.prefs](https://github.com/openjdk-mirror/jdk7u-jdk/tree/master/src/share/classes/java/util/prefs) 能够操作一些平台寄存器，[java.awt.SystemTray](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/awt/SystemTray.java) 提供了对桌面的系统栏访问的代码，所以因为平台特性原因使用 native 的代码将要来越少。

同时，由于 Java 虚拟机性能的改进也不建议使用 native 代码来提高性能。比如 [java.math](https://github.com/openjdk-mirror/jdk7u-jdk/tree/master/src/share/classes/java/math) 的引入使得 Java 的运算速度基本与 C 语言类似。

另外使用 native 代码是不安全的，native 的运行环境与内存不受 jvm 管理。如果紧紧在 native 中进行简单的动作，那么由于载入 native 库带来的开销将会降低程序性能。

## 慎重的进行调优

以下摘选三条有关调优的著名格言：

> More computing sins are committed in the name of efficiency (without necessarily achieving it) than for any other single reason—including blind stupidity.
> —William A. Wulf [Wulf72]
>
> We should forget about small efficiencies, say about 97% of the time: premature optimization is the root of all evil.
> —Donald E. Knuth [Knuth74]
>
> We follow two rules in the matter of optimization:
> Rule 1. Don’t do it.
> Rule 2 (for experts only). Don’t do it yet—that is, not until you have a perfectly clear and unoptimized solution.
> —M. A. Jackson [Jackson75]

这几条都在说不要基于进行 Java 语言的调优，过早的进行调优可能会造成性能既没有提高原来的逻辑也不正确而且不好被修复的结果。

**争取写入更好的程序而不是更快的程序**

然而我们需要在程序架构设计阶段多花精力。一个好的架构能够让我们快速定位是哪里出了问题并能够轻松的重构这个模块来实现性能改进。而且程序的架构一旦确定是很难在今后的优化中有所改变的，所以要设计好程序的框架结构。力求避免设计决策中性能限制。在 API 的设计阶段就完全考虑好性能问题，比如一个公有的可变类可能会造成很多不必要的防御性拷贝开销，那么就要避免这样的设计，寻求其他的解决方案。

但是为了程序性能在 API 在做妥协是非常不划算的，因为一旦 API 确定后很难再改变，但是程序的性能可以在后期版本的重构优化中有所改善。另外 M. A. Jackson [Jackson75] 所说的是指我们在进行性能调优前要评估有多少改进。很多调优在进行前都没有准确的评估性能改进，事实上，我们很难发现性能瓶颈在哪，盲目的做调优是很不明智的。

所以我们要重点放在写出优秀的代码上，而不是更快的代码。当系统完成时如果没有性能问题那么就不需要改变什么，如果存在性能问题需要根据之前不熟的性能工具找出瓶颈在哪从而针对性的做出有效的优化。

## 遵循普遍的命名规范

命名规范是一个很大的话题，而且没有强制要求，但是遵循优秀的命名规范会大大提高 API 的可用性，这里推荐一个 Google 的命名规范：[Google Java Style Guide](https://google.github.io/styleguide/javaguide.html)
