---
title: Effective Java - 类与接口
category: java
---

在 Java 面向对象编程中，类与接口扮演这很重要的角色。我们设计类的好坏直接影响了程序的性能与易用性，在设计类的过程中有很多原则可以让我们尽可能规避错误，设计出更好的类图关系。比如使类与其成员的访问权限尽可能小，通过 get 方法而不是直接暴露的形式访问属性，使用不可变元素，使用组合而不是继承，可能会有继承的地方一定要有文档，优先使用接口而不是抽象类，只用接口来定义类型，使用继承而不是标签类，使用函数对象来表示策略，尽可能使用静态的嵌套类而不是非静态的。
<!--more-->

- [使类与成员访问权限最小](#使类与成员访问权限最小)
- [提供 get 方法，而不是直接暴露公有可变属性域](#提供-get-方法，而不是直接暴露公有可变属性域)
- [使用不可变元素](#使用不可变元素)
- [使用组合而不是继承](#使用组合而不是继承)
- [可能会有继承的地方一定要有文档](#可能会有继承的地方一定要有文档)
- [优先使用接口而不是抽象类](#优先使用接口而不是抽象类)
- [只用接口来定义类型](#只用接口来定义类型)
- [使用继承而不是标签类](#使用继承而不是标签类)
- [使用函数对象来表示策略](#使用函数对象来表示策略)
- [尽可能使用静态的嵌套类而不是非静态的](#尽可能使用静态的嵌套类而不是非静态的)

## 使类与成员访问权限最小

我们要是时刻对类和类成员的访问权限保持警惕，要只暴露能够提供系统功能的最小接口，隐藏内部实现，将 API 的定义与现实解耦开，这样在我们遇到性能问题时能够通过重构内部实现来提升性能，另外，一旦我们声明了某个公有 API，我们有义务在今后的版本中维护这个接口，因此随意扩大类的访问权限是非常不明智的，我们要在提供 API 功能的同时使类与成员的访问权限尽可能的小。

通常访问权限有 private，package-private(friendly，默认权限)，protected，public。这里对这几种权限不再赘述。

对于一些非 final 属性，或者 final 属性索引的可变变量不要声明为 public 权限，否则暴露出内部成员变量可能会引发很多安全漏洞。如果需要访问类的私有可变成员，我们可以将它封装为不可变的公有成员或者提供一个 get 函数返回它的副本，从而保护原属性成员

```java
private static final Thing[] PRIVATE_VALUES = { ... };
public static final List<Thing> VALUES = Collections.unmodifiableList(Arrays.asList(PRIVATE_VALUES));

private static final Thing[] PRIVATE_VALUES = { ... };
public static final Thing[] values() {
    return PRIVATE_VALUES.clone();
}
```

## 提供 get 方法，而不是直接暴露公有可变属性域

有关提供 get 方法而不是公有属性的做法有很多好处，比如我们可以重构 get 方法的实现而不是改变 API 中的变量来重构内部实现等，同时通过 set 方法能够对赋值的合法性做检查等。

这点在类的设计中是很基础的，不做过多赘述。这里据两个 jdk 中没有遵循这点的类的例子：[java.awt.Point](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/awt/Point.java#L38)  [java.awt.Dimension](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/awt/Dimension.java#L54)

## 使用不可变元素

jdk 中有很多不可变类，比如：String，装箱后的原始类型，BigInteger，BigDecimal。不可变类更易于设计，更好实现而且能够让类变的更安全，因此我们要尽量使用不可变的元素，要实现一个不可变类，有下面 5 条规则：

1. 不要提供能够改变类的状态的方法
2. 让类不可被继承
3. 将类的所有属性设为 final
4. 将类的所有属性权限设为 private
5. 不要将类中持有可变变量的属性暴露给客户

```java
// Immutable class

public final class Complex {
	private final double re;
	private final double im;

	private Complex(double re, double im) {
		this.re = re;
		this.im = im;
	}

	public static Complex valueOf(double re, double im) {
		return new Complex(re, im);
	}

	public static Complex valueOfPolar(double r, double theta) {
		return new Complex(r * Math.cos(theta), r * Math.sin(theta));
	}

	public static final Complex ZERO = new Complex(0, 0);
	public static final Complex ONE = new Complex(1, 0);
	public static final Complex I = new Complex(0, 1);

	// Accessors with no corresponding mutators
	public double realPart() {
		return re;
	}

	public double imaginaryPart() {
		return im;
	}

	public Complex add(Complex c) {
		return new Complex(re + c.re, im + c.im);
	}

	public Complex subtract(Complex c) {
		return new Complex(re - c.re, im - c.im);
	}

	public Complex multiply(Complex c) {
		return new Complex(re * c.re - im * c.im, re * c.im + im * c.re);
	}

	public Complex divide(Complex c) {
		double tmp = c.re * c.re + c.im * c.im;
		return new Complex((re * c.re + im * c.im) / tmp, (im * c.re - re
				* c.im)
				/ tmp);
	}

	@Override
	public boolean equals(Object o) {
		if (o == this)
			return true;
		if (!(o instanceof Complex))
			return false;
		Complex c = (Complex) o;

		return Double.compare(re, c.re) == 0 && Double.compare(im, c.im) == 0;
	}

	@Override
	public int hashCode() {
		int result = 17 + hashDouble(re);
		result = 31 * result + hashDouble(im);
		return result;
	}

	private int hashDouble(double val) {
		long longBits = Double.doubleToLongBits(re);
		return (int) (longBits ^ (longBits >>> 32));
	}

	@Override
	public String toString() {
		return "(" + re + " + " + im + "i)";
	}
}
```

如上的复数类，属性 re，im 都是 private final 类型的并且提供了访问方法 realPart 和 imaginaryPart。对于运算过程的结果是返回了一个新建的复数类而不是在原来的基础上修改，这种防御性的复制是很有必要的。

如果你对这种通过函数保证的不可变性不熟悉的话你可能会觉着很怪异。但是不可变对象有很多优势，比如，它只有一个状态而且就是它被创建时的状态，我们可以放心的使用不可变类作为 Map 中的 Key；不可变对象通常是线程安全的，我们不用考虑多线程请景下引发的线程安全问题；**不可变对象可以非常方便的被分享与重用**，我们可以通过提供一个静态工厂方法类将不可变对象缓存并返回，比如所有装箱原始类型对象以及 BigInteger 等都是这样优化的，这样，不可变类便不用考虑防御性的拷贝问题，也不用提供 clone 或者拷贝构建函数，因为每个对象只有一个状态，这点在早期是不太好理解的，比如 String 类就提供了 copy 的构建函数，但是它显然用处不大了。

不可变类的一点不好的地方就是，每次值的改变都会创建一个新的对象，这样对于小的改变开销还是很大的。比如可变类型的 [java.util.BitSet](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/util/BitSet.java#L63) 每次改变只是对他本身的操作，并不会创建新对象，然而 [java.math.BigInteger](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/math/BigInteger.java#L99) 即使一位的改变也会创建一个新的对象。如果你在循环中需要改变类的值，那么这个开销很有可能会被放大。

为了避免在循环中多次创建对象的开销，通常我们提供了不可变对象的可变封装，比如 [java.lang.StringBuilder](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/lang/StringBuilder.java#L72) 相比于 [java.lang.String](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/lang/String.java#L110)

为了避免其他子类的继承，我们需要为 class 添加 final 属性，或者将构建函数设为 private 同时提供静态工厂方法，这样更加利于理解和性能调优，具体可参看 [Effective Java - 对象的创建与回收](http://timqi.com/2016/08/11/effective-java-object/#使用静态工厂方法)

```java
// Immutable class with static factories instead of constructors
public class Complex {
	private final double re;
	private final double im;
	private Complex(double re, double im) {
		this.re = re;
		this.im = im;
	}

	public static Complex valueOf(double re, double im) {
		return new Complex(re, im);
	}
... // Remainder unchanged
}
```

尽可能的让类不可变是有很多优势的，但是在 jdk 中还有很多具备不可变类特点的类并不是不可变的，比如 [java.util.Date](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/util/Date.java#L129) [java.awt.Point](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/awt/Point.java#L38)。另外，对于一些可变类我们要尽可能的让他们可变的属性变少，比如 [java.util.TimerTask](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/util/TimerTask.java#L36) 虽然它是个可变类，但是实现的时候让他的状态尽可能少，你可以执行这个任务，也可以取消，但是一旦任务完成后便不能重新执行了。

## 使用组合而不是继承

继承是一个强大的工具，但是它违被了**封装**的概念，继承将一部分封装交由父类去管理，这会造成很多问题。

```java
// Broken - Inappropriate use of inheritance!

import java.util.Arrays;
import java.util.Collection;
import java.util.HashSet;

public class InstrumentedHashSet<E> extends HashSet<E> {
	// The number of attempted element insertions
	private int addCount = 0;

	public InstrumentedHashSet() {
	}

	public InstrumentedHashSet(int initCap, float loadFactor) {
		super(initCap, loadFactor);
	}

	@Override
	public boolean add(E e) {
		addCount++;
		return super.add(e);
	}

	@Override
	public boolean addAll(Collection<? extends E> c) {
		addCount += c.size();
		return super.addAll(c);
	}

	public int getAddCount() {
		return addCount;
	}

	public static void main(String[] args) {
		InstrumentedHashSet<String> s = new InstrumentedHashSet<String>();
		s.addAll(Arrays.asList("Snap", "Crackle", "Pop"));
		System.out.println(s.getAddCount());
	}
}
```

如上类中 InstrumentedHashSet 继承自 HashSet，并添加了 Set 中一共存储多少条数据的一个变量，最后的输出结果 s.getAddCount() 为 6，因为 HashSet 中的 addAll 方法调用了 add 方法。像这样父类的行为在子类中是无法控制的，如果将来父类中又新添加一个增加记录的方法那么你的类也需要改变，风险很大。因此面对这种情况我们通常使用组合关系来表示并在外面宰割 wrapper，记装饰者模式

```java
// InstrumentedSet.java
// Wrapper class - uses composition in place of inheritance

import java.util.Arrays;
import java.util.Collection;
import java.util.HashSet;
import java.util.Set;

public class InstrumentedSet<E> extends ForwardingSet<E> {
	private int addCount = 0;

	public InstrumentedSet(Set<E> s) {
		super(s);
	}

	@Override
	public boolean add(E e) {
		addCount++;
		return super.add(e);
	}

	@Override
	public boolean addAll(Collection<? extends E> c) {
		addCount += c.size();
		return super.addAll(c);
	}

	public int getAddCount() {
		return addCount;
	}

	public static void main(String[] args) {
		InstrumentedSet<String> s = new InstrumentedSet<String>(
				new HashSet<String>());
		s.addAll(Arrays.asList("Snap", "Crackle", "Pop"));
		System.out.println(s.getAddCount());
	}
}

// ForwardingSet.java
// Reusable forwarding class

import java.util.Collection;
import java.util.Iterator;
import java.util.Set;

public class ForwardingSet<E> implements Set<E> {
	private final Set<E> s;

	public ForwardingSet(Set<E> s) {
		this.s = s;
	}

	public void clear() {
		s.clear();
	}

	public boolean contains(Object o) {
		return s.contains(o);
	}

	public boolean isEmpty() {
		return s.isEmpty();
	}

	public int size() {
		return s.size();
	}

	public Iterator<E> iterator() {
		return s.iterator();
	}

	public boolean add(E e) {
		return s.add(e);
	}

	public boolean remove(Object o) {
		return s.remove(o);
	}

	public boolean containsAll(Collection<?> c) {
		return s.containsAll(c);
	}

	public boolean addAll(Collection<? extends E> c) {
		return s.addAll(c);
	}

	public boolean removeAll(Collection<?> c) {
		return s.removeAll(c);
	}

	public boolean retainAll(Collection<?> c) {
		return s.retainAll(c);
	}

	public Object[] toArray() {
		return s.toArray();
	}

	public <T> T[] toArray(T[] a) {
		return s.toArray(a);
	}

	@Override
	public boolean equals(Object o) {
		return s.equals(o);
	}

	@Override
	public int hashCode() {
		return s.hashCode();
	}

	@Override
	public String toString() {
		return s.toString();
	}
}
```

这样我们就能够轻松面对 API 的改变而不会影响到内部的业务逻辑。因此在如果不是严格满足 "is-a" 的情况下尽量使用 组合，中继加 wrappeer 的形式而不是继承

## 可能会有继承的地方一定要有文档

有可能会使用到继承的类或方法一定要清楚的在文档中注明前因后果，比如 [remove@java.util.AbstractCollection](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/util/AbstractCollection.java#L271)  [removeRange@java.util.AbstractList](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/util/AbstractList.java#L567).

## 优先使用接口而不是抽象类

接口和抽象类都为 API 定义下的多种实现提供了可能，但是由于 java 的单一继承性，在使用抽象类的过程中子类的类型与继承树就确定了，这为程序的灵活性产生很多障碍，但是现有的一个类很轻松的去实现多个接口。

但是使用抽象类很多时候可以在同层继承之间重用很多代码，比如 [java.util.AbstractList](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/util/AbstractList.java#L71)。充分发挥了接口与抽象类的优势，使用接口定义类型，抽象类来实现一个基本骨架。

## 只用接口来定义类型

接口最好只用来定义类型与方法，比如一些常量尽量不要放在接口中，比如 [java.io.ObjectStreamConstants](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/io/ObjectStreamConstants.java#L34) 就不是一个值得效仿的案例。当需要在 API 中暴露常量时通常我们会将他们放在类中而不是接口中，其次使用枚举型也是很好的选择。

## 使用继承而不是标签类

我们来看一个例子：

```java
// Tagged class - vastly inferior to a class hierarchy!

class Figure {
	enum Shape {
		RECTANGLE, CIRCLE
	};

	// Tag field - the shape of this figure
	final Shape shape;

	// These fields are used only if shape is RECTANGLE
	double length;
	double width;

	// This field is used only if shape is CIRCLE
	double radius;

	// Constructor for circle
	Figure(double radius) {
		shape = Shape.CIRCLE;
		this.radius = radius;
	}

	// Constructor for rectangle
	Figure(double length, double width) {
		shape = Shape.RECTANGLE;
		this.length = length;
		this.width = width;
	}

	double area() {
		switch (shape) {
		case RECTANGLE:
			return length * width;
		case CIRCLE:
			return Math.PI * (radius * radius);
		default:
			throw new AssertionError();
		}
	}
}
```

上面的例子中我们使用 shape 变量来标识 Figure，显然用这样的方法组织是非常杂乱而且容易出错的。

为此，我们引入抽象类和继承工具来重新组织：

```java
// Figure.java
// Class hierarchy replacement for a tagged class

abstract class Figure {
	abstract double area();
}

// Circle.java
class Circle extends Figure {
	final double radius;

	Circle(double radius) {
		this.radius = radius;
	}

	double area() {
		return Math.PI * (radius * radius);
	}
}

// Rectangle.java
class Rectangle extends Figure {
	final double length;
	final double width;

	Rectangle(double length, double width) {
		this.length = length;
		this.width = width;
	}

	double area() {
		return length * width;
	}
}
```

这样很好的避免了原来类中混乱的逻辑问题，降低了内存开销，同时也增加了程序的可扩展性，比如此时我们要新引入一个 Square 类完全可以写为：

```java
class Square extends Rectangle {
	Square(double side) {
		super(side, side);
	}
}
```

## 使用函数对象来表示策略

一般编程语言中都会提供诸如函数指针，lambda 表达式这样的语法来执行某个函数。比如 C 语言中的 qsort 中一个参数就是提供了函数指针来为排序提供策略。在 Java 语言中定义一个类，其中有个方法来提供某种策略函数就是函数对象，比如

```java
class StringLengthComparator {
	public int compare(String s1, String s2) {
		return s1.length() - s2.length();
	}
}
```

对于客户端来讲可能需要提供更多的比较策略，那么此时便需要定义一个接口来兼容这一策略：

```java
// Strategy interface
public interface Comparator<T> {
	public int compare(T t1, T t2);
}
```

然后由函数对象来实现这个策略接口

```java
class StringLengthComparator implements Comparator<String> {
	... // class body is identical to the one shown above
}
```

然而，对于函数对象，更多的我们可能会使用匿名类：

```java
Arrays.sort(stringArray, new Comparator<String>() {
	public int compare(String s1, String s2) {
		return s1.length() - s2.length();
	}
});
```

## 尽可能使用静态的嵌套类而不是非静态的

显然的，相比于静态的嵌套类，非静态的嵌套类会增加对嵌套类关联类的引用，增大内存开销。
