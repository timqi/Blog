---
title: 没有游戏引擎节奏大师游戏
category: android
---
「单词消消乐」游戏推出后广受好评，迅速带动了用户增长。于是我们决定再接再厉决定在下一版推出一款新游戏，先上 Demo 一睹为快：
<!--more-->

<embed src="http://player.youku.com/player.php/sid/XMTQwNDIzODI5Ng==/v.swf" allowFullScreen="true" quality="high" width="480" height="400" align="middle" allowScriptAccess="always" type="application/x-shockwave-flash"></embed>

视频地址：[http://sr.timqi.com/demo/gameff](http://sr.timqi.com/demo/gameff)<br/>
优酷地址：[http://v.youku.com/v_show/id_XMTQwNDIzODI5Ng==.html](http://v.youku.com/v_show/id_XMTQwNDIzODI5Ng==.html)


在现有的 android 框架下，呈现到手机界面上的组件都是通过 measure，layout，draw 三个过程显示到屏幕上的，其中 measure 确定了每个组件的宽、高的大小，layout 则根据 measure 的结果确定组件在 window 中的布局位置，最后通过 draw 过程绘制到手机屏幕上，通常情况下根据 android view 框架的原理每个控件都是矩形的，很难实现出 3D 效果。

不过幸运的是 android 中 view 基类提供了 rotationX 属性来做一些简单的空间坐标变换，这个旋转变化是 3D 的，我们可以很轻松的使用这个属性实现游戏中跑道的透视，但是要达到游戏运行效果只利用这个特性还是远远不够的，本文就讲述如何实现上面 Demo 展示的效果，鉴于其中细节过多篇幅有限，本文侧重于原理上的实现方法描述。

## 跑道的透视与点击效果

![](/i/2015-12-06-1.png)

使用一个 LinearLayout ，将它的背景设置为游戏中四条跑道的大背景图片，然后在这个 LinearLayout 中加入四个 Button 作为四条纵向的跑道，这四个 Button 根据逻辑需要设置不同的 SelectorDrawable 来反应实现不同的点击效果。比如跑道中单词的对错分别需要用绿色渐变或红色渐变来表示，那么久根据那个单词的对错给它设置响应的 Backgroud，大致代码如下：

```java

for (int i = 0; i < RUN_WAY_COUNTS; i++) { // RUN_WAY_COUNTS为4
    float marginLeft; // 四条跑道左偏移的值
    if (i == 0) {
        marginLeft = (34f / 1136f) * (float) llRunWayFullWidth;
    } else {
        marginLeft = (7f / 1136f) * (float) llRunWayFullWidth;
    }
    options[i] = new Button(this);

    options[i].setBackgroundResource(R.drawable.gameff_wrong_selector);
    //或者 options[i].setBackgroundResource(R.drawable.gameff_right_selector);

    lp = new LinearLayout.LayoutParams(runWayWidth, ViewGroup.LayoutParams.MATCH_PARENT);
    lp.leftMargin = (int) marginLeft;
    llRunwayFull.addView(options[i], lp);
}
```

其中 selector 的 xml 定义大致如下：正常状态下没有背景，点击时有一个交互效果

```xml
<?xml version="1.0" encoding="utf-8"?>
<selector xmlns:android="http://schemas.android.com/apk/res/android">
  <item android:drawable="@drawable/gameff_runway_right" android:state_pressed="true"/>
</selector>
```

这样二维状态下跑道的效果与交互就完成了，为了使跑道显示出透视效果我们设置 llRunwayFull 这个 LinearLayout 的 rotationX 属性，让它绕 X 轴旋转并同事拉长 llRunwayFull 的高度即可。不同 dpi 屏幕下绕 X 轴旋转的效果差别很大，因此我们需要对不同 dpi 屏幕设置不同 CameraDistance 值来适配效果。

注：使用 graghics 包中的 Camera 对象也能实现 View 的 3D 旋转，但是相比调用 View 的 rotation 属相会更加麻烦。

跑道透视的设置如下：

```java
//设置跑道的旋转透视
llRunwayFull.setPivotX(llRunWayFullWidth / 2);
llRunwayFull.setPivotY(llRunWayFullHeight);
llRunwayFull.setX(-widthIncrease);
llRunwayFull.setY(llRunwayFull.getHeight() - heightScale * displayMetrics.heightPixels);

//dxDegres的值大概为33.5f
llRunwayFull.setRotationX(dxDegree);

// 适配不同 dpi 屏幕的透视效果
if (displayMetrics.density == 3.0f) {
    llRunwayFull.setCameraDistance(5851);
} else if (displayMetrics.density == 2.0f) {
    llRunwayFull.setCameraDistance(2600);
} else if (displayMetrics.density == 4.0f) {
    llRunwayFull.setCameraDistance(11090);
} else if (displayMetrics.density == 1.5f) {
    llRunwayFull.setCameraDistance(1286);
}
```

## 四条跑道中的动画控制

界面的根布局使用一个 FrameLayout，让每一个元素都能到达界面让的任意位置，同时又不至于因为动画的频繁更新带来性能的过度损耗

### 确定跑道中动画元素的起始状态

首先有 3 中动画元素需要考虑：单词（TextView）、炸弹、礼包。炸弹与礼包都属于是一张图片元素，他们的其实状态是相同的。

#### 单词的其实状态：

在单词的这个动画过程需要改变的属性分别是：

- 单词上边距
- 单词左边距
- 单词的宽度大小
- 单词的高度大小
- 单词的字号大小

图片元素，也就是炸弹与礼包动画中需要改变的属性分别是：

- 单词上边距
- 单词左边距
- 单词的宽度大小
- 单词的高度大小

根据设计图的效果，可以在游戏初始化的过程中确定四条跑道中元素不同属性的初始值与终止值。这里需要注意兼容不同机型的适配代码，以在不同型号的手机上都能有不错的表现效果。

确定好动画过程中需要改变哪些属性值并得到这些属性的初始值与终止值那么就可以建立 ValueAnimator，在它的 UpdateListener 中得到 animatedFraction，然后根据

> property = startValue + ( endValue - startValue ) * animatedFraction;

更新元素的不同属性来实现动画效果；

### 为每一条跑道建立一个 ValueAnimator，并实现动画

四个跑道中的动画效果是相互独立的，并且四条跑道中均有可能出现任何元素的动画，所以我们为每一条跑道都维护一个 AnimPolicyInfo 对象来控制四个跑道上不同动画的效果：

```java
public static class AnimPolicyInfo {
    public static final int TYPE_WORD = 1;
    public static final int TYPE_GIFT = 2;
    public static final int TYPE_BOOM = 3;

    int type = 0;    //存储这条跑道将要出现元素的类型
    boolean isRight; //根据 isRight 的值来记录玩家的正确率
    String text;     //如果动画元素类型是单词，text 中存储用来现实的字符信息
}
```

创建对象：

```java
for (int i = 0; i < RUN_WAY_COUNTS; i++) {
    float animLeftPaddingStart = leftPaddingBaseStart + i * (67.5f / 1280f) * displayMetrics.widthPixels;
    float animLeftPaddingEnd = leftPaddingBaseEnd + i * (displayMetrics.widthPixels / 4.0f);

    animPolicyInfo.add(new AnimPolicyInfo());
    runwayAnims[i] = ValueAnimator.ofFloat(0, 1);
    runwayAnims[i].setDuration(ANIM_DURATION);
}
```

根据 AnimPolicyInfo 中存储信息，在动画的 UpdateListener 中将相应的属性值应用的元素上来实现动画效果

```java
@Override
public void onAnimationUpdate(ValueAnimator animation) {
    AnimPolicyInfo policyInfo = GameAty.this.animPolicyInfo.get(runwayIndex);
    float animatedFraction = animation.getAnimatedFraction();

    switch (policyInfo.type) {
        case AnimPolicyInfo.TYPE_BOOM:
            FrameLayout.LayoutParams lpb = (FrameLayout.LayoutParams) ivBoom.getLayoutParams();
            lpb.leftMargin = (int) (animLeftPaddingStart + animLeftPaddingLength * animatedFraction);
            lpb.topMargin = (int) (animTopPaddingGiftLength * animatedFraction);
            lpb.width = DPU.dp2px(GameAty.this, 29 + animatedFraction * 124);
            lpb.height = DPU.dp2px(GameAty.this, 8 + animatedFraction * 77);
            ivBoom.setLayoutParams(lpb);
            break;

        case AnimPolicyInfo.TYPE_GIFT:
            FrameLayout.LayoutParams lp = (FrameLayout.LayoutParams) ivGift.getLayoutParams();
            lp.leftMargin = (int) (animLeftPaddingStart + animLeftPaddingLength * animatedFraction);
            lp.topMargin = (int) (animTopPaddingGiftLength * animatedFraction);
            lp.width = DPU.dp2px(GameAty.this, 29 + animatedFraction * 124);
            lp.height = DPU.dp2px(GameAty.this, 8 + animatedFraction * 77);
            ivGift.setLayoutParams(lp);
            break;

        case AnimPolicyInfo.TYPE_WORD:
            tvOptions[runwayIndex].setText(policyInfo.text);
            FrameLayout.LayoutParams lpw = (FrameLayout.LayoutParams) tvOptions[runwayIndex].getLayoutParams();
            lpw.leftMargin = (int) (animLeftPaddingStart + animLeftPaddingLength * animatedFraction);
            lpw.topMargin = (int) (animTopPaddingLength * animatedFraction);
            lpw.width = DPU.dp2px(GameAty.this, 29 + animatedFraction * 124);
            lpw.height = DPU.dp2px(GameAty.this, 8 + animatedFraction * 34);
            tvOptions[runwayIndex].setLayoutParams(lpw);
            tvOptions[runwayIndex].setTextSize(TypedValue.COMPLEX_UNIT_SP, 7 + 30 * animatedFraction);
            break;
    }
}
```
### 实现不同跑道中元素随机出发

实际上如果只是实现四个跑道中元素的滑行效果，那么只需建立一个 ValueAnimator，并在它的 UpdateListener 中一次更新四个跑道中不同元素的属性即可。但是我们要实现不同跑道中元素的出发时间不同，也就是看到的四个元素滑动的水平位置不一样。那么就需要适当的延时 anim `start` 方法的的触发时间。这样就实现了不同跑道元素下落的位置不一的效果：

```java
for (int i = 0; i < RUN_WAY_COUNTS; i++) {
  runwayAnims[i].setStartDelay(random.nextInt(ANIM_D));
  runwayAnims[i].start();
}
```

## 礼包效果

当玩家连续答对一定数目的单词的时候回派送一个礼包，领取时需要用点击礼包，然后将礼包放置在左侧空间。

礼包的动画大致分为两个阶段，第一阶段与通用逻辑类似，让礼包滑动即可，当用户点击礼包的时候触发第二阶段，改变红包的滑动路线，让礼包移动到左侧存放区。当礼包数量超过 9 过以至于没有空间的时候，那么动画完成时将礼包数量信息展示在9个礼包的下方。

首先第一阶段我们可以通过之前的 AnimPolicyInfo 信息来控制，同时为礼包的 View 添加点击事件，触发第二阶段动画。

第二阶段动画同样需要确定改变礼包 view 的哪些属性与相应属性的起始值与终止值。

- 单词上边距
- 单词左边距
- 单词的宽度大小
- 单词的高度大小

我们可以看到动画过程实际是上述四个属性的变化过程，他们的起始值就是礼包点击事件触发时的状态，而终止值就是礼包运动结束状态的属性。起始状态的值是很容易得到的，为了更方便的处理终止状态的值，这里我们不妨先把所有的能够得到的礼包先添加的到视图中，

![](/i/2015-12-06-4.png)

然后将左侧所有的礼包的 view 设置为 invisible，然后根据当前礼包的个数 get 到动画终止时礼包所应该的属性值，在动画结束时设置相应的 view 为 visible 。

```java
private View.OnClickListener giftClickListener
        = new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        ivGift.setClickable(false);

        //停止第一阶段动画
        for (int i = 0; i < RUN_WAY_COUNTS; i++) {
            if (animPolicyInfo.get(i).type == AnimPolicyInfo.TYPE_GIFT) {
                runwayAnims[i].cancel();
            }
        }

        //确定第二阶段动画的初始值与终止值
        FrameLayout.LayoutParams lp = (FrameLayout.LayoutParams) ivGift.getLayoutParams();
        final int leftMarginStart = lp.leftMargin;
        final int topMarginStart = lp.topMargin;
        final int widthStart = lp.width;
        final int heightStart = lp.height;

        final int leftMarginLength;
        final int topMarginLength;
        final int widthLength;
        final int heightLength;
        if (giftCount > 8) {
            FrameLayout.LayoutParams l = (FrameLayout.LayoutParams) tvGiftCounts.getLayoutParams();
            leftMarginLength = l.leftMargin - leftMarginStart;
            topMarginLength = l.topMargin - topMarginStart;
            widthLength = - widthStart;
            heightLength = - heightStart;

        } else {
            FrameLayout.LayoutParams l = (FrameLayout.LayoutParams) ivGifts[giftCount].getLayoutParams();
            leftMarginLength = l.leftMargin - leftMarginStart;
            topMarginLength= l.topMargin - topMarginStart;
            widthLength = l.width - widthStart;
            heightLength = l.height - heightStart;
        }

        giftCount++;

        ValueAnimator gAnim = ValueAnimator.ofFloat(0, 1);
        ToastU.showToastShort(GameAty.this, "Get Gift");
        gAnim.addUpdateListener(new ValueAnimator.AnimatorUpdateListener() {
            @Override
            public void onAnimationUpdate(ValueAnimator animation) {

                //更新元素属性值
                float animatedFraction = animation.getAnimatedFraction();
                FrameLayout.LayoutParams lp = (FrameLayout.LayoutParams) ivGift.getLayoutParams();
                lp.leftMargin = (int) (leftMarginStart + leftMarginLength *animatedFraction);
                lp.topMargin = (int) (topMarginStart + topMarginLength * animatedFraction);
                lp.width = (int) (widthStart + widthLength *animatedFraction);
                lp.height = (int) (heightStart + heightLength * animatedFraction);
                ivGift.setLayoutParams(lp);
            }
        });
        gAnim.addListener(new Animator.AnimatorListener() {
            @Override
            public void onAnimationStart(Animator animation) {}

            @Override
            public void onAnimationEnd(Animator animation) {

                //动画结束时，现实礼包的数量信息
                if (giftCount > 9) {
                    tvGiftCounts.setText("+"+(giftCount-9));
                    tvGiftCounts.setVisibility(View.VISIBLE);
                } else {
                    ivGifts[giftCount-1].setVisibility(View.VISIBLE);
                }
                ivGift.setClickable(true);
                stopAnims();
                performScoreRecordContinue(false, false);
            }

            @Override
            public void onAnimationCancel(Animator animation) {}
            @Override
            public void onAnimationRepeat(Animator animation) {}
        });
        gAnim.setDuration(500);
        gAnim.start();
    }
};
```
至此，这个节奏大师游戏中的难点就基本解决完了，当然如果你要动手实现起来，还会遇到更多问题，一个一个解决最终成功。「火星救援」中 Mark 说：当你解决的问题足够多的时候，你就成功的回到地球了
