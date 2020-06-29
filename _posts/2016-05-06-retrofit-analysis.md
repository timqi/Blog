---
title: Retrofit 2.0 源码解析
category: android
---

Retrofit 使用方法在 [这里](http://square.github.io/retrofit/) 查看，本文针对 [db2fcf3](https://github.com/square/retrofit/commit/db2fcf31b3e9e1a52d8b0081c711324fcfb62683) 版本源码进行分析。
<!--more-->

先看一个简单的 retrofit 使用场景，定义一个获取 REST 数据的接口，如 GitHubService

```java
public interface GitHubService {
  @GET("users/{user}/repos")
  Call<List<Repo>> listRepos(@Path("user") String user);
}
```
使用 retrofit.create 便可获取这个完成了这个接口功能的对象

```java
Retrofit retrofit = new Retrofit.Builder()
    .baseUrl("https://api.github.com/")
    .build();

GitHubService service = retrofit.create(GitHubService.class);
```

REST API 的访问过程基本没有任何胶水代码，直接了当。 retrofit 使用注解的方式获取了构建请求所需的所有信息，通过 Java SDK 提供的动态代理功能接管接口中的每个方法，构建去相应的网络请求对象并将句柄返回。

# 动态代理

[代理设计模式](https://en.wikipedia.org/wiki/Proxy_pattern) 在 wikipedia 上有详细的解释：

> Use of the proxy can simply be forwarding to the real object, or can provide additional logic. In the proxy extra functionality can be provided, for example caching when operations on the real object are resource intensive, or checking preconditions before operations on the real object are invoked. For the client, usage of a proxy object is similar to using the real object, because both implement the same interface.

代理类可以简单的仅仅完成被代理函数的功能，也可以在此基础上添加日志，性能分析等功能。从实现上来讲我们不一定对每一个需要被代理的方法编写一个代理函数，我们可以借助 Java SDK 把一个接口中的所有方法均代理到一个入口中，大概像下面这样

```java
public class DynamicProxy {

  public static interface MyInterface {
    int sum(int arg1,int arg2);
    MyInterface returnMySelf();
  }

  public static void main(String args[]) {
    Object object = Proxy.newProxyInstance(
        MyInterface.class.getClassLoader(),
        new Class[]{MyInterface.class},
        new InvocationHandler() {
          @Override
          public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
            if (method.getName().equals("sum")) {
              return (int)args[0]+(int)args[1];
            }
            if (method.getName().equals("returnMySelf")) {
              return proxy;
            }
            return null;
          }
        });
    MyInterface myInterface = (MyInterface)object;
    System.out.println("1+2="+myInterface.sum(1, 2));
  }
}
```

通过 Proxy.newProxyInstance 产生了一个 MyInterface 的实例，得到这个实例后，我们便可以调用它的方法 sum，我们来看一下这个实例怎样通过接口产生的

## newProxyInstance

JDK 中 newProxyInstance 源码如下

```java
public static Object newProxyInstance(ClassLoader loader,
                                      Class<?>[] interfaces,
                                      InvocationHandler h)
    throws IllegalArgumentException
{
  //权限判断等，忽略
  //生成代理类
  Class<?> cl = getProxyClass0(loader, intfs);
  //调用构造器，生成实例
    final Constructor<?> cons = cl.getConstructor(constructorParams);
    final InvocationHandler ih = h;
    if (!Modifier.isPublic(cl.getModifiers())) {
      AccessController.doPrivileged(new PrivilegedAction<Void>() {
        public Void run() {
            cons.setAccessible(true);
            return null;
        }
      });
    }
    return cons.newInstance(new Object[]{h});
  } catch (IllegalAccessException|InstantiationException e) {
    //各种异常处理
  }
}
```

getProxyClass0 代码如下：

```java
private static Class<?> getProxyClass0(ClassLoader loader,
                                     Class<?>... interfaces) {
  if (interfaces.length > 65535) {
    throw new IllegalArgumentException("interface limit exceeded");
  }

  //此处根据 classloader 和 interfaces 对 Proxy 做了一次缓存，如果缓存中不存在则生成它

  byte[] proxyClassFile = ProxyGenerator.generateProxyClass(proxyName, interfaces);
  try {//将字节码加载到JVM
    proxyClass = defineClass0(loader, proxyName, proxyClassFile, 0, proxyClassFile.length);
  }
  retrun proxyClass;
}
```

至此，我们根据预定义的接口生成了一个代理类，这个代理类实现了所有预定接口的方法，并通过预定义接口的 classloader 将这个生成代理类加载到 JVM 虚拟机

# Retrofit 生成 REST 服务实例

```java
public <T> T create(final Class<T> service) {
  Utils.validateServiceInterface(service);
  if (validateEagerly) {
    eagerlyValidateMethods(service);
  }
  return (T) Proxy.newProxyInstance(service.getClassLoader(),
      new Class<?>[] { service },
      new InvocationHandler() {
        private final Platform platform = Platform.get();

        @Override public Object invoke(Object proxy, Method method, Object... args)
            throws Throwable {
          // If the method is a method from Object then defer to normal invocation.
          if (method.getDeclaringClass() == Object.class) {
            return method.invoke(this, args);
          }
          if (platform.isDefaultMethod(method)) {
            return platform.invokeDefaultMethod(method, service, proxy, args);
          }
          ServiceMethod serviceMethod = loadServiceMethod(method);
          OkHttpCall okHttpCall = new OkHttpCall<>(serviceMethod, args);
          return serviceMethod.callAdapter.adapt(okHttpCall);
        }
      });
}
```

我们可以看到，Retrofit 实际上对 REST 服务接口做了一个动态代理，并返回一个实例，完成实际的 http 请求。

在 InvocationHandler 的 invoke 方法中我们可以得到预定接口方法的方法名，返回值类型，注解类型与值等相关信息，通过这些构建出 ServiceMethod 实例，这是 Retrofit 中最核心的一个类，通过 ServiceMethod 中存储的请求信息向网络方向可以根据 Call 构建出真实的请求实体进行网络请求，通过 Convet 将返回的 http 信息解析成 java 对象方便程序访问。

# CallAdapter 与 Converter

retrofit 对网络请求各层封装进行了非常透彻的解偶， 其中 Call 实现了底层网络的适配，比如 HttpClient，HttpURLConnection，Okhttp，当然在 Retrofit2.0 中网络请求更加依赖 Okhttp，仅添加了 Okhttp 的支持；通过设置不同的 Converter，可以实现不同数据格式如 xml，json 等到 java 对象的转化，并且 Converter 这部分的代码转移到了其它包中尽可能的减小了 retrofit 本身的大小；CallAdapter 的灵活配置实现了对不同返回类型的支持，比如添加 RxJava 支持的返回类型 Obsverable 类型。

最终当调用 api 的时候，比如：`Call<List<Repo>> repos = service.listRepos("octocat");`。实际运行的是代理类的 InvocationHandler 的 invoke 方法。在构建出 serviceMethod 与 call 对象后返回了 serviceMethod.callAdapter.adapt(okHttpCall);

在 Android 平台，我们使用了 ExecutorCallAdapterFactory 封装网络请求为一个 Call 并将请求结果转发到主线程

```java
//ExecutorCallAdapterFactory.java

@Override
public CallAdapter<Call<?>> get(Type returnType, Annotation[] annotations, Retrofit retrofit) {
  if (getRawType(returnType) != Call.class) {
    return null;
  }
  final Type responseType = Utils.getCallResponseType(returnType);
  return new CallAdapter<Call<?>>() {
    @Override public Type responseType() {
      return responseType;
    }

    @Override public <R> Call<R> adapt(Call<R> call) {
      return new ExecutorCallbackCall<>(callbackExecutor, call);
    }
  };
}

static final class ExecutorCallbackCall<T> implements Call<T> {
  final Executor callbackExecutor;
  final Call<T> delegate;

  ExecutorCallbackCall(Executor callbackExecutor, Call<T> delegate) {
    this.callbackExecutor = callbackExecutor;
    this.delegate = delegate;
  }

  @Override public void enqueue(final Callback<T> callback) {
    if (callback == null) throw new NullPointerException("callback == null");

    delegate.enqueue(new Callback<T>() {
      @Override public void onResponse(Call<T> call, final Response<T> response) {
        callbackExecutor.execute(new Runnable() {
          @Override public void run() {
            if (delegate.isCanceled()) {
              // Emulate OkHttp's behavior of throwing/delivering an IOException on cancellation.
              callback.onFailure(ExecutorCallbackCall.this, new IOException("Canceled"));
            } else {
              callback.onResponse(ExecutorCallbackCall.this, response);
            }
          }
        });
      }

      @Override public void onFailure(Call<T> call, final Throwable t) {
        callbackExecutor.execute(new Runnable() {
          @Override public void run() {
            callback.onFailure(ExecutorCallbackCall.this, t);
          }
        });
      }
    });
  }
}
```

ExecutorCallAdapterFactory 提供了基础的适配对象，并通过 Platform 加入到 retrofit 对象中。

对于网络请求结果的处理上，Retrofit 使用了 Converter 将 ResponseBody 转化为需要的 Java 数据对象，我们可以向 Retrofit 添加自定义 Converter 来处理 json 数据等

```java
/**
 * Convert objects to and from their representation in HTTP. Instances are created by {@linkplain
 * Factory a factory} which is {@linkplain Retrofit.Builder#addConverterFactory(Factory) installed}
 * into the {@link Retrofit} instance.
 */
public interface Converter<F, T> {
  T convert(F value) throws IOException;

  /** Creates {@link Converter} instances based on a type and target usage. */
  abstract class Factory {
    /**
     * Returns a {@link Converter} for converting an HTTP response body to {@code type}, or null if
     * {@code type} cannot be handled by this factory. This is used to create converters for
     * response types such as {@code SimpleResponse} from a {@code Call<SimpleResponse>}
     * declaration.
     */
    public Converter<ResponseBody, ?> responseBodyConverter(Type type, Annotation[] annotations,
        Retrofit retrofit) {
      return null;
    }

    /**
     * Returns a {@link Converter} for converting {@code type} to an HTTP request body, or null if
     * {@code type} cannot be handled by this factory. This is used to create converters for types
     * specified by {@link Body @Body}, {@link Part @Part}, and {@link PartMap @PartMap}
     * values.
     */
    public Converter<?, RequestBody> requestBodyConverter(Type type,
        Annotation[] parameterAnnotations, Annotation[] methodAnnotations, Retrofit retrofit) {
      return null;
    }

    /**
     * Returns a {@link Converter} for converting {@code type} to a {@link String}, or null if
     * {@code type} cannot be handled by this factory. This is used to create converters for types
     * specified by {@link Field @Field}, {@link FieldMap @FieldMap} values,
     * {@link Header @Header}, {@link HeaderMap @HeaderMap}, {@link Path @Path},
     * {@link Query @Query}, and {@link QueryMap @QueryMap} values.
     */
    public Converter<?, String> stringConverter(Type type, Annotation[] annotations,
        Retrofit retrofit) {
      return null;
    }
  }
}
```

Converter 定义了一个方法 `T convert(F value) throws IOException;` 和一个工厂类，这个工厂类提供了三种 Converter：

- responseBodyConverter: 最常用，将响应结果转化为 java 对象
- requestBodyConverter: 组装 reqeuest 的 body 体
- stringConverter: 处理接口定义的 @Field，@Header 等参数

这三个 Converter 实现了相应的数据转换。

在设置 retrofit 的 converters 时需要注意，设置的顺序问题，因为 retrofit 会顺序在备选项中查找合适的 converter，一旦找到立即返回并且不访问排在后面的 converter

```java
int start = adapterFactories.indexOf(skipPast) + 1;
for (int i = start, count = adapterFactories.size(); i < count; i++) {
  CallAdapter<?> adapter = adapterFactories.get(i).get(returnType, annotations, this);
  if (adapter != null) {
    return adapter;
  }
}
```

# 总结

使用 Retrofit 发送一个网络请求非常简单，只需要定义一个函数就好了；而且 Retrofit 具有非常好的扩展性，只需要制定 CallAdapter 活着 Converter 就能实现不同数据类型的访问；顶层的 Okhttp 性能非常好；支持请求取消。

但是 Retrofit 中没有对缓存提供额外支持，完全由 Okhttp 来实现，若要修改缓存策略需要服务端配合或者通过 Header 来 Hack 一些缓存的访问。


