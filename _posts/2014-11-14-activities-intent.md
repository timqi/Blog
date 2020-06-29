---
title: Activities 间使用 Intent 交换信息
category: [android]
---

在Android系统中，Activities表示了app与用户交互的一个界面所有元素与行为，而在不同的Activities之间进行数据通信则需要使用Intent实力进行。
<!--more-->

在 Android 中， 每个 Activity 表示了 app 与用户进行交互的一个界面所有的元素与行为的定义，用户在不同的 Activities 之间进行切换就必然涉及到系统不同 Activities 之间的通信。

系统为每个 Activity 定义了一个 Intent 实例， 一般这 Intent 实例是由系统创建 Activity 的时候指定的，我们可以通过`getIntent()`方法获得系统制定的 Intent 实例，从而得到其中的信息。

我们可以在被启动的第二个 activity 的 onCreate() 函数中读出 Intent 实例中的信息：

``` java
@Override
public void onCreate(Bundle savedInstanceState) {
	super.onCreate(savedInstanceState);

	// Get the message from the intent
	Intent intent = getIntent();
	String message = intent.getStringExtra(MainActivity.EXTRA_MESSAGE);

	// Create the text view
	TextView textView = new TextView(this);
	textView.setTextSize(40);
	textView.setText(message);

	// Set the text view as the activity layout
	setContentView(textView);
}
```

既然是要通信，那么就至少需要需要有两个 activities ，一个发送消息，一个接受消息，上面介绍了怎样获取也就是接受消息，那么下面来说下怎样向另一个 activity 发送信息。

首先，我们需要创建一个 Intent 实例，然后把需要发送的信息附加进 Intent 实例中，然后告诉系统创建新的 activity 的时候使用我们创建的 Intent 实例就行了。

``` java
public final static String EXTRA_MESSAGE = "com.example.myfirstapp.MESSAGE";

public void sendMessage(View view) {
	Intent intent = new Intent(this, DisplayMessageActivity.class);
	EditText editText = (EditText) findViewById(R.id.edit_message);
	String message = editText.getText().toString();
	intent.putExtra(EXTRA_MESSAGE, message);
	startActivity(intent);
}
```

其中`DisplayMessageActivity.class`指定了新的需要被启动的 activitiy 的类名，系统根据这个类名启动 app 的中一个类（也就是对应的activity）。`EXTRA_MESSAGE`变量相当于一个地址指定了系统中 message 这个唯一变量的内容，利于接收方查找信息。
