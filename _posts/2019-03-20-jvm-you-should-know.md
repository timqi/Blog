---
title: 类的编译与加载及JVM内存划分
category: java
---

JVM（Java Virtual Machine）优化的已经很完善以至于大家都感觉不到他的存在。面对复杂并发业务通常架构上扩容加机器能够得到解决，但是到了一定阶段扩容仍然效果不佳的时候从jvm入手降低服务器内存、CPU使用是非常靠谱的选择。同时了解jvm有助于理解java应用的生命周期与运行环境，编写性能更好的代码与排查故障。
<!--more-->

java代码经过编译生成符合规范的class字节码，字节码约定了jvm上程序执行的规范。安装java运行环境JRE(Java Runtime Environment)中即包含了jvm虚拟机，jvm有自己的内存结构、字节码执行引擎，因此字节码可以在jvm上执行。于此同时，jvm通常由C/C++编写，但是有多种实现比如IBM、Oracle、Android平台的jvm各不相同。只有符合规范的class字节码即可在jvm上自行，开发语言不一定是java，比如Scala、Kotlin、Groovy等都可以编程成符合jvm规范的class字节码。

## java程序是怎样执行的

那么对于Java程序来讲它是编译执行还是解释执行的？首先说java程序是编译执行还是解释执行都是不完整的。

众所周知我们把java语言的执行分为编译器和执行期，中间的过度产物是class字节码，而不是机器码。通过java字节码和jvm的抽象屏蔽了操作系统的内部细节即是“一次编写、到处执行”的基础。运行时通过jvm内嵌的解释器将字节码转换成机器码执行，这一过程显然是**解释执行**的。但是大多数jvm的具体实现比如Oracle的Hotspot JVM都有JIT（Just In Time）编译器，就是在运行过程中将部分热点代码编译成机器码直接执行，而这一部分就是**编译执行**了。

启动java程序的时候指定`-Xmixed`,`-Xint`,`-Xcomp`参数表示要求jvm虚拟机使用热点混合解释与编译，只使用解释，只使用编译。当然这里`-Xcomp`完全编译执行并不一定是性能最优选择，比如完全编译会增加应用启动时间，而且无法准确预估一些分支逻辑等。

初次之外，还有一种新的编译模式AOT（Ahead-of-Time Compilation），即直接将字节码编译成机器码，省去了JIT预热过程的开销。Oracle JDK 9就引入了AOT工具`jaotc`。

```java
jaotc --output libHelloWorld.so HelloWorld.class
jaotc --output libjava.base.so --module java.base
java -XX:AOTLibrary=./libHelloWorld.so,./libjava.base.so HelloWorld
```
分层编译与AOT也不是互斥的，他们可以同时协作使用。

## 类的加载、双亲委派

类加载是JDK1.0中就引入的概念，目的是为了从不同的来源加载class代码，比如支持浏览器端Java Applet。类的加载通过类加载器（Class-Loader）实现。 加载器读取字节码，创建对用的`java.lang.Class`实例代表对应的类，而加载器通常都是`java.lang.ClassLoader`类的实例。ClassLoader中类加载的相关方法：

|方法|作用|
|-----------|---------------------|
|getParent()|返回该类加载器的父类加载器|
|loadClass(String name)|加载名称为name的类，返回的结果是java.lang.Class类的实例|
|findClass(String name)|查找名称为name的类，返回的结果是java.lang.Class类的实例|
|findLoadedClass(String name)|查找名称为name的已经被加载过的类，返回的结果是java.lang.Class类的实例|
|defineClass(String name, byte[] b, int off, int len)|把字节数组b中的内容转换成 Java 类，返回的结果是 java.lang.Class类的实例。这个方法被声明为 final的|
|resolveClass(Class<?> c)|链接指定的 Java 类|

其中name参数为类名，需要注意内部类的表示$表示方法如`com.example.Sample$1`,`com.example.Sample$Inner`。

### 类加载器的树状组织

除了引导类加载器外所有类都有一个父加载器，他们的树形关系如下图所示：

![Java类加载器](/i/2019-03-20-1.png)

```java
public class Main {
    public static void main(String[] args) {
        ClassLoader classLoader = Main.class.getClassLoader();
        while (classLoader!=null) {
            System.out.println(classLoader.toString());
            classLoader = classLoader.getParent();
        }
    }
}
// jdk.internal.loader.ClassLoaders$AppClassLoader@3d4eac69
// jdk.internal.loader.ClassLoaders$PlatformClassLoader@38af3868
```

上面代码AppClassLoader就是应用类加载器，PlatformClassLoader就是扩展类加载器，对于父类是引导类加载器情况getParent()即返回null。对于加载器需要特别指出的是，java中**不同加载器加载相同类名存在于不同命名空间，相互强制类型转换会引发ClassCastException，也就是说加载器实例+类名才唯一确定了这个类**。

类加载器加载某个类的时候会先委派他的父加载器，依次递归，如果父加载器能能够加载该类的话则直接返回成功，只有父加载器无法成功加载该类的时候才会有自己加载，这种模式称为**双亲委派**。

### 加载过程

class的加载分为`加载`,`链接`,`初始化`三个阶段，[jvm规范,类加载](https://docs.oracle.com/javase/specs/jvms/se8/html/jvms-5.html)中有明确说明。链接阶段又分为验证、准备、和解析。

![Java类生命周期](/i/2019-03-20-2.png)

加载就是上面所说的将class从不同的源如jar、class文件、网络读取载入虚拟机。验证是jvm的安全保障如校验文件格式、元数据、符号引用等，否则会报VerifyError。准备阶段创建类或接口的静态变量设为默认值，后续初始化阶段中才真正赋值，如`public static int value=123;`准备阶段值为0，初始化时才为123。解析会将一些符号引用替换为直接引用（指向目标的指针、偏移量等，与jvm内存布局直接相关）插入到字节码中。

初始化阶段会**收集类中的所有变量的赋值动作和静态语句块(static{}块)中的语句并执行**。 什么时候进行类的初始化在jvm规范中并没有具体说明，但通常jvm实现时通常遵循：

1. 创建类的实例时
2. 访问类的静态变量（出final表记的外）和静态方法时
3. 启动虚拟机时main函数所在的类需要初始化
4. 子类调用父类的静态变量，父类会被初始化而子类不会

```java
public class ClassLoadProcess {
    public static ClassLoadProcess singleTon = new ClassLoadProcess();
    public static int var1;
    public static int var2 = 0;
    public int var3 = 5;

    public ClassLoadProcess() {
        var1++;
        var2++;
        var3++;
    }

    public static ClassLoadProcess newInstance() {
        return singleTon;
    }

    public static void main(String[] args) {
        ClassLoadProcess instance = ClassLoadProcess.newInstance();
        System.out.println("var1: " + instance.var1);
        System.out.println("var2: " + instance.var2);
        System.out.println("var3: " + instance.var3);
    }
}
// var1: 1
// var2: 0
// var3: 6
```

另外AOT这种技术可以将java直接编译成机器码，这个情况可以使用AppCDS（Application Class-Data Sharing）在Bootstap Class Loader中通过内存映射直接加载，跳过上述步骤。

## JVM内存划分

jvm的内存实现会根据厂商的不同而有所不同，此处给出[jvm内存区域划分规范](https://docs.oracle.com/javase/specs/jvms/se9/html/jvms-2.html#jvms-2.5)。

**程序计数器（PC Program Counter Register）**。每个线程都有唯一的PC，指向当前执行jvm指令的地址。

**JVM栈（Java Virtual Machine Stack）**。每个线程都有一个栈结构，里面存储多个栈帧（Stack Frame），没一个对应了一次函数调用，当前执行函数对应的帧为活动帧，jvm对栈的操作只有压栈和出栈。栈中存储着局部变量表、操作数、动态链接、方法正常或异常退出。

**堆（Heap）**。堆内存被进程中的各个线程共享，堆也是java内存管理的核心区域，用来放置各种java对象实例，平时使用的`Xmx`类似的参数指定的就是这块内存的大小。java各种gc也是工作在此区域内，因此又被不同的垃圾收集器分为不同区域。

**方法区（Method Area）**。所有线程共享，存储程序Meta信息如类结构、常量池、字段、方法等。早期HotspotJVM中实现称为永久区（Permanent Generation），后来Oracle JDK 8将此移除，增加了元数据去（Metaspace）。

**运行常量池（Run-Time Constant Pool）**。存放各种常量信息，不管是编译时生成的字面量还是运行时决定的符号引用，比一般语言的符号表意义更广。

**本地方法栈（Native Method Area）**。与jvm栈很相似，没个线程都有，通常与jvm栈在同一个区域，取决于具体实现，规范中并未要求。本地方法栈运行了jvm虚拟机本身的一些功能如JIT Compiler，GC等。

![jvm内存划分](/i/2019-03-20-3.png)

上图是jvm大致的内存划分，还有一个直接内存区用于一些通信、缓存等，一个Code区用于存放JIT生成的代码信息等。OutOfMemoryError产生时表示已经没有空闲内存并且GC无法回收更多内存。那么，上述区域除了PC域外其他区域都有可能发生OOM，比如

**OutOfMemoryError**，堆内存不足。原因有很多，很可能是程序存在内存泄露，或者启动时指定的堆内存过小。

**StackOverFlowError**，发生这种错误表示jvm栈或本地栈内存不足，可能是方法存在递归调用而没有正确的终止