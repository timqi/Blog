---
title: TextView 显示全文与隐藏功能
category: android
---

经常遇到大段文本需要部分展示的场景，通常的做法是在隐藏的状态下文本末尾加上「显示全文」，在展开的状态下文本末尾加上「隐藏」来控制文本的展示状态。这个交互可能有很多种实现方法，本文则以一个简单的 TextView 来实现这些交互，封装后的 CollapsiableTextView 仅增加了不到 70 个额外的方法数。
<!--more-->

[Git 仓库地址：https://github.com/timqi/CollapsibleTextView](https://github.com/timqi/CollapsibleTextView)

![](https://raw.githubusercontent.com/timqi/CollapsibleTextView/master/art/CollapsedTextView.gif)

[Demo App 下载](https://github.com/timqi/CollapsibleTextView/raw/master/art/example-debug.apk)

## 参数定义

如上图效果，我们需要使用到几个可配置的参数：

```xml
<declare-styleable name="CollapsibleTextView">
  <attr name="suffixColor" format="color"/>
  <attr name="collapsedLines" format="integer"/>
  <attr name="collapsedText" format="string"/>
  <attr name="expandedText" format="string"/>
  <attr name="suffixTrigger" format="boolean"/>
</declare-styleable>
```

这几个参数分别表示

- 后缀颜色，也就是「显示全文」，「隐藏」这几个字的颜色
- 折叠后显示几行文字
- 折叠后的后缀文字，也就是「显示全文」
- 展开后的后缀文字，也就是「隐藏」
- 隐藏与展示的触发事件是点击后缀还是整个 TextView

主要的构造函数如：

```java
public CollapsibleTextView(Context context, AttributeSet attrs, int defStyleAttr) {
  super(context, attrs, defStyleAttr);
  TypedArray attributes = context.getTheme()
      .obtainStyledAttributes(attrs, R.styleable.CollapsibleTextView, defStyleAttr, 0);

  mSuffixColor = attributes.getColor(R.styleable.CollapsibleTextView_suffixColor, 0xff0000ff);
  mCollapsedLines = attributes.getInt(R.styleable.CollapsibleTextView_collapsedLines, 1);
  mCollapsedText = attributes.getString(R.styleable.CollapsibleTextView_collapsedText);
  if (TextUtils.isEmpty(mCollapsedText)) mCollapsedText = " Show All";
  mExpandedText = attributes.getString(R.styleable.CollapsibleTextView_expandedText);
  if (TextUtils.isEmpty(mExpandedText)) mExpandedText = " Hide";
  mSuffixTrigger = attributes.getBoolean(R.styleable.CollapsibleTextView_suffixTrigger, false);

  this.mText = getText() == null ? null : getText().toString();
  setMovementMethod(LinkMovementMethod.getInstance());
  super.setOnClickListener(mClickListener);
}
```

## 代理 onClick 事件

为了配置是否由后缀触发显示与隐藏操作，我们要在 CollapsibleTextView 中处理点击事件。所以在构造函数中设置 clickListener 为 mClickListener。同时在 mClickListener 中处理点击事件：

```java
private OnClickListener mClickListener = new OnClickListener() {
  @Override
  public void onClick(View v) {
    if (!mSuffixTrigger) {
      mExpanded = !mExpanded;
      applyState(mExpanded);
    }

    if (mCustomClickListener != null) {
      mCustomClickListener.onClick(v);
    }
  }
};
```

为了用户仍可以设置 clickListener 我们重写 setOnClickListener 方法，并保留 clickListener 为 mCustomClickListener:

```java
@Override
public void setOnClickListener(OnClickListener l) {
  mCustomClickListener = l;
}
```

这样就将 click 事件代理到了 CollapsibleTextView 内部。

## ClickableSpan 处理部分文本点击

为了能够监听后缀的点击事件，需要使用 ClickableSpan 

```java
str.setSpan(mClickSpanListener,
  note.length(),
  note.length() + suffix.length(),
  SpannableString.SPAN_EXCLUSIVE_EXCLUSIVE);

// ClickableSpan
private ClickableSpan mClickSpanListener
    = new ClickableSpan() {
  @Override
  public void onClick(View widget) {
    if (mSuffixTrigger) {
      mExpanded = !mExpanded;
      applyState(mExpanded);
    }
  }

  @Override
  public void updateDrawState(TextPaint ds) {
    super.updateDrawState(ds);
    ds.setUnderlineText(false);
  }
};
```

## 根据状态计算出 SpannableString

```java
private void applyState(boolean expanded) {
  if (TextUtils.isEmpty(mText)) return;

  String note = mText, suffix;
  if (expanded) {
    suffix = mExpandedText;
  } else {
    if (mCollapsedLines - 1 < 0) {
      throw new RuntimeException("CollapsedLines must equal or greater than 1");
    }
    int lineEnd = getLayout().getLineEnd(mCollapsedLines - 1);
    suffix = mCollapsedText;
    int newEnd = lineEnd - suffix.length() - 1;
    int end = newEnd > 0 ? newEnd : lineEnd;

    TextPaint paint = getPaint();
    int maxWidth = mCollapsedLines * (getMeasuredWidth() - getPaddingLeft() - getPaddingRight());
    while (paint.measureText(note.substring(0, end) + suffix) > maxWidth)
      end--;
    note = note.substring(0, end);
  }

  final SpannableString str = new SpannableString(note + suffix);
  if (mSuffixTrigger) {
    str.setSpan(mClickSpanListener,
        note.length(),
        note.length() + suffix.length(),
        SpannableString.SPAN_EXCLUSIVE_EXCLUSIVE);
  }
  str.setSpan(new ForegroundColorSpan(mSuffixColor),
      note.length(),
      note.length() + suffix.length(),
      SpannableString.SPAN_EXCLUSIVE_EXCLUSIVE);
  post(new Runnable() {
    @Override
    public void run() {
      setText(str);
    }
  });
}
```

其中 `paint.measureText` 可以测量出文本布局的宽度从而得只文本行数并与 mCollapsedLines 比较裁剪出合适的字符长度并添加上后缀与 span 赋予 TextView 即可

由于 getLineEnd 等函数只有在 layout 过程之后值才有意义，所以要合理的选择 applyState 的时机：  

```java
@Override
protected void onLayout(boolean changed, int left, int top, int right, int bottom) {
  super.onLayout(changed, left, top, right, bottom);
  if (mShouldInitLayout && getLineCount() > mCollapsedLines) {
    mShouldInitLayout = false;
    applyState(mExpanded);
  }
}
```

至此 CollapsibleTextView 的要点已经完成，添加上 getter，setter 函数与一些逻辑组织即可，具体见文件 [CollapsibleTextView.java](https://github.com/timqi/CollapsibleTextView/blob/master/library/src/main/java/com/timqi/collapsibletextview/CollapsibleTextView.java).

[Git 仓库地址：https://github.com/timqi/CollapsibleTextView](https://github.com/timqi/CollapsibleTextView)
