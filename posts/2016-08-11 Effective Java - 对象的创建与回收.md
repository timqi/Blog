- tags: [java](/tags.md#java)
- date: 2016-08-11

# Effective Java - 对象的创建与回收

Java 是一门面向对象的编程语言，使用 Java 的过程中免不了处理各种对象的创建与销毁过程。为了写出具备良好可读性，扩展性与性能的程序我们需要注意对象的创建与回收过程中的一些技巧，比如使用静态工厂方法，当构造参数较多时考虑使用建造者模式，设置单例的对象为 enum 或构造函数为 private，将不需要实例化类的构造函数设为 private，避免一些不必要对象的创建，及时清除过时的引用，避免使用 finalizer。

- [使用静态工厂方法](#%E4%BD%BF%E7%94%A8%E9%9D%99%E6%80%81%E5%B7%A5%E5%8E%82%E6%96%B9%E6%B3%95)
- [当构造参数较多时考虑使用建造者模式](#%E5%BD%93%E6%9E%84%E9%80%A0%E5%8F%82%E6%95%B0%E8%BE%83%E5%A4%9A%E6%97%B6%E8%80%83%E8%99%91%E4%BD%BF%E7%94%A8%E5%BB%BA%E9%80%A0%E8%80%85%E6%A8%A1%E5%BC%8F)
- [设置单例的对象为 enum 或构造函数为 private](#%E8%AE%BE%E7%BD%AE%E5%8D%95%E4%BE%8B%E7%9A%84%E5%AF%B9%E8%B1%A1%E4%B8%BA-enum-%E6%88%96%E6%9E%84%E9%80%A0%E5%87%BD%E6%95%B0%E4%B8%BA-private)
- [将不需要实例化类的构造函数设为 private](#%E5%B0%86%E4%B8%8D%E9%9C%80%E8%A6%81%E5%AE%9E%E4%BE%8B%E5%8C%96%E7%B1%BB%E7%9A%84%E6%9E%84%E9%80%A0%E5%87%BD%E6%95%B0%E8%AE%BE%E4%B8%BA-private)
- [避免一些不必要对象的创建](#%E9%81%BF%E5%85%8D%E4%B8%80%E4%BA%9B%E4%B8%8D%E5%BF%85%E8%A6%81%E5%AF%B9%E8%B1%A1%E7%9A%84%E5%88%9B%E5%BB%BA)
- [及时清除过时的引用](#%E5%8F%8A%E6%97%B6%E6%B8%85%E9%99%A4%E8%BF%87%E6%97%B6%E7%9A%84%E5%BC%95%E7%94%A8)
- [避免使用 finalizer](#%E9%81%BF%E5%85%8D%E4%BD%BF%E7%94%A8-finalizer)

## 使用静态工厂方法

优点：

- 拥有自己的名字，便于理解使用，比如 Bitmap.createBitmap, Bitmap.decodeFrom
- 通过方法内部处理，减少对象的创建，比如 Boolean.valueOf
- 能够返回其它类的 Object，比如该类的子类，通过多态根据不同场景对内部细节做优化
- 能够返回目前仍为实现的类对象，一帮这种情况用于实现服务，比如连接数据库的 JDBC，使用静态工厂能够很好的把接口和实现解耦

缺点：

- 只提供静态工厂方法而构造函数为 private 的类不能够被继承
- 不像构造函数一样有清晰的创建对象的模式，静态工厂方法往往和普通静态方法差不多，辨识度不高，在怎样创建对象上还需要借助 javadoc

常见的静态工厂方法命名：

- valueOf，获得参数的值，常用的类型转换
- of，valueOf 的更加简洁版
- getInstance，获取一个由参数指定类的对象，这个对象可能是同一个也可能不是
- newInstance，和 getInstance 类似，但是 newInstance 保证每次创建的都是新对象
- getType，像 getInstance 一样获取一个实例，通常用在统一工厂方法且有多态的场景中，Type 一般为子类类型
- newType，含义与 getType 类似，但是 newType 保证每次返回的都是新对象

**使用静态工厂方法在很多情况下能够让对象的创建过程更加的可预测，符合预期**

- [Demo android.graphics.Bitmap](https://github.com/android/platform_frameworks_base/blob/master/graphics/java/android/graphics/Bitmap.java#L632)
- [Demo android.graphics.BitmapFactory](https://github.com/android/platform_frameworks_base/blob/master/graphics/java/android/graphics/BitmapFactory.java#L386)

## 当构造参数较多时考虑使用建造者模式

当构建一个对象的参数非常多的时候我们通常想到使用望远镜模式直接将多个参数直接列在构造参数种构建，比如我们要建立一个类来描述某种食物的营养情况，一般会有脂肪，糖，卡里路等二十几个参数，如果使用望远镜模：

```java
// Telescoping constructor pattern - does not scale well!
public class NutritionFacts {
  private final int servingSize; // (mL) required
  private final int servings; // (per container) required
  private final int calories; // optional
  private final int fat; // (g) optional
  private final int sodium; // (mg) optional
  private final int carbohydrate; // (g) optional

  public NutritionFacts(int servingSize, int servings) {
    this(servingSize, servings, 0);
  }

  public NutritionFacts(int servingSize, int servings, int calories) {
    this(servingSize, servings, calories, 0);
  }

  public NutritionFacts(int servingSize, int servings, int calories, int fat) {
    this(servingSize, servings, calories, fat, 0);
  }

  public NutritionFacts(int servingSize, int servings, int calories, int fat,
      int sodium) {
    this(servingSize, servings, calories, fat, sodium, 0);
  }

  public NutritionFacts(int servingSize, int servings, int calories, int fat,
      int sodium, int carbohydrate) {
    this.servingSize = servingSize;
    this.servings = servings;
    this.calories = calories;
    this.fat = fat;
    this.sodium = sodium;
    this.carbohydrate = carbohydrate;
  }

  public static void main(String[] args) {
    NutritionFacts cocaCola = new NutritionFacts(240, 8, 100, 0, 35, 27);
  }
}

```

虽然望远镜模式能够正常工作，但是这样的 API 使用起来有很多缺点：

- 代码不容易读
- 开发者会很担心这些参数到底是什么意思，会不会传错
- 多个连续的同型参数如果位置写错那么编译时发现不了但是运行时不会正常运行

在这个基础上改进下我们发现可以使用 JavaBean 的模式来解决这个问题

```java
// JavaBeans Pattern - allows inconsistency, mandates mutability

public class NutritionFacts {
  // Parameters initialized to default values (if any)
  private int servingSize = -1; // Required; no default value
  private int servings = -1; // "     " "      "
  private int calories = 0;
  private int fat = 0;
  private int sodium = 0;
  private int carbohydrate = 0;

  public NutritionFacts() {
  }

  // Setters
  public void setServingSize(int val) {
    servingSize = val;
  }

  public void setServings(int val) {
    servings = val;
  }

  public void setCalories(int val) {
    calories = val;
  }

  public void setFat(int val) {
    fat = val;
  }

  public void setSodium(int val) {
    sodium = val;
  }

  public void setCarbohydrate(int val) {
    carbohydrate = val;
  }

  public static void main(String[] args) {
    NutritionFacts cocaCola = new NutritionFacts();
    cocaCola.setServingSize(240);
    cocaCola.setServings(8);
    cocaCola.setCalories(100);
    cocaCola.setSodium(35);
    cocaCola.setCarbohydrate(27);
  }
}

```

为每个参数设置 setter 方法解决了多参数问题，但是这种模式是先创建对象，然后为对象的每个参数赋值，这样在多线程环境中是非常不安全的，而且这种模式提供了 setter 方法也就意味着对象的参数可以随意改变不可能具有 immutable 属性

而建造者模式：

```java
// Builder Pattern

public class NutritionFacts {
  private final int servingSize;
  private final int servings;
  private final int calories;
  private final int fat;
  private final int sodium;
  private final int carbohydrate;

  public static class Builder {
    // Required parameters
    private final int servingSize;
    private final int servings;

    // Optional parameters - initialized to default values
    private int calories = 0;
    private int fat = 0;
    private int carbohydrate = 0;
    private int sodium = 0;

    public Builder(int servingSize, int servings) {
      this.servingSize = servingSize;
      this.servings = servings;
    }

    public Builder calories(int val) {
      calories = val;
      return this;
    }

    public Builder fat(int val) {
      fat = val;
      return this;
    }

    public Builder carbohydrate(int val) {
      carbohydrate = val;
      return this;
    }

    public Builder sodium(int val) {
      sodium = val;
      return this;
    }

    public NutritionFacts build() {
      return new NutritionFacts(this);
    }
  }

  private NutritionFacts(Builder builder) {
    servingSize = builder.servingSize;
    servings = builder.servings;
    calories = builder.calories;
    fat = builder.fat;
    sodium = builder.sodium;
    carbohydrate = builder.carbohydrate;
  }

  public static void main(String[] args) {
    NutritionFacts cocaCola = new NutritionFacts.Builder(240, 8)
        .calories(100).sodium(35).carbohydrate(27).build();
  }
}

```

建造者模式提供的 API 就很好的解决了上面两种模式的弊端，同时在 Builder 加入参数合法性检查更加提高了程序健壮性。但是在一些高频的 API 中，Builder 对象的创建开销仍然是不可忽略的，在一些高频库的内部完全可以直接使用构造函数的方法来提高性能。

[Demo android.app.AlertDialog.Builder](https://github.com/android/platform_frameworks_base/blob/master/core/java/android/app/AlertDialog.java#L438)

## 设置单例的对象为 enum 或构造函数为 private

为实现单例，我们在程序上一方面要避免创建新对象，一方面要避免对单例对象的非法修改：

```java
// Singleton with static factory

public class Elvis {
  private static final Elvis INSTANCE = new Elvis();

  private Elvis() {
  }

  public static Elvis getInstance() {
    return INSTANCE;
  }

  public void leaveTheBuilding() {
    System.out.println("Whoa baby, I'm outta here!");
  }

  private Object readResolve() {
    // Return the one true Elvis and let the garbage collector
    // take care of the Elvis impersonator.
    return INSTANCE;
  }

  // This code would normally appear outside the class!
  public static void main(String[] args) {
    Elvis elvis = Elvis.getInstance();
    elvis.leaveTheBuilding();
  }
}

```

这里就需要注意**反射**,**序列化**的方法实际上是有可能新建对象的，我们可以采取在私有构造函数中做合法性检验和重写 readResolve 函数的方法来避免。同时，我们可以使用只含有一个元素的枚举型来解决这个问题，使用枚举型也是单例实现模式的优先选择：

```java
// Enum singleton - the preferred approach

public enum Elvis {
  INSTANCE;

  public void leaveTheBuilding() {
    System.out.println("Whoa baby, I'm outta here!");
  }

  // This code would normally appear outside the class!
  public static void main(String[] args) {
    Elvis elvis = Elvis.INSTANCE;
    elvis.leaveTheBuilding();
  }
}

```

## 将不需要实例化类的构造函数设为 private

有些类中只提供 public static 的方法，比如一些工具类 [java.util.Collections](https://github.com/openjdk-mirror/jdk7u-jdk/blob/master/src/share/classes/java/util/Collections.java#L73) 提供有关集合操作的一些工具。为避免用户在使用这些 API 时意外新建对象可以将构造函数设为私有，同时也避免了子类的继承。

## 避免一些不必要对象的创建

```java
String s = new String("stringette"); // DON'T DO THIS!
String s = "stringette";

```

如上第一行代码如果放在循环中带来的多余开销将是非常大的

又比如我们创建一个 Person 对象，提供一个方法来计算他是不是在婴儿潮期间（1946 年到 1964 年之间）出生的方法 isBabyBoomer，我们可以这样写：

```java
// Creates lots of unnecessary duplicate objects

import java.util.Calendar;
import java.util.Date;
import java.util.TimeZone;

public class Person {
  private final Date birthDate;

  public Person(Date birthDate) {
    // Defensive copy - see Item 39
    this.birthDate = new Date(birthDate.getTime());
  }

  // Other fields, methods omitted

  // DON'T DO THIS!
  public boolean isBabyBoomer() {
    // Unnecessary allocation of expensive object
    Calendar gmtCal = Calendar.getInstance(TimeZone.getTimeZone("GMT"));
    gmtCal.set(1946, Calendar.JANUARY, 1, 0, 0, 0);
    Date boomStart = gmtCal.getTime();
    gmtCal.set(1965, Calendar.JANUARY, 1, 0, 0, 0);
    Date boomEnd = gmtCal.getTime();
    return birthDate.compareTo(boomStart) >= 0
        && birthDate.compareTo(boomEnd) < 0;
  }
}

```

但是每次调用 isBabyBoomer 的时候都会重复创建 Calendar 对象，这个是不必要的，我们可以改进为：

```java
class Person {
  private final Date birthDate;

  public Person(Date birthDate) {
    // Defensive copy - see Item 39
    this.birthDate = new Date(birthDate.getTime());
  }

  // Other fields, methods

  /**
   * The starting and ending dates of the baby boom.
   */
  private static final Date BOOM_START;
  private static final Date BOOM_END;

  static {
    Calendar gmtCal = Calendar.getInstance(TimeZone.getTimeZone("GMT"));
    gmtCal.set(1946, Calendar.JANUARY, 1, 0, 0, 0);
    BOOM_START = gmtCal.getTime();
    gmtCal.set(1965, Calendar.JANUARY, 1, 0, 0, 0);
    BOOM_END = gmtCal.getTime();
  }

  public boolean isBabyBoomer() {
    return birthDate.compareTo(BOOM_START) >= 0
        && birthDate.compareTo(BOOM_END) < 0;
  }
}

```

改进版只创建一次 Calendar，TimeZone，Date 对象，降低了系统开销。但是如果 isBabyBoomer 调用频率较低，那么 BOOM_START，BOOM_END 的创建就显得有些多余。虽然我们可以通过懒加载的办法在第一次调用 isBabyBoomer 时创建他们，但是一般不建议这样做。

还有一个创建不必要对象的常见场景是 Java 语言提供的自动装箱，int 到 Integer，long 到 Long 的转换：

```java
// Hideously slow program! Can you spot the object creation?
Long sum = 0L;
for (long i = 0; i < Integer.MAX_VALUE; i++) {
  sum += i;
}

```

这是一个非常慢的程序，sum 声明为 Long 却每次与 long 原始类型的数值相加 i 与 Integer.MAX_VALUE 的比较中也有多次类型转换中对象创建的开销。

我们要尽量使用原始类型而不是自动装箱后的封装对象，要时刻对隐藏的装箱操作留意

## 及时清除过时的引用

虽然 Java 语言中带有 GC，但是我们仍然要注意及时释放对象指针，不然很容易形成内存泄露从而影响程序性能，甚至 OOM 错误

```java
import java.util.Arrays;

public class Stack {
  private Object[] elements;
  private int size = 0;
  private static final int DEFAULT_INITIAL_CAPACITY = 16;

  public Stack() {
    elements = new Object[DEFAULT_INITIAL_CAPACITY];
  }

  public void push(Object e) {
    ensureCapacity();
    elements[size++] = e;
  }

  public Object pop() {
    if (size == 0)
      throw new EmptyStackException();
    return elements[--size];
  }

  /**
   * Ensure space for at least one more element, roughly doubling the capacity
   * each time the array needs to grow.
   */
  private void ensureCapacity() {
    if (elements.length == size)
      elements = Arrays.copyOf(elements, 2 * size + 1);
  }
}

```

如上的 Stack 代码，如果在栈特别大，然后多次调用 pop 后实际上引用的相关对象并没有释放掉，从而引起内存泄露。要解决这个问题我们要及时释放掉相关引用：

```java
public Object pop() {
  if (size == 0)
    throw new EmptyStackException();
  Object result = elements[--size];
  elements[size] = null; // Eliminate obsolete reference
  return result;
}

```

一旦程序员遇到过类似的问题，很有可能就会比较敏感进而在很多情况下将变量置空，程序变得非常啰嗦，然而这是没有必要的，我们要做的是尽可能的让变量的作用域更小，和一些手动管理内存的类（如上面的 Stack）中多加注意内存释放问题。

另外一个容易引起内存泄露的场景是内存缓存和各种 listeners 回调对象，我们将一些对象缓存在内存中，一段时间过期后仍没有释放将引起内存泄露，类似的问题可以使用弱引用的方法来及时释放相关对象。

## 避免使用 finalizer

finalizer 指的是 Java 对象的 finalize 方法，通常它看起来像是 C++ 中的析构函数，然后他们并不相同，实际上存在很大的区别。

finalizer 什么时候执行没有明确的规定，在语言级别都没有保障，Java 语言种甚至不能保证 finalizer 最终会执行。而且 finalizer 的线程优先级较低，如果大量对象累积在 finalizer 中销毁，而 finalizer 很长时间没有执行，那么必然会引起内存问题。

另外 finalizer 带来的开销比正常情况下销毁对象高几百倍，通常情况我们也没有必要使用 finalizer。我们可以通过在类中编写一个终止函数来释放相关资源并在相应的程序逻辑中调用这个终止函数，比如 InputStream 中数据读完后需要调用 close。

但是 finalizer 可以最终作为终止函数的保障，如果用户忘记调用终止函数，在 finalizer 中记录下警告日志并释放相关资源；或者通过 jni 释放一些资源的时候可能需要用到 finalizer。

最后，如果使用了 finalizer，为了避免在子类中忘记调用父类 finalize 方法导致父类没有执行 finalize 的问题我们可以使用 Finalizer Guardian 模式，在类中声明一个匿名类并重写 finaliz 方法，这样在对象执行 finalize 的时候比然后引发匿名类 finalize 方法的调用

```java
// Finalizer Guardian idiom
public class Foo {
  // Sole purpose of this object is to finalize outer Foo object
  private final Object finalizerGuardian = new Object() {
    @Override protected void finalize() throws Throwable {
      ... // Finalize outer Foo object
    }
  };
  ...  // Remainder omitted
}

```