- tags: [java](/tags.md#java)
- date: 2016-08-15

# Effective Java - Objec 通用方法

java.lang.Object 是 Java 语言中所有类的基类，在这个基类中提供了很多基础的方法比如 equals, hashCode, toString 以及 Coparable 的 compareTo 等。我们在使用和重写这些方法时需要遵循一些基本事项，本文就此展开讨论。

- [重写 equals 方法时要遵循一般规律](#%E9%87%8D%E5%86%99-equals-%E6%96%B9%E6%B3%95%E6%97%B6%E8%A6%81%E9%81%B5%E5%BE%AA%E4%B8%80%E8%88%AC%E8%A7%84%E5%BE%8B)
- [当重写 equals 时一定要重写 hashCode](#%E5%BD%93%E9%87%8D%E5%86%99-equals-%E6%97%B6%E4%B8%80%E5%AE%9A%E8%A6%81%E9%87%8D%E5%86%99-hashCode)
- [总是要记得重写 toString](#%E6%80%BB%E6%98%AF%E8%A6%81%E8%AE%B0%E5%BE%97%E9%87%8D%E5%86%99-toString)
- [慎重重写 clone](#%E6%85%8E%E9%87%8D%E9%87%8D%E5%86%99-clone)
- [考虑实现 Comparable 接口](#%E8%80%83%E8%99%91%E5%AE%9E%E7%8E%B0-Comparable-%E6%8E%A5%E5%8F%A3)

## 重写 equals 方法时要遵循一般规律

有关 equals 方法的说明在 [java.lang.Object](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/lang/Object.java#L149)。

重写 equals 方法看上去很简单，但是其中有很多需要注意的地方，一不留神很可能造成非常严重的后果。一般情况下每个对象都是非常独特的，它只和它自己相等。大多数时候你不需要重写 equals 方法，比如：

- 类的每个对象内部都是特别的，比如每个线程对象内部存储了激活的任务，而不是特别的值
- 不需要提供“逻辑相等”的测试，比如 java.util.Random 类可以通过重写 equals 方法判断这个对象接下来产生的随机数序列是否一样。但是 Random 类的设计者认为用户不需要这样的功能，所以并没有重写
- 类的父类中已经实现了 equals 方法并且对子类同样适用，比如 [java.util.AbstractList](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/util/AbstractList.java#L512) 实现了 equals，在它的子类 java.util.List 便不用重写 equals
- 确定私有类中 equals 没有被调用过，为了保险起见可以加上判断：

```java
@Override public boolean equals(Object o) {
  throw new AssertionError(); // Method is never called
}

```

**通常只有在需要判断逻辑相等的情况下才需要重写 equals 方法。equals 的结果影响其它类的使用结果，比如 HashMap，HashSet**

如果要重写 equals，那么它必须要满足自反性，对称性，及物性和统一性，并且对于非空对象 x，x.equals(null) 必须返回 false

- 自反性，对于任何非空对象 x，如果 x.equals(x) 一定为 true。

如果不满足自反性，当你向一个 Collection 中添加对象时，contains 方法返回 false 会认为集合中没有你已经添加的对象

- 对称性，对于任何非空对象 x，y 如果 x.equals(y) 则必然有 y.equals(x)

```java
// Broken - violates symmetry!

public final class CaseInsensitiveString {
	private final String s;

	public CaseInsensitiveString(String s) {
		if (s == null)
			throw new NullPointerException();
		this.s = s;
	}

	// Broken - violates symmetry!
	@Override
	public boolean equals(Object o) {
		if (o instanceof CaseInsensitiveString)
			return s.equalsIgnoreCase(((CaseInsensitiveString) o).s);
		if (o instanceof String) // One-way interoperability!
			return s.equalsIgnoreCase((String) o);
		return false;
	}

	// This version is correct.
	// @Override public boolean equals(Object o) {
	// return o instanceof CaseInsensitiveString &&
	// ((CaseInsensitiveString) o).s.equalsIgnoreCase(s);
	// }

	public static void main(String[] args) {
		CaseInsensitiveString cis = new CaseInsensitiveString("Polish");
		String s = "polish";
		System.out.println(cis.equals(s) + "  " + s.equals(cis));
	}
}

```

上面的例子中就不满足对称性，比如：

```java
CaseInsensitiveString cis = new CaseInsensitiveString("Polish");
String s = "polish";

List<CaseInsensitiveString> list =
       new ArrayList<CaseInsensitiveString>();
list.add(cis);

list.contains(s) // false

```

上述代码中使用注释部分的 equals 代码是正确的

- 及物性，对于任何非空对象 x，y，z， 如果 x.equals(y) ，y.equals(z) 则必然有 x.equals(z)

假设我们有一个类来表示坐标内的一点

```java
// Simple immutable two-dimensional integer point class

public class Point {
	private final int x;
	private final int y;

	public Point(int x, int y) {
		this.x = x;
		this.y = y;
	}

	@Override
	public boolean equals(Object o) {
		if (!(o instanceof Point))
			return false;
		Point p = (Point) o;
		return p.x == x && p.y == y;
	}
}

```

现在我们希望加一个属性来表示这个点的颜色

```java
// Attempting to add a value component to Point

public class ColorPoint extends Point {
	private final Color color;

	public ColorPoint(int x, int y, Color color) {
		super(x, y);
		this.color = color;
	}

	// Broken - violates symmetry!
	@Override
	public boolean equals(Object o) {
		if (!(o instanceof ColorPoint))
			return false;
		return super.equals(o) && ((ColorPoint) o).color == color;
	}

	// Broken - violates transitivity!
	// @Override public boolean equals(Object o) {
	// if (!(o instanceof Point))
	// return false;
	//
	// // If o is a normal Point, do a color-blind comparison
	// if (!(o instanceof ColorPoint))
	// return o.equals(this);
	//
	// // o is a ColorPoint; do a full comparison
	// return super.equals(o) && ((ColorPoint)o).color == color;
	// }

	public static void main(String[] args) {
		// First equals function violates symmetry
		Point p = new Point(1, 2);
		ColorPoint cp = new ColorPoint(1, 2, Color.RED);
		System.out.println(p.equals(cp) + " " + cp.equals(p));

		// Second equals function violates transitivity
		ColorPoint p1 = new ColorPoint(1, 2, Color.RED);
		Point p2 = new Point(1, 2);
		ColorPoint p3 = new ColorPoint(1, 2, Color.BLUE);
		System.out.printf("%s %s %s%n", p1.equals(p2), p2.equals(p3),
				p1.equals(p3));
	}
}

```

我们可以看到上述代码违反了对称性原则，p.equals(cp) 返回 true，而 cp.equals(p) 返回 false。为了考虑到与父类混合比较的情况我们希望把 equals 重写为上述注释中的样子，但是我们得到 p1.equals(p2)，p2.equals(p3) 而 p1.equals(p3) 却不成立，这违反了及物性原则。

**事实上，没有办法添加属性并扩展实例化类，同时保留了 equals 的结果，除非你愿意放弃面向对象的抽象化的好处。**

通常情况下为了 equals 满足需求我们会使用组合的形势而不是继承来描述 Point 和 ColorPoint 的关系。

```java
// Adds a value component without violating the equals contract

public class ColorPoint {
	private final Point point;
	private final Color color;

	public ColorPoint(int x, int y, Color color) {
		if (color == null)
			throw new NullPointerException();
		point = new Point(x, y);
		this.color = color;
	}

	/**
	 * Returns the point-view of this color point.
	 */
	public Point asPoint() {
		return point;
	}

	@Override
	public boolean equals(Object o) {
		if (!(o instanceof ColorPoint))
			return false;
		ColorPoint cp = (ColorPoint) o;
		return cp.point.equals(point) && cp.color.equals(color);
	}

	@Override
	public int hashCode() {
		return point.hashCode() * 33 + color.hashCode();
	}
}

```

不幸的是 jdk 中也存在这样的错误，比如 [java.sql.Timestamp](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/sql/Timestamp.java#L152) 类继承自 [java.util.Date](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/util/Date.java#L129) 类并添加了 nanos 属性。这样，如果 Date 与 Timestamp 同时出现在一个 Collection 中调用 contains 方法时便有可能产生非常奇怪的错误并且很难调试。

但是如果父类是抽象类，不能实例化那么也不会产生这样的问题。

- 统一性，统一性是指对于两个对象进行 equals 测试时返回的结果要始终相同

这要求我们在重写 equals 方法时不要依赖一些不可靠的属性进行判断，如果违反了这一要求就很难满足统一性，比如 [java.net.URL](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/net/URL.java#L855) 的 equals 方法就是判断 host 对应的 IP 地址是否相等，这是不可靠的，破坏了 URL equals 的统一性。

- 无效处理，这里指当 equals 的传入参数为 null 时要始终返回 false

我们在重写 equals 时并不需要进行非空判断，因为在进行 equals 之前我们都需要做类型检查，如果传入参数为 null 时，在类型检查阶段 equals 函数便会返回 false。

综上所述，当我们重写 equals 方法时要：

1. 首先使用 == 操作符来判断两者是不是相同的引用来提高性能，如果这种场景足够多的话
2. 使用 instanceof 操作符来判断参数的类型是不是符合要求，如果不符合要求返回 false
3. 将参数强制转换为目标类型
4. 检查每一个特征字段是否是否逻辑相等，如果都相等返回 true，否则返回 false
5. 当完成 equals 方法时检查是否满足对称性，及物性，统一性，包括自反性和无效性

其中第四步检查每个特征字段逻辑相等时，如果是非 float，double 的原始类型属性可以直接 == 来判断；对于对象引用的字段，我们可以递归的调用 equals 来判断相关属性是否相等；对于 float 和 double 类型可以使用 Float.compare 和 Double.compare 来避免 Float.NaN, -0.0f 带来的错误；有些属性字段很有可能为空，我们可以这样判断：

```java
(field == null ? o.field == null : field.equals(o.field))
//slower
//(field == o.field || (field != null && field.equals(o.field)))

```

为了提高 equals 的性能，要先比较那些更可能不相等而且比较操作代价较低的属性字段。

## 当重写 equals 时一定要重写 hashCode

有关 hashCode 方法的说明在 [java.lang.Object](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/lang/Object.java#L101)

hashCode 函数也需要具备统一性原则，即当某个对象数据不变的时候其 hashCode 返回值总是相同。另外 hashCode 要满足**当 equals 测试相等的两个对象的 hashCode 值是相同的**。但是当 equals 测试不相等时并没有要求两个对象的 hashCode 值要形同。

为了保证使用哈希值的性能，通常我们要满足当 equals 测试不相等是两个对象的 hashCode 值也是不相等的，否则，哈希表就退化为了单链表。

```java
package org.effectivejava.examples.chapter03.item09;

// Shows the need for overriding hashcode when you override equals - Pages 45-46

import java.util.HashMap;
import java.util.Map;

public final class PhoneNumber {
	private final short areaCode;
	private final short prefix;
	private final short lineNumber;

	public PhoneNumber(int areaCode, int prefix, int lineNumber) {
		rangeCheck(areaCode, 999, "area code");
		rangeCheck(prefix, 999, "prefix");
		rangeCheck(lineNumber, 9999, "line number");
		this.areaCode = (short) areaCode;
		this.prefix = (short) prefix;
		this.lineNumber = (short) lineNumber;
	}

	private static void rangeCheck(int arg, int max, String name) {
		if (arg < 0 || arg > max)
			throw new IllegalArgumentException(name + ": " + arg);
	}

	@Override
	public boolean equals(Object o) {
		if (o == this)
			return true;
		if (!(o instanceof PhoneNumber))
			return false;
		PhoneNumber pn = (PhoneNumber) o;
		return pn.lineNumber == lineNumber && pn.prefix == prefix
				&& pn.areaCode == areaCode;
	}

	public static void main(String[] args) {
		Map<PhoneNumber, String> m = new HashMap<PhoneNumber, String>();
		m.put(new PhoneNumber(707, 867, 5309), "Jenny");
		System.out.println(m.get(new PhoneNumber(707, 867, 5309)));
	}
}

```

上面的 PhoneNumber 类中没有重写 hashCode 方法，当执行

```java
Map<PhoneNumber, String> m = new HashMap<PhoneNumber, String>();
m.put(new PhoneNumber(707, 867, 5309), "Jenny");
// can't get correct string in m
m.get(new PhoneNumber(707, 867, 5309))
​````

两个 new PhoneNumber(707, 867, 5309) 产生对象的 hashCode 是不相同的，因此在 HashMap，HashSet，HashTable 等结构中认为两个 PhoneNumber 是不同的，无法根据具体的 PhoneNumber 值去除 HashMap 中的 string。

为此，我们要重写 hashCode 方法来修复这个问题，一般生成 hashCode 的方法如下：

>1. Store some constant nonzero value, say, 17, in an int variable called >result.
>2. For each significant field f in your object (each field taken into account by the equals method, that is), do the following:
>  a. Compute an int hash code c for the field:
>    i. If the field is a boolean, compute (f ? 1 : 0).
>    ii. If the field is a byte, char, short, or int, compute (int) f.
>    iii. Ifthefieldisalong,compute(int)(f^(f>>>32)).
>    iv. Ifthefieldisafloat,computeFloat.floatToIntBits(f).
>    v. If the field is a double, compute Double.doubleToLongBits(f), and then hash the resulting long as in step 2.a.iii.
>    vi. If the field is an object reference and this class’s equals method compares the field by recursively invoking equals, recursively invoke hashCode on the field. If a more complex comparison is required, compute a “canonical representation” for this field and invoke hashCode on the canonical representation. If the value of the field is null, return 0 (or some other constant, but 0 is traditional).
>    vii. If the field is an array, treat it as if each element were a separate field. That is, compute a hash code for each significant element by applying these rules recursively, and combine these values per step 2.b. If every element in an array field is significant, you can use one of the Arrays.hashCode methods added in release 1.5.
>  b. Combine the hash code c computed in step 2.a into result as follows: result = 31 * result + c;
>3. Return result.
>4. When you are finished writing the hashCode method, ask yourself whether equal instances have equal hash codes. Write unit tests to verify your intuition! If equal instances have unequal hash codes, figure out
why and fix the problem.

在计算哈希值时可以忽略对象中一些无关紧要的类，至于为什么在最后的 result 要乘以 31 这个神奇的数字，是因为几乎所有的当代 java 虚拟机中都进行了 31 * i == (i << 5) - i 优化来提高性能。

那么 PhoneNumber 的 hashCode 就可以重写为：

​```java
//A decent hashCode method
@Override public int hashCode() {
	int result = 17;
	result = 31 * result + areaCode;
	result = 31 * result + prefix;
	result = 31 * result + lineNumber;
	return result;
}

```

如果 PhoneNumber 紧紧是个存储数据用的不可变对象而且 hashCode 调用的频率非常高，那么我们可以在创建对象的时候将哈希值缓存下来，或者采用在第一次调用 hashCode 的时候计算并缓存的懒加载策略来优化性能：

```java
// Lazily initialized, cached hashCode
private volatile int hashCode;

@Override public int hashCode() {
	int result = hashCode;
	if (result == 0) {
		result = 17;
		result = 31 * result + areaCode;
		result = 31 * result + prefix;
		result = 31 * result + lineNumber;
		hashCode = result;
	}
	return result;
}

```

## 总是要记得重写 toString

有 toString 方法的说明在 [java.lang.Object](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/lang/Object.java#L236)。

合理的重写 toString 方法能让你编写的类更加易用。在 println，printlf，或者调试器中，对象的 toString 函数经常被调用。

如果你不重写 toString，那么当这个对象被打印时总是输出该对象的类型名+@+该对象的哈希值的十六进制表示，比如：PhoneNumber@163b91。

toString 方法的输出中应该包含所有能够描述该对象特征的所有信息。同时，虽然 java 语言中没有明确要求 toString 的输出格式是怎样的，但是为了用户能够更好的使用我们的 api，我们至少需要在 javadoc 的明确的指明 toString 函数的输出格式，是否可信赖以及在下一个版本中是否有可能会改变等信息以供用户参考。

## 慎重重写 clone

有关 clone 方法的说明在 [java.lang.Object](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/lang/Object.java#L213)。

覆盖 clone 方法时需要重写实现 [java.lang.Cloneable](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/lang/Cloneable.java#L53) 接口。但是 Cloneable 中并没有什么方法。Cloneable 不保证任何 clone 操作能够成功实现，仅仅标识该对象的 protected 权限的 clone 方法重写为 public 权限。通常 Objec 的 clone 方法会返回该对象的逐域拷贝。调用一个没有实现 Cloneable 的对象的 clone 方法时会抛出 CloneNotSupportedException 异常。

**通常的实现接口是为了表明类的行为，但是 Cloneable 接口改变了父类 protected 方法的行为，这种非典型用法是不值得效仿的**

通常要重写 clone 方法，对于任意对象 x 我们要在不改变原对象的情况下满足：

```
x.clone() != x
x.clone().getClass() == x.getClass()
x.clone().equals(x)

```

在重写 clone 方法时我们面对的最大问题就是深拷贝和浅拷贝，一般情况下对于可变变量的浅拷贝会让新对象持有原对象的引用进而引发不必要的错误。

当类的所有属性都是不可变的时候，我们可以直接使用 super.clone 完成拷贝，比如重写 PhoneNumber 类的 clone 方法：

```java
@Override
public PhoneNumber clone() {
  try {
  	return (PhoneNumber) super.clone();
  } catch (CloneNotSupportedException e) {
  	throw new AssertionError(); // Can't happen
  }
}

```

但是对于类中含有可变属性的类就不能简单的使用 super.clone  了，比如：

```java
// A cloneable version of Stack

import java.util.Arrays;

public class Stack implements Cloneable {
	private Object[] elements;
	private int size = 0;
	private static final int DEFAULT_INITIAL_CAPACITY = 16;

	public Stack() {
		this.elements = new Object[DEFAULT_INITIAL_CAPACITY];
	}

	public void push(Object e) {
		ensureCapacity();
		elements[size++] = e;
	}

	public Object pop() {
		if (size == 0)
			throw new EmptyStackException();
		Object result = elements[--size];
		elements[size] = null; // Eliminate obsolete reference
		return result;
	}

	public boolean isEmpty() {
		return size == 0;
	}

	@Override
	public Stack clone() {
		try {
			Stack result = (Stack) super.clone();
			result.elements = elements.clone();
			return result;
		} catch (CloneNotSupportedException e) {
			throw new AssertionError();
		}
	}

	// Ensure space for at least one more element.
	private void ensureCapacity() {
		if (elements.length == size)
			elements = Arrays.copyOf(elements, 2 * size + 1);
	}

	// To see that clone works, call with several command line arguments
	public static void main(String[] args) {
		Stack stack = new Stack();
		for (String arg : args)
			stack.push(arg);
		Stack copy = stack.clone();
		while (!stack.isEmpty())
			System.out.print(stack.pop() + " ");
		System.out.println();
		while (!copy.isEmpty())
			System.out.print(copy.pop() + " ");
	}
}

```

要通过 result.elements = elements.clone(); 将 elements 属性中对原对象的引用重新 clone 为新的，这样才能**不破坏原对象的属性内容**。

事实上，我们的目的仅仅是在不破坏原来对象的基础上保留原对象的属性，要对每个属性域做深复制，当然根据需要改变那些特殊的不可变属性，比如 ID等。

**所有实现了 Cloneable 接口的需要重写 clone 方法为 public 并且返回值类型与该对象的类型相同。然后调用 super.clone 复制类中的不可变属性，然后通过深复制修复类中的可变属性，而且大多数情况可以通过循环调用 clone 方法来完成深复制。如果你的类是为了让用户继承，那么你需要实现一个 protected 权限的 clone 方法，来让子类决定是否实现 clone，如果父类没有正确实现 clone，那么子类一定不能正确的实现 clone 方法。**

通过 clone 实现对象的复制是相当繁琐的。通常情况下我们可以通过传入不同参数的构造函数或者静态工厂方法来实现对象的复制，比如：

```java
public Yum(Yum yum);
public static Yum newInstance(Yum yum);

```

## 考虑实现 Comparable 接口

有关 Comparable 接口的介绍在 [java.lang.Comparable](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/lang/Comparable.java#L137)

compareTo 方法并没有声明在 Object 中，它在 Comparable 中声明。与 equals 类似，但是 compareTo 更多的使用在比较排序的场景下，更加通用，比如实现了 Comparable 接口的类可以直接使用 Arrays.sort(a) 来完成排序。

通常在需要排序的场景上依赖关系处理是由 compareTo 决定的，比如 TreeMap，TreeSet 等（HashMap，HashSet 使用的是 equals 方法）。与 equals 相同，compareTo 也需要遵循对称性，及物性。

编写 compareTo 方法与 equals 类似，但是 compareTo 方法中不需要做类型判断，如果传入参数类型不对会直接引发编译时错误，同时，compareTo 的传入参数有可能为 null，如果传入参数为 null 时访问它的某个属性会引起 NullPointerException 错误。

compareTo 只根据返回值的正负来判断序列关系，所以它的返回值取值不必局限于 {-1，0，1}，比如 PhoneNumber 类的 compareTo 函数就可以编写为：

```java
public int compareTo(PhoneNumber pn) {
	// Compare area codes
	int areaCodeDiff = areaCode - pn.areaCode;
	if (areaCodeDiff != 0)
	return areaCodeDiff;

	// Area codes are equal, compare prefixes
	int prefixDiff = prefix - pn.prefix;
	if (prefixDiff != 0)
	return prefixDiff;

	// Area codes and prefixes are equal, compare line numbers
	return lineNumber - pn.lineNumber;
}

```

但是这这中间会有个问题就是 areaCodeDiff，或 prefixDiff 的值有溢出的可能，比如 areaCode 为最大正整数，pn.areaCode 为最小负整数，那么 areaCodeDiff 的值将会溢出整型变量的取值范围表现为一个负数，进而影响比较的结果，这样的错误是很难发现调试的。