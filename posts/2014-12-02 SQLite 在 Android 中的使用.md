- tags: [android](/tags.md#android)
- date: 2014-12-02

# SQLite 在 Android 中的使用

项目源码地址：[SQLite应用](https://github.com/timqi/android-code-samples/tree/master/SQLite)

SQLite 是一个轻量级的数据库，只支持部分常用 SQL 指令，但是体积大小只有几千字节，操作灵活，在一些特殊使用场景下有着非常独特的优势。

在某些情况下，使用文件时无效的：

- 多线程访问数据
- 需要事物处理
- 应用程序需要处理需要变化的复杂数据结构
- 数据库对于创建他们的包套件是私有的

## 创建数据库

一般创建一个继承自 SQLiteOpenHelper 专门的数据库管理的类：

```java
public class Db extends SQLiteOpenHelper {
    public Db(Context context) {
        super(context, "db", null, 1);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE user(" +
                "_id INTEGER PRIMARY KEY AUTOINCREMENT, " +
                "name TEXT DEFAULT \"\"," +
                "age TEXT DEFAULT \"\")");
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
    }
}

```

当类的构造函数中传进的数据库版本提高时系统会执行 onUpgrade 来适应变化

## 增删改查基本操作

首先我们需要获取数据库操作的工具：

```java
private Db db = new Db(this);
private SQLiteDatabase dbreader = db.getReadableDatabase();
private SQLiteDatabase dbwriter = db.getWritableDatabase();

```

### 增加或者修改

```java
ContentValues cv = new ContentValues();
cv.put("name", name);
cv.put("age", age);
if (request == "ADD")
    dbwriter.insert("user", null, cv);
else if (request == "MODIFY")
    dbwriter.update("user", cv, "_id=?", new String[]{itemId+""});

```

## 删除与查找

```java
dbwriter.delete("user", "_id=?", new String[]{itemId+""});

// 直接摘自源程序的一部分
Cursor c = dbreader.query("user", new String[]{"name", "age"}, "name=?",
                    new String[]{et.getText().toString()}, null, null, null);
if (c.getCount() == 0)
    new AlertDialog.Builder(this).setMessage("No result Found").create().show();
else  {
    String message = "";
    while (c.moveToNext())
        message += ("\nname: "+c.getString(c.getColumnIndex("name"))
                +"\nage: "+c.getString(c.getColumnIndex("age"))+"\n");
    new AlertDialog.Builder(this).setMessage(message).create().show();
}

```

其中主要要了解 Cursor 对象，它实际上就是一个简单的指针，从查询结果的一个元组（一行）跳到下一个元组，Cursor 的位置总要停在将要读取的数据的前一行。