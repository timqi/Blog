- tags: [java](/tags.md#java)
- date: 2016-08-18

# Effective Java - 枚举型、注解

枚举型的引入大大增加了 Java 语言编译时的类型安全性，大部分的使用静态整型常量来表示不同状态的应用场景都可以用枚举型来解决，同时 EnumSet，EnumMap 的引入也大可取代传统的位域操作的实际模式，同时也保证了位运算的性能与编译时类型安全。于此同时，Java 中的枚举型不仅仅只有枚举值几个元素，它是一个完整的类，能够拥有自己的属性与方法为程序提供了更大的灵活性，但是它不能够实例化与继承。

- [使用枚举型而不是整型常量](#%E4%BD%BF%E7%94%A8%E6%9E%9A%E4%B8%BE%E5%9E%8B%E8%80%8C%E4%B8%8D%E6%98%AF%E6%95%B4%E5%9E%8B%E5%B8%B8%E9%87%8F)
- [使用值域代替序列号](#%E4%BD%BF%E7%94%A8%E5%80%BC%E5%9F%9F%E4%BB%A3%E6%9B%BF%E5%BA%8F%E5%88%97%E5%8F%B7)
- [使用 EnumSet 代替位域](#%E4%BD%BF%E7%94%A8-EnumSet-%E4%BB%A3%E6%9B%BF%E4%BD%8D%E5%9F%9F)
- [使用 EnumMap 代替序列号索引](#%E4%BD%BF%E7%94%A8-EnumMap-%E4%BB%A3%E6%9B%BF%E5%BA%8F%E5%88%97%E5%8F%B7%E7%B4%A2%E5%BC%95)
- [使用接口来扩展枚举型](#%E4%BD%BF%E7%94%A8%E6%8E%A5%E5%8F%A3%E6%9D%A5%E6%89%A9%E5%B1%95%E6%9E%9A%E4%B8%BE%E5%9E%8B)
- [使用注解而不是命名约定](#%E4%BD%BF%E7%94%A8%E6%B3%A8%E8%A7%A3%E8%80%8C%E4%B8%8D%E6%98%AF%E5%91%BD%E5%90%8D%E7%BA%A6%E5%AE%9A)
- [总是使用 @Override 注解](#%E6%80%BB%E6%98%AF%E4%BD%BF%E7%94%A8-@Override-%E6%B3%A8%E8%A7%A3)
- [用标记接口定义类型](#%E7%94%A8%E6%A0%87%E8%AE%B0%E6%8E%A5%E5%8F%A3%E5%AE%9A%E4%B9%89%E7%B1%BB%E5%9E%8B)

## 使用枚举型而不是整型常量

Java 中的枚举型看上去与 C，C++ 中的类似，但实际上 Java 中的枚举型功能更加强大，它本质上就是一个类，但是不能实例化，它是绝对单例的，它的值就是这个类的 public static final 类型的常量。为枚举类型添加方法可以是个很强大的工具，我们通常称为富枚举型。比如我们需要一个枚举型来描述太阳系中的行星：

```java
// Enum type with data and behavior

public enum Planet {
	MERCURY(3.302e+23, 2.439e6),
	VENUS(4.869e+24, 6.052e6),
	EARTH(5.975e+24, 6.378e6),
	MARS(6.419e+23, 3.393e6),
	JUPITER(1.899e+27, 7.149e7),
	SATURN(5.685e+26, 6.027e7),
	URANUS(8.683e+25, 2.556e7),
	NEPTUNE(1.024e+26, 2.477e7);

	private final double mass; // In kilograms
	private final double radius; // In meters
	private final double surfaceGravity; // In m / s^2

	// Universal gravitational constant in m^3 / kg s^2
	private static final double G = 6.67300E-11;

	// Constructor
	Planet(double mass, double radius) {
		this.mass = mass;
		this.radius = radius;
		surfaceGravity = G * mass / (radius * radius);
	}

	public double mass() {
		return mass;
	}

	public double radius() {
		return radius;
	}

	public double surfaceGravity() {
		return surfaceGravity;
	}

	public double surfaceWeight(double mass) {
		return mass * surfaceGravity; // F = ma
	}
}

```

我们可以为枚举型提供一个构造函数，然后为它指定相应的值。上例是一个典型的不可变对象。同时可以提供函数来扩展功能。根据上面的枚举类我们可以很轻松的计算各行星与地球重力的比值：

```java
public class WeightTable {
	public static void main(String[] args) {
		double earthWeight = Double.parseDouble(args[0]);
		double mass = earthWeight / Planet.EARTH.surfaceGravity();
		for (Planet p : Planet.values())
			System.out.printf("Weight on %s is %f%n", p, p.surfaceWeight(mass));
	}
}

```

输出中也很好的兼容了 toString，让日志更加易读：

```
Weight on MERCURY is 66.133672
Weight on VENUS is 158.383926
Weight on EARTH is 175.000000
Weight on MARS is 66.430699
Weight on JUPITER is 442.693902
Weight on SATURN is 186.464970
Weight on URANUS is 158.349709
Weight on NEPTUNE is 198.846116

```

其次考虑如果我们有一个枚举类来表示四则运算符，然后提供一个函数来进行该类计算，代码如下：

```java
// Enum type that switches on its own value - questionable
public enum Operation {
	PLUS, MINUS, TIMES, DIVIDE;
	// Do the arithmetic op represented by this constant
	double apply(double x, double y) {
		switch(this) {
			case PLUS:   return x + y;
			case MINUS:  return x - y;
			case TIMES:  return x * y;
			case DIVIDE: return x / y;
		}
		throw new AssertionError("Unknown op: " + this);
	}
}

```

当然上述代码是很不安全的，首先 throw 代码肯定不会被执行，但是如果不添加这一句又会产生编译时错误。如果我们想要新添加一种运算那么还要在 case 中添加一种情况，很繁琐，面对这种情况我们可以这样写：

```java
// Enum type with constant-specific class bodies and data

import java.util.HashMap;
import java.util.Map;

public enum Operation {
	PLUS("+") {
		double apply(double x, double y) {
			return x + y;
		}
	},
	MINUS("-") {
		double apply(double x, double y) {
			return x - y;
		}
	},
	TIMES("*") {
		double apply(double x, double y) {
			return x * y;
		}
	},
	DIVIDE("/") {
		double apply(double x, double y) {
			return x / y;
		}
	};
	private final String symbol;

	Operation(String symbol) {
		this.symbol = symbol;
	}

	@Override
	public String toString() {
		return symbol;
	}

	abstract double apply(double x, double y);

	// Implementing a fromString method on an enum type - Page 154
	private static final Map<String, Operation> stringToEnum = new HashMap<String, Operation>();

	static { // Initialize map from constant name to enum constant
		for (Operation op : values())
			stringToEnum.put(op.toString(), op);
	}

	// Returns Operation for string, or null if string is invalid
	public static Operation fromString(String symbol) {
		return stringToEnum.get(symbol);
	}

	// Test program to perform all operations on given operands
	public static void main(String[] args) {
		double x = Double.parseDouble(args[0]);
		double y = Double.parseDouble(args[1]);
		for (Operation op : Operation.values())
			System.out.printf("%f %s %f = %f%n", x, op, y, op.apply(x, y));
	}
}

```

在外层声明一个静态方法，然后由枚举的各个成员分别来实现。这样在新添加一种运算时便能及时处理。重写 toString 能够使程序的输出更加易读，同时我们可以通过一个 fromString 函数来获得枚举型的值，这个 fromString 相当与一个不可变类的静态工厂方法。代码中 stringToEnum 的初始化应该放在 static 代码段中，因为如果放在构建函数中会有些值还没有实例化，会引发空指针错误。同样的，在构建函数中也无法访问类的静态成员，因为它们还没有被初始化。

当要处理一个常量集合的时候枚举型是一个很好的选择。当然枚举型本质上是一个类，它的若干个枚举值这个类的不可变实例化对象。相比于使用静态整型常量的设计模式，使用枚举的性能更好，当然使用枚举的初始化开销更大。

## 使用值域代替序列号

我们知道枚举型值的定义可以根据其先后顺序对应一个整型数值。通常情况下不要依赖这个序列值

```java
// Abuse of ordinal to derive an associated value - DON'T DO THIS
public enum Ensemble {
	SOLO,   DUET,   TRIO, QUARTET, QUINTET,
	SEXTET, SEPTET, OCTET, NONET,  DECTET;

	public int numberOfMusicians() {
		return ordinal() + 1;
	}
}

```

如上 numberOfMusicians 返回的是每个乐队的音乐家的数量。而代码中通过 ordinal() 依赖枚举值定义顺序是非常不可靠的，如果新加一个类型的乐团，那么上述代码需要做出非常大的改动。为了避免这种情况，我们需用其他字段来存储这个信息：

```java
public enum Ensemble {
	SOLO(1), DUET(2), TRIO(3), QUARTET(4), QUINTET(5), SEXTET(6), SEPTET(7), OCTET(
			8), DOUBLE_QUARTET(8), NONET(9), DECTET(10), TRIPLE_QUARTET(12);

	private final int numberOfMusicians;

	Ensemble(int size) {
		this.numberOfMusicians = size;
	}

	public int numberOfMusicians() {
		return numberOfMusicians;
	}
}

```

## 使用 EnumSet 代替位域

在使用静态整型模式时候常把一位作为一个标识来描述对象的状态叫做位域，比如：

```java
 // Bit field enumeration constants - OBSOLETE!
 public class Text {
 	public static final int STYLE_BOLD          = 1 << 0;
 	public static final int STYLE_ITALIC        = 1 << 1;
 	public static final int STYLE_UNDERLINE     = 1 << 2;
 	public static final int STYLE_STRIKETHROUGH = 1 << 3;

 	// Parameter is bitwise OR of zero or more STYLE_ constants
 	public void applyStyles(int styles) { ... }
 }

text.applyStyles(STYLE_BOLD | STYLE_ITALIC);

```

这种方法具有静态整型模式的所有缺点，比如输入不易读等等。在 jdk 中提供了一个类 [java.util.EnumSet](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/util/EnumSet.java#L80)，它实现了 Set 接口，实现所有 Set 的功能以及保证了类型安全。EnumSet 内部也是一个位向量，算法都是通过位操作实现的，在性能上与位域差不多，但是使用 EnumSet 还有上面介绍 enum 提到的诸多优点。使用 EnumSet 实现上述代码如下：

```java
public class Text {
	public enum Style {
		BOLD, ITALIC, UNDERLINE, STRIKETHROUGH
	}

	// Any Set could be passed in, but EnumSet is clearly best
	public void applyStyles(Set<Style> styles) {
		// Body goes here
	}

	// Sample use
	public static void main(String[] args) {
		Text text = new Text();
		text.applyStyles(EnumSet.of(Style.BOLD, Style.ITALIC));
	}
}

```

## 使用 EnumMap 代替序列号索引

上文中提到使用枚举型的值域来替代索引序号现在考虑这样一个类，

```java
public class Herb {
	public enum Type { ANNUAL, PERENNIAL, BIENNIAL }
	private final String name;
	private final Type type;

	Herb(String name, Type type) {
		this.name = name;
		this.type = type;
	}

	@Override public String toString() {
		return name;
	}
}

```

此时需要对花园中的植物按照 Type 分类，那我们可能会用一个数据集合来处理：

```java
// Using ordinal() to index an array - DON'T DO THIS!
Herb[] garden = ... ;
Set<Herb>[] herbsByType = // Indexed by Herb.Type.ordinal() (Set<Herb>[]) new Set[Herb.Type.values().length];

for (int i = 0; i < herbsByType.length; i++)
	herbsByType[i] = new HashSet<Herb>();
for (Herb h : garden) herbsByType[h.type.ordinal()].add(h);

// Print the results
for (int i = 0; i < herbsByType.length; i++) {
	System.out.printf("%s: %s%n",
	Herb.Type.values()[i], herbsByType[i]);
}

```

上面代码中存在很多问题，比如泛型集合数组不合法，对枚举类型序列的依赖不可靠。此时，我们可以使用 EnumMap

```java
// Using an EnumMap to associate data with an enum
Map<Herb.Type, Set<Herb>> herbsByType =
	new EnumMap<Herb.Type, Set<Herb>>(Herb.Type.class);

for (Herb.Type t : Herb.Type.values())
	herbsByType.put(t, new HashSet<Herb>());
for (Herb h : garden)
	herbsByType.get(h.type).add(h);
System.out.println(herbsByType);

```

EnumMap 内部也是封装了一个数组来保证性能，同时使用 EnumMap 保留了类型安全，输出友好等优点。

如果在多维数组中描述映射关系可以使用 EnumMap 的嵌套，比如一个描述物质 固态，液态，气态 三态变化的程序：

```java
public enum Phase {
	SOLID, LIQUID, GAS;

	public enum Transition {
		MELT(SOLID, LIQUID), FREEZE(LIQUID, SOLID), BOIL(LIQUID, GAS), CONDENSE(
				GAS, LIQUID), SUBLIME(SOLID, GAS), DEPOSIT(GAS, SOLID);

		private final Phase src;
		private final Phase dst;

		Transition(Phase src, Phase dst) {
			this.src = src;
			this.dst = dst;
		}

		// Initialize the phase transition map
		private static final Map<Phase, Map<Phase, Transition>> m = new EnumMap<Phase, Map<Phase, Transition>>(
				Phase.class);
		static {
			for (Phase p : Phase.values())
				m.put(p, new EnumMap<Phase, Transition>(Phase.class));
			for (Transition trans : Transition.values())
				m.get(trans.src).put(trans.dst, trans);
		}

		public static Transition from(Phase src, Phase dst) {
			return m.get(src).get(dst);
		}
	}
}

```

## 使用接口来扩展枚举型

枚举型是无法继承的，但是可以实现某个接口。因此我们可以定义好一个接口由不同的枚举型显现来扩展枚举型变量。

```java
// Operation.java
// Emulated extensible enum using an interface
public interface Operation {
	double apply(double x, double y);
}

// BasicOperation.java
// Emulated extensible enum using an interface
public enum BasicOperation implements Operation {
	PLUS("+") {
		public double apply(double x, double y) {
			return x + y;
		}
	},
	MINUS("-") {
		public double apply(double x, double y) {
			return x - y;
		}
	},
	TIMES("*") {
		public double apply(double x, double y) {
			return x * y;
		}
	},
	DIVIDE("/") {
		public double apply(double x, double y) {
			return x / y;
		}
	};
	private final String symbol;

	BasicOperation(String symbol) {
		this.symbol = symbol;
	}

	@Override
	public String toString() {
		return symbol;
	}
}

// ExtendedOperation.java
// Emulated extension enum
public enum ExtendedOperation implements Operation {
	EXP("^") {
		public double apply(double x, double y) {
			return Math.pow(x, y);
		}
	},
	REMAINDER("%") {
		public double apply(double x, double y) {
			return x % y;
		}
	};

	private final String symbol;

	ExtendedOperation(String symbol) {
		this.symbol = symbol;
	}

	@Override
	public String toString() {
		return symbol;
	}

	// Test class to exercise all operations in "extension enum" - Page 167
	public static void main(String[] args) {
		double x = Double.parseDouble(args[0]);
		double y = Double.parseDouble(args[1]);
		test(ExtendedOperation.class, x, y);

		System.out.println(); // Print a blank line between tests
		test2(Arrays.asList(ExtendedOperation.values()), x, y);
	}

	// test parameter is a bounded type token (Item 29)
	private static <T extends Enum<T> & Operation> void test(Class<T> opSet,
			double x, double y) {
		for (Operation op : opSet.getEnumConstants())
			System.out.printf("%f %s %f = %f%n", x, op, y, op.apply(x, y));
	}

	// test parameter is a bounded wildcard type (Item 28)
	private static void test2(Collection<? extends Operation> opSet, double x,
			double y) {
		for (Operation op : opSet)
			System.out.printf("%f %s %f = %f%n", x, op, y, op.apply(x, y));
	}
}

```

这样客户端程序可以通过新建一个枚举型类并实现接口来扩展功能。

## 使用注解而不是命名约定

在 Java 1.5 之前没有注解，通常会使用特定的命名来规范某一特征，比如 JUnit 中规定类中的以 test 开头的方法为测试函数。现在这样做是不安全的，比如 tsetSafetyOverride 就不会执行测试，从而可能会引发安全漏洞。后来引入 @Test 注解

```java
/**
 * Indicates that the annotated method is a test method. Use only on
 * parameterless static methods.
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface Test {
}

// Use case of @Test
// Program containing marker annotations
public class Sample {
	@Test public static void m1() { } // Test should pass
	public static void m2() { }
	@Test public static void m3() { // Test Should fail
		throw new RuntimeException("Boom");
	}
	public static void m4() { }
	@Test public void m5() { } // INVALID USE: nonstatic method
	public static void m6() { }
	@Test public static void m7() { // Test should fail
		throw new RuntimeException("Crash");
	}
	public static void m8() { }
}

```

引入注解避免了约定错误，在编译时就能发现问题。

有关注解的知识推荐：[Java 注解 Annotation](http://a.codekk.com/detail/Android/Trinea/%E5%85%AC%E5%85%B1%E6%8A%80%E6%9C%AF%E7%82%B9%E4%B9%8B%20Java%20%E6%B3%A8%E8%A7%A3%20Annotation)

## 总是使用 @Override 注解

@Override 注解标识了被注解的方法是重写了父类的方法，编译器会检查重写的限制条件，比如方法的签名是否匹配等。这样能够避免一些非常神器的错误

```java
public class Bigram {
	private final char first;
	private final char second;

	public Bigram(char first, char second) {
		this.first = first;
		this.second = second;
	}

	public boolean equals(Bigram b) {
		return b.first == first && b.second == second;
	}

	public int hashCode() {
		return 31 * first + second;
	}

	public static void main(String[] args) {
		Set<Bigram> s = new HashSet<Bigram>();
		for (int i = 0; i < 10; i++)
			for (char ch = 'a'; ch <= 'z'; ch++)
				s.add(new Bigram(ch, ch));
		System.out.println(s.size());
	}
}

```

上述代码 s 大小为 260 而不是 26，因为 equals 方法的参数为 Object，而 Bigram 参数并没有重写父类方法，因此造成错误，而且很难发现。

## 用标记接口定义类型

有些接口中没有定义任何方法，它紧紧是为了标识对象具有某种属性。比如 Serializable 接口代表对象可以写入 ObjectOutputStream。有人认为标记注解的出现取代了标记接口，实际上这样说是不准确的，因为接口实际上定义了一种类型可以让类去实现，从而能够在编译时就发现一些异常，不用等到编译时。而且相比标记注解能够被标记在类的任何元素中，接口只能被类实现，从而增强了安全性。使用注解的优势在于能够提供更多的参数信息和对框架的统一性有所益处。

那么到底什么时候使用接口标记什么时候使用注解标记呢？首先如果你的标记需要用在非 class，interface 元素上，那么必须要使用注解，接口在这种场景下无法使用。如果你的标记是用于 class 或 interface 那么你需要考虑一下你是否需要一个方法只接受有这个标记为参数的方法，如果是那么最好优先使用标记接口，这样可以帮助你进行编译阶段的类型检查。当你想要编写一个 target 为 ElementType.TYPE 的类时，考虑一下是否可以用接口来现实更合适。