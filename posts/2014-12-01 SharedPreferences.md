- tags: [android](/tags.md#android)
- date: 2014-12-01

# SharedPreferences

SharedPredferences 是系统存储的一种基本方法，它能够高效的存储一些常用键值对，非常适合做系统状态的保存介质。

Android 系统中有一下几种存储数据的方法：

- Shared Preferences
- 存储到文件
- SQLite 数据库
- 存储到网络
- Content Provider

SharedPreferences 实质上是用 xml 文件存放的各种键值数据的轻量级存储类，文件的存放路径为：/data/data/${package name}/shared_prefs 目录下

## 存入

```java
private SharedPreferences sp = getSharedPreferences("mysp", MODE_PRIVATE);
Editor edt = sp.edit();
edt.putInt("age", 35);
edt.putBoolean("new", true);
edt.commit();

```

以上是存入操作的基本过程，

- getSharedPreferences(name, mode) 方法
    - 参数1：指定该文件名称，名称不带后缀
    - 参数2：指定文件操作模式，共有四种模式
        - Context.MODE_PRIVATE：默认模式，只能被应用本身访问，写入的内容会覆盖原内容
        - Context.MODE_APPEND：检查文件是否存在，若存在就在文件末尾追加，若不存在则创建
        - Context.MODE_WORLD_READBLE 与 Context.MODE_WORLD_WRITEADBLE：控制其它应用是否有权读写
- getSharedPreferences(mode) 这个函数使用当前类不带包名的类名作为文件名称
- 应用程序（.apk）安装时，系统会分配给它一个 userid 来管理相关权限

## 读取

```java
private SharedPreferences sp = getSharedPreferences("mysp", MODE_PRIVATE);
int age = sp.getInt("age");
bool new = sp.getBoolean("new");

```

### 访问其它应用的 SharedPreferences

需要其它应用指定 WORLD 的 mode，**然后先创建其它应用的 context，通过这个 context 访问 SharedPreferences**：

```java
Context otherApp = createPackageContext("packageName", Context.CONTEXT_IGNORE_SECURITY);
private SharedPreferences sp = otherApp.getSharedPreferences("mysp", MODE_WORLD_READBLE);

```