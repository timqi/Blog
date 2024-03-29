- tags: [android](/tags.md#android)
- date: 2016-12-07

# View ClipBound

应用开发中有很多要为 View 定制的情况，比如下面三种气泡，显然用 9patch 的方式不够灵活，三角处的颜色不好处理。但如果我们能限制起 View 绘制的边界为气泡的形状，那么只需要通常的布局方法就能轻松的完成下图的效果。本文涉及 View 绘制的过程，Path 使用方法。

![2016 12 07 View ClipBound [android] cd628d77fc1c40e082778487d0eb59b9/2016-12-07-1.png](/images/2016-12-07-1.png)

![2016 12 07 View ClipBound [android] cd628d77fc1c40e082778487d0eb59b9/2016-12-07-2.png](/images/2016-12-07-2.png)

![2016 12 07 View ClipBound [android] cd628d77fc1c40e082778487d0eb59b9/2016-12-07-3.png](/images/2016-12-07-3.png)

首先我们清楚 Android 每个页面中只有一个 Canvas，View 树的递归绘制仅仅是对这个 canvas 的裁剪重定位，通常使用 [canvas.clipRect](https://github.com/android/platform_frameworks_base/blob/master/graphics/java/android/graphics/Canvas.java#L685)。如果通过自定义的 [Path](https://github.com/android/platform_frameworks_base/blob/master/graphics/java/android/graphics/Path.java) 来限定 Canvas 的有效范围，那么 View 的有效绘制范围就被限定在 Path 中，从而简化内部布局的复杂度。

那么在什么场景下对 Canvas 进行限制呢，我们来看一下 view 的绘制过程（假设此时已经完成 mesarue 与 layout）。[android.view.View](https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/View.java)

- draw
- dispatchDraw
- onDraw

[View#draw](https://github.com/android/platform_frameworks_base/blob/master/core/java/android/view/View.java#L17154)

```java
/**
 * Manually render this view (and all of its children) to the given Canvas.
 * The view must have already done a full layout before this function is
 * called.  When implementing a view, implement
 * {@link #onDraw(android.graphics.Canvas)} instead of overriding this method.
 * If you do need to override this method, call the superclass version.
 *
 * @param canvas The Canvas to which the View is rendered.
 */
public void draw(Canvas canvas) {

  ...

  /*
   * Draw traversal performs several drawing steps which must be executed
   * in the appropriate order:
   *
   *      1. Draw the background
   *      2. If necessary, save the canvas' layers to prepare for fading
   *      3. Draw view's content
   *      4. Draw children
   *      5. If necessary, draw the fading edges and restore layers
   *      6. Draw decorations (scrollbars for instance)
   */

   ...

   dispatchDraw(canvas);
}

```

绘制过程中一次调用了 draw -> dispatchDraw -> onDraw。通常我们会想到在 onDraw 中裁剪 canvas，然而此时 background 已经绘制过了，所以我们需要在 draw 的时候就裁剪 canvas，然后在绘制完成后将边界绘制到 canvas 上。

重写 LinearLayout（当然也可以是其他的 View 或 ViewGroup）ChatBubbleLinearLayout.java:

```java
public class ChatBubbleLinearLayout extends LinearLayout {

    private int mBubbleDirection = 0;

    public ChatBubbleLinearLayout(Context context) {
        super(context);
    }

    public ChatBubbleLinearLayout(Context context, AttributeSet attrs) {
        super(context, attrs);
        TypedArray a = context.getTheme().obtainStyledAttributes(
                attrs,
                R.styleable.chatBubble,
                0, 0);

        try {
            mBubbleDirection = a.getInteger(R.styleable.chatBubble_direction, 0);
        } finally {
            a.recycle();
        }
    }

    @Override
    public void draw(Canvas canvas) {
        Rect clipBounds = canvas.getClipBounds();
        int width = clipBounds.width();
        int height = clipBounds.height();
        Path clipPath = mBubbleDirection == 0 ? 
          ChatPathCreator.getLeftPath(width, height) : 
          ChatPathCreator.getRightPath(width, height);

        // 限制 canvas 绘制区域
        canvas.clipPath(clipPath);

        super.draw(canvas);

        // 绘制边界
        canvas.drawPath(clipPath, ChatPathCreator.getOutlinePaint());
    }
}

```

接下来看看 Path。有关 [Path 的使用](https://github.com/GcsSloop/AndroidNote/blob/master/CustomView/Advance/%5B05%5DPath_Basic.md)，上面的系列文章讲得已经很详细了，这里不在赘述。Path 描述了路径信息，可以理解为一些矢量形状的集合。

那么我们构建一个类来专门构建气泡所需要的 Path，以及绘制气泡边界的画笔，从而将 View 于 Path 解耦，这样可以更加轻松的自定义其他类型的气泡 View，甚至可以使用这个 Path 结合 Glide 的 BitmapTransformation 和 Xfermode 裁剪 Bitmap。

ChatPathCreator.java:

```java
public class ChatPathCreator {

    private static int dpRadius;
    private static int dpAngleWidth;
    private static int dpAngleHeight;
    private static int dpAngleMarginTop;

    private static Paint mOutlinePaint;

    static {
        dpRadius = dp2px(5);
        dpAngleWidth = dp2px(6);
        dpAngleHeight = dp2px(6);
        dpAngleMarginTop = dp2px(4);

        mOutlinePaint = new Paint();
        mOutlinePaint.setAntiAlias(true);
        mOutlinePaint.setColor(App.getCtx().getResources().getColor(R.color.bgDivider));
        mOutlinePaint.setStyle(Paint.Style.STROKE);
        mOutlinePaint.setStrokeWidth(dp2px(1));
    }

    public static Paint getOutlinePaint() {
        return mOutlinePaint;
    }

    public static Path getRightPath(int width, int height) {
        Path path = new Path();
        path.moveTo(dpRadius, 0);
        path.lineTo(width - dpAngleWidth - dpRadius, 0);
        RectF oval = new RectF(width - dpAngleWidth - dpRadius * 2, 0, width - dpAngleWidth, dpRadius * 2);
        path.arcTo(oval, 270, 90, false);
        path.lineTo(width - dpAngleWidth, dpRadius + dpAngleMarginTop);
        path.lineTo(width, dpRadius + dpAngleMarginTop + dpAngleHeight);
        path.lineTo(width - dpAngleWidth, dpRadius + dpAngleMarginTop + dpAngleHeight * 2);
        path.lineTo(width - dpAngleWidth, height - dpRadius);
        oval = new RectF(width - dpAngleWidth - dpRadius * 2, height - dpRadius * 2, width - dpAngleWidth, height);
        path.arcTo(oval, 0, 90, false);
        path.lineTo(dpRadius, height);
        oval = new RectF(0, height - dpRadius * 2, dpRadius * 2, height);
        path.arcTo(oval, 90, 90, false);
        path.lineTo(0, dpRadius);
        oval = new RectF(0, 0, dpRadius * 2, dpRadius * 2);
        path.arcTo(oval, 180, 90, false);
        path.close();
        return path;
    }

    public static Path getLeftPath(int width, int height) {
        Path path = new Path();
        path.moveTo(dpRadius, 0);
        path.lineTo(width - dpRadius, 0);
        RectF oval = new RectF(width - dpRadius * 2, 0, width, dpRadius * 2);
        path.arcTo(oval, 270, 90, false);
        path.lineTo(width, height - dpRadius);
        oval = new RectF(width - dpRadius * 2, height - dpRadius * 2, width, height);
        path.arcTo(oval, 0, 90, false);
        path.lineTo(dpAngleWidth + dpRadius, height);
        oval = new RectF(dpAngleWidth, height - dpRadius * 2, dpAngleWidth + dpRadius * 2, height);
        path.arcTo(oval, 90, 90, false);
        path.lineTo(dpAngleWidth, dpRadius + dpAngleMarginTop + dpAngleHeight * 2);
        path.lineTo(0, dpRadius + dpAngleMarginTop + dpAngleHeight);
        path.lineTo(dpAngleWidth, dpRadius + dpAngleMarginTop);
        path.lineTo(dpAngleWidth, dpRadius);
        oval = new RectF(dpAngleWidth, 0, dpAngleWidth + dpRadius * 2, dpRadius * 2);
        path.arcTo(oval, 180, 90, false);
        path.close();
        return path;
    }
}

```

在布局中使用 ChatBubbleLinearLayout

```xml
<com.bixin.bixin_android.modules.chat.clipview.ChatBubbleLinearLayout
    xmlns:custom="http://schemas.android.com/apk/res-auto"
    android:layout_width="211dp"
    android:layout_height="70.5dp"
    android:orientation="vertical"
    custom:direction="right"
    >

  <LinearLayout
    android:layout_width="match_parent"
    android:layout_height="0dp"
    android:layout_weight="1"
    android:background="@color/qrBlue"
    android:orientation="horizontal"
    >

    <ImageView
      android:layout_width="33dp"
      android:layout_height="33dp"
      android:layout_gravity="center_vertical"
      android:layout_marginLeft="12dp"
      android:src="@drawable/bill_chat"
      />

    <LinearLayout
      android:layout_width="wrap_content"
      android:layout_height="wrap_content"
      android:layout_gravity="center_vertical"
      android:layout_marginLeft="11dp"
      android:orientation="vertical"
      >

      <TextView
        android:id="@+id/title"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:maxLines="1"
        android:text="转账"
        android:textColor="@color/white"
        android:textSize="15sp"
        />

      <TextView
        android:id="@+id/desc"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="2dp"
        android:maxLines="1"
        android:text="金额"
        android:textColor="@color/white"
        android:textSize="9sp"
        />

    </LinearLayout>

  </LinearLayout>

  <TextView
    android:id="@+id/comment"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:paddingBottom="2.5dp"
    android:paddingLeft="11dp"
    android:paddingTop="2.5dp"
    android:text="测试支付"
    android:textColor="@color/bcLightBlack"
    android:textSize="10sp"
    />
</com.bixin.bixin_android.modules.chat.clipview.ChatBubbleLinearLayout>

```

这样只需要在 ChatBubbleLinearLayout 中布局内容即可，边界会自动控制在气泡范围内。

![2016 12 07 View ClipBound [android] cd628d77fc1c40e082778487d0eb59b9/2016-12-07-3 1.png](/images/2016-12-07-4.png)