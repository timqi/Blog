---
title: 理解并实现IoC与AOP
category: java
---

IoC(Inversion of Control)与AOP(Aspect Oriented Programming)是java web编程领域领的重要概念。java作为面向对象的强类型静态语言在编程时存在很多局限性，比如对象之间的复杂依赖关系处理，比如运行时获取修改代码meta信息等。本文就聊聊IoC与AOP是什么以及怎样实现。
<!--more-->

## IoC

IoC的核心思想在于**资源不由使用的双方管理，而是由第三方（容器）管理**。这样做有很多好处，首先资源实现了统一管理和配置，其次大大降低了资源双方的依赖程度，也就是我们通常所说的解耦，也就是其中一方有变化需求时不需要全局修改各种代码，只要在变化的地方少量修改即可。

资源由第三方管理容器是什么意思呢？这个第三方就像是一个超市，比如你想要一个牙刷，告诉超市你要一个牙刷就好了，你不需要关心牙刷是怎样制造生产出来的。牙刷本身在定义好自己的属性、使用方法后也不用关心每个人具体怎样使用。这个容器就是资源创建与消费的一个代理商，中介。另外比如我们使用支付宝付款我们直接与支付宝对接就可以了而不用了解具体商户的银行信息。

以上是IoC解决的问题，在这个问题上引申出了依赖注入（DI）与IoC（控制反转）这些概念。我们通过一个简单的IoC实现来看看这些概念是什么意思。

### IoC的简单实现

我们使用`BeanFactory`管理容器中的对象，它应该至少包含两个方法，一个是获取bean，一个是注册bean。`BeanDefinition`定义一个被管理的资源，他通常持有资源的实例，资源的`class`对象以获取资源的meta信息可以通过反射操作资源。

```java
public abstract class BeanFactory {

  private HashMap<String, BeanDefinition> map = new HashMap<>();

  public Object getBean(String name) throws Exception {
    BeanDefinition beandefinition = map.get(name);
    if (beandefinition == null) {
      throw new IllegalArgumentException("No bean named " + name + " is defined");
    }
    Object bean = beandefinition.getBean();
    if (bean == null) {
      bean = doCreate(beandefinition);
    }
    return bean;
  }

  public void registerBeanDefinition(String name, BeanDefinition beandefinition) throws Exception {
    Object bean = doCreate(beandefinition);
    beandefinition.setBean(bean);
    map.put(name, beandefinition);
  }

  abstract Object doCreate(BeanDefinition beandefinition) throws Exception;
}


public class BeanDefinition {

  private Object bean;

  private Class beanClass;

  private String ClassName;

  private PropertyValues propertyValues = new PropertyValues();

  public Object getBean() {
    return this.bean;
  }

  public void setBean(Object bean) {
    this.bean = bean;
  }

  public Class getBeanclass() {
    return this.beanClass;
  }

  public void setClassname(String name) {
    this.ClassName = name;
    try {
      this.beanClass = Class.forName(name);
    } catch (ClassNotFoundException e) {
      e.printStackTrace();
    }
  }

  public PropertyValues getPropertyValues() {
    return this.propertyValues;
  }

  public void setPropertyValues(PropertyValues pv) {
    this.propertyValues = pv;
  }
}
```

定义接口`IBeanDefinitionReader`通过读取并解析`xml文件`或者利用java本身的`annotation机制`等获取被管理资源的meta信息创建资源的BeanDefinition实例，然后register到BeanFactory中。IBeanDefinitionReader的具体实现我们这里不再赘述。

BeanFactory中的`doCreate`方法是真正创建资源实例的地方，需要递归的的从BeanDefinition中获取资源的构造函数并创建。我们通过`AutowireBeanFactory`类来简单实现这一逻辑，Spring中数千行的DefaultListableBeanFactory类就相当于该类。

```java
public class AutowireBeanFactory extends AbstractBeanFactory {
  @Override
  protected Object doCreate(BeanDefinition beandefinition) throws Exception {
    Object bean = beandefinition.getBeanclass().newInstance();
    addPropertyValue(bean, beandefinition);
    return bean;
  }
}
```

然后结合java的annotation实现`@Autowire`,`@Resource`,`@Inject`等调用特定的getBean即实现了一个简单的IoC容器。

## AOP

AOP(Aspect Oriented Programming)是面向切面编程，就是在不改变原来代码逻辑的前提下对源代码中放法、类的一些属性与逻辑做修改。这样有什么好处呢，显然一些支撑性工作非常适合用AOP比如，统计每个函数的执行时间，监控函数的调用，拦截一些特定函数的执行。

要理解什么是AOP我们需要看看他实现的原理。如果要监控函数的执行时间，首先我们想到的就是在函数体执行的开始记录一下时间，函数执行完成后再记录一下时间，顺着这个思路我们在每个方法执行的开始于结束部分都添加相应的监控代码显然是非常费力而且难以维护的。

由于java是编译成字节码运行在java虚拟机上的，通过操作java字节码或者hook虚拟机调用函数时的钩子我们就能接管过函数的执行过程，在这个过程中的上下文中加入我们时间统计代码即可完成对函数直接时间的统计。

### AOP的简单实现

我们有一个简单的接口IHello

```java
public class Hello implements IHello {
    public void sayHello(String name) {
        System.out.println("Hello " + name);
    }
    public void sayGoogBye(String name) {
        System.out.println(name+" GoodBye!");
    }
}


import java.lang.reflect.Method;
public class LoggerOperation implements IOperation {
    public void end(Method method) {
        //Logger.logging(Level.DEBUGE, method.getName() + " Method end .");
    }
    public void start(Method method) {
        Logger.logging(Level.INFO, method.getName() + " Method Start!");
    }
}
```

jvm虚拟机为我们提供了反射代理接口实现的方法，需要实现`java.lang.reflect.InvocationHandler`，并完成invoke方法

```java
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;

public class DynaProxyHello implements InvocationHandler {
    private Object proxy;
    private Object delegate;

    public Object bind(Object delegate,Object proxy) {
       
        this.proxy = proxy;
        this.delegate = delegate;
        return Proxy.newProxyInstance(
                this.delegate.getClass().getClassLoader(), this.delegate
                        .getClass().getInterfaces(), this);
    }

    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        Object result = null;
        try {
            Class clazz = this.proxy.getClass();
            Method start = clazz.getDeclaredMethod("start",new Class[] { Method.class });
            start.invoke(this.proxy, new Object[] { method });
            result = method.invoke(this.delegate, args);
            Method end = clazz.getDeclaredMethod("end",new Class[] { Method.class });
            end.invoke(this.proxy, new Object[] { method });
        } catch (Exception e) {
            e.printStackTrace();
        }
        return result;
    }
}
```

让后在主函数中使用DynaProxyHello

```java
public class Test {
    public static void main(String[] args) {
        IHello hello = (IHello)new DynaProxyHello().bind(new Hello(),new LoggerOperation());
        hello.sayGoogBye("Double J");
        hello.sayHello("Double J");       
    }
}
```

## 其他AOP的实现方式

上面通过jvm动态接口代理实现了AOP，但是由于jvm限制只能够代理接口的方法。在Spring AOP中还提供了使用`cglib`包动态生成jvm字节码继承类而代理该类方法。由于使用的是继承，因此它无法代理标有final的类。

上面两种方法都是运行时的代理。此外，`AspectJ`通过代码生成结合特定的编译器插件实现了在编译器对方法的代理操作，由于是代码级别的，AspectJ能够代理所有的接口和类，包括final标记的类。

我们来看下 Spring AOP 与 AspectJ 的不同：

|Spring AOP|AspectJ|
|--------------|-------------------|
|纯Java语言层面|Java代码生成、编译器插件等|
|不需要其他的编译过程|除非设置了LTW，否则需要AspectJ编译器（ajc）|
|只有运行时代理|不支持运行时代理，只支持编译时、加载时代理|
|不够强大，只支持方法级别|支持所有属性、方法、构建函数、final类等|
|只能代理Sprint容器管理的类|支持所有对象|
|只支持方法作为切入点|支持所有切入点|
|使用反射，性能不如AspectJ|运行时性能优于Spring AOP|    