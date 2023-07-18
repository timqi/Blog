- tags: [android](/tags.md#android)
- date: 2016-02-22

# butterknife 源码分析

[ButterKnife](https://github.com/JakeWharton/butterknife) 出自大神 [JakeWharton](https://github.com/JakeWharton) 之作，涉及到 Java 注解相关知识，本文主要讲述 ButterKnife ，基于源码版本 [6ab6fb5e98a9da8eeaecc4f8917f06adbc8b67a7](https://github.com/JakeWharton/butterknife/commit/6ab6fb5e98a9da8eeaecc4f8917f06adbc8b67a7)， 有关 Java 注解的相关知识请查看 [codeKK-公共技术点之 Java 注解 Annotation](http://a.codekk.com/detail/Android/Trinea/%E5%85%AC%E5%85%B1%E6%8A%80%E6%9C%AF%E7%82%B9%E4%B9%8B%20Java%20%E6%B3%A8%E8%A7%A3%20Annotation)

ButterKnife 项目有 4 个模块:

- butterknife：提供 ButterKnife API
- butterknife-annotations：定义诸如 @Bind, @OnClick 等注解
- butterknife-compiler：编译时对源代码预处理生成辅助类
- butterknife-sample：使用 butterknife 的示例项目

## 使用注解完成 view 绑定的过程

从使用者角度来看：主模块在类中使用注解标注 Field 与 view 的相关属性绑定，然后调用了 ButterKnife.bind(...) 完成绑定。

实际上在 ButterKnife 类中维护了一个 "Map<Class<?>, ViewBinder<Object>>" 类型的对象 **BINDERS**，它是由 LinkedHashMap 实现的，Key 值为 ButterKnife.bind() 传入的绑定目标的 Class 对象，比如某个 Activity 的 .class，某个 ViewHolder 的 .class 对象；Value 值为在 butterknife-compiler 模块中编译时生成的各种 $$ViewBinder 类，这些实例对象是通过反射得到 Class 对象并调用 newInstance 生成的。

bind() 的过程会首先根据需要绑定的目标的 Key 获取到相应的 ViewBinder，然后调用相应 ViewBinder 的 bind() 方法完成绑定。

ButterKnife 类中通过 findViewBinderForClass(Class<?> cls) 方法获取 ViewBinder 对象。findViewBinderForClass 方法会首先在 BINDERS 中查找是否有对应 Key 值为 cls 的 ViewBinder 实例，如果存在并且不为空就返回这个对象；如果 cls 是以 "android." 或 "java." 包名开头的框架类的话，就返回一个默认的 ViewBinder `NOP_VIEW_BINDER`，它的 bind 方法为空，不进行任何绑定操作；最后查找类名为当前类名加上 "$$ViewBinder" 为类名的类是否存在，如果存在就把它实例化并返回，同时把实例化后的 ViewBinder 对象存入 BINDERS 中以便方便下次查找；如果不存在则递归查找它的父类。

```java
@NonNull
private static ViewBinder<Object> findViewBinderForClass(Class<?> cls)
    throws IllegalAccessException, InstantiationException {
  ViewBinder<Object> viewBinder = BINDERS.get(cls);
  if (viewBinder != null) {
    if (debug) Log.d(TAG, "HIT: Cached in view binder map.");
    return viewBinder;
  }
  String clsName = cls.getName();
  if (clsName.startsWith("android.") || clsName.startsWith("java.")) {
    if (debug) Log.d(TAG, "MISS: Reached framework class. Abandoning search.");
    return NOP_VIEW_BINDER;
  }
  try {
    Class<?> viewBindingClass = Class.forName(clsName + "$$ViewBinder");
    //noinspection unchecked
    viewBinder = (ViewBinder<Object>) viewBindingClass.newInstance();
    if (debug) Log.d(TAG, "HIT: Loaded view binder class.");
  } catch (ClassNotFoundException e) {
    if (debug) Log.d(TAG, "Not found. Trying superclass " + cls.getSuperclass().getName());
    viewBinder = findViewBinderForClass(cls.getSuperclass());
  }
  BINDERS.put(cls, viewBinder);
  return viewBinder;
}

```

## $$ViewBinder 类的作用

诸如 $ViewBinder 的类是由 butterknife-compiler 模块生成的 java 代码源文件，类名的产生规则是以原类名（包含包名）加上 `$ViewBinder` 构成，这个 java 文件在编译时根据注解生成，具体的的生成过程由 butterknife-compiler 模块处理，在样例工程中生成的 SimpleActivity$$ViewBinder（butterknife-sample 模块的 build->generated 目录下）这个 ViewBinder 类的定义为：

```java
public class SimpleActivity$$ViewBinder<T extends SimpleActivity> implements ViewBinder<T>

```

我们看到这个类实现了 ViewBinder，ViewBinder 是一个接口，只有一个方法：

```java
void bind(Finder finder, T target, Object source);

```

在 $$ViewBinder 的 bind 方法中调用了 finder 类提供的几个工具方法最终完成了目标对象各属性对应的绑定工作，finder 主要简化兼容了各种 findViewById 的过程和错误处理。

## $$ViewBinder 类的生成过程，butterknife-compiler 模块

这个模块中涉及 java 语言注解的处理，RoundEnvironment，TypeElement 等一些程序元数据的使用方法，同时模块依赖 javapoet 项目生成 java 源码，本文重点在与分于 butterknife 原理，相关知识请读者自行补充：

- [codeKK-公共技术点之 Java 注解 Annotation](http://a.codekk.com/detail/Android/Trinea/%E5%85%AC%E5%85%B1%E6%8A%80%E6%9C%AF%E7%82%B9%E4%B9%8B%20Java%20%E6%B3%A8%E8%A7%A3%20Annotation)
- [square/javapoet](https://github.com/square/javapoet)

ButterKnifeProcessor 中的 process 是处理注解的核心方法;每个 BindingClass 对象中存储了生成每个 java 源码文件所需要的信息，BindingClass 提供生成 java 源码的方法 `brewJava()`，并写入对应文件中。

```java
@Override public boolean process(Set<? extends TypeElement> elements, RoundEnvironment env) {
  Map<TypeElement, BindingClass> targetClassMap = findAndParseTargets(env);

  for (Map.Entry<TypeElement, BindingClass> entry : targetClassMap.entrySet()) {
    TypeElement typeElement = entry.getKey();
    BindingClass bindingClass = entry.getValue();

    try {
      bindingClass.brewJava().writeTo(filer);
    } catch (IOException e) {
      error(typeElement, "Unable to write view binder for type %s: %s", typeElement,
          e.getMessage());
    }
  }

  return true;
}

```

targetClassMap 维护了需要生成的 java 类查询表，Key 是不同的 TypedElement，也就是每组注解所在的 Class，由 process 中的信息 .getEnclosingElement() 得到，Map 中的每条信息对应着一个待生成的 java 源文件。在 sample 中 `SimpleActivity` 和 `SimpleActivity$ViewHolder` 类对应的 TypedElement 即为这里 targetClassMap 的 Key 值。与 Key 值相对应的 bindingClass 类中存储了生成 java 文件 SimpleActivity$ViewBinder 和 SimpleAdapter$ViewHolder$ViewBinder 的所需信息。

这里的 targetClassMap 对象由 findAndParseTargets(env) 方法创建。

findAndParseTargets(env) 中分别根据不同的注解如 @Bind @BindArray @BindBitmap ...等 调用相应的解析方法构建出 bindingClass 对象并存储。

butterknife 提供了不同的注解工具，在解析的过程中都映射到了不同的 *Binding 对象如 FieldBitmapBinding, FieldViewBinding, MethodViewBinding ...等，findAndParseTargets 过程解析出了这个对象并根据其 Key 值存储在不同的 bindingClass 中分别对应不同的文件，并最终通过 brewJava() 构建出不同的 java 语句写入 $$ViewBinder 源文件中。

findAndParseTargets 过程根据绑定事件类型的不同而不同，但最终目的都如上所说为构建出相应的 bindingClass 类。我们以单个 View 的 id 绑定为例来解释这一过程：

```java
private void parseBindOne(Element element, Map<TypeElement, BindingClass> targetClassMap,
    Set<String> erasedTargetNames) {
  boolean hasError = false;
  TypeElement enclosingElement = (TypeElement) element.getEnclosingElement();

  // Verify that the target type extends from View.
  TypeMirror elementType = element.asType();
  if (elementType.getKind() == TypeKind.TYPEVAR) {
    TypeVariable typeVariable = (TypeVariable) elementType;
    elementType = typeVariable.getUpperBound();
  }
  if (!isSubtypeOfType(elementType, VIEW_TYPE) && !isInterface(elementType)) {
    error(element, "@%s fields must extend from View or be an interface. (%s.%s)",
        Bind.class.getSimpleName(), enclosingElement.getQualifiedName(), element.getSimpleName());
    hasError = true;
  }

  // Assemble information on the field.
  int[] ids = element.getAnnotation(Bind.class).value();
  if (ids.length != 1) {
    error(element, "@%s for a view must only specify one ID. Found: %s. (%s.%s)",
        Bind.class.getSimpleName(), Arrays.toString(ids), enclosingElement.getQualifiedName(),
        element.getSimpleName());
    hasError = true;
  }

  if (hasError) {
    return;
  }

  int id = ids[0];
  BindingClass bindingClass = targetClassMap.get(enclosingElement);
  if (bindingClass != null) {
    ViewBindings viewBindings = bindingClass.getViewBinding(id);
    if (viewBindings != null) {
      Iterator<FieldViewBinding> iterator = viewBindings.getFieldBindings().iterator();
      if (iterator.hasNext()) {
        FieldViewBinding existingBinding = iterator.next();
        error(element, "Attempt to use @%s for an already bound ID %d on '%s'. (%s.%s)",
            Bind.class.getSimpleName(), id, existingBinding.getName(),
            enclosingElement.getQualifiedName(), element.getSimpleName());
        return;
      }
    }
  } else {
    bindingClass = getOrCreateTargetClass(targetClassMap, enclosingElement);
  }

  String name = element.getSimpleName().toString();
  TypeName type = TypeName.get(elementType);
  boolean required = isFieldRequired(element);

  FieldViewBinding binding = new FieldViewBinding(name, type, required);
  bindingClass.addField(id, binding);

  // Add the type-erased version to the valid binding targets set.
  erasedTargetNames.add(enclosingElement.toString());
}

```

单个 View id 的绑定最终调用了 parseBindOne 方法。View id 绑定显然是类的属性（变量）绑定，这个方法中首先检验了需要绑定对象的类型是否为某个类的属性，如果不是就产生错误。然后获取注释中的 id。最后根据类名在 targetClassMap 中查找是否已经含有相应的 bindingClass，如果存在就把这个 bindingClass 对象取出，如果注释 id 已经在这个 bindingClass 绑定过就产生错误；如果 targetClassMap 中不存在相应的 bindingClass ，那么久创建一个新的 bindingClass 对象。最后将这个 View 的 id 绑定封装为一个 FieldViewBinding 对象并添加入刚才取得的 bindingClass 中，至此 parse 过程结束。

最后 BindingClass 的 brewJava 方法会根据它的 viewIdMap，collectionBindings，bitmapBindings，drawableBindings，resourceBindings... 信息构建出相应的 java 语句并写入文件以完成代码生成，具体的 java 语句生成逻辑很简单，依赖 [square/javapoet](https://github.com/square/javapoet) 项目，请读者自行分析。

至此，butterknife 的原理就很清楚了，根据最初源代码的注解生成绑定辅助类，运行时 ButterKnife.bind() 方法调用辅助类中的代码完成绑定。当然，完成绑定的过程中创建 $$ViewBinder 对象运用了反射，而且很多辅助类的创建增加了额外的内存开销，相比传统的 findViewById 的方法有一定性能消耗，但是对大多数普通应用而言这些牺牲是非常值得的。