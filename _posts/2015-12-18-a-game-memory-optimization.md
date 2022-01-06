---
title: 内存优化，从 O(N) 到 O(1)
category: android
---

「单词消消乐」是我们推出单词功能时做的一个小游戏。从产品的角度来看，游戏能够快速的拉动用户增长，尤其是这种将玩游戏、背单词、查看错词功能网状打通，寓教于学的模式是非常受欢迎的。引入轻社交（排行榜）配合运营部门的活动推广更是能够快速推动产品发展。
<!--more-->

![](/i/2015-12-18-1.png)

在做单词模块的时候我负责的是单词学习的主要逻辑与实现（有关背单词的实现下节再讲），单词消消乐是由另外一个同事完成的。在单词消消乐上线一段时间后我们发现一个神奇的 Bug：每当用户玩到六七百分的时候游戏就会离奇闪退，很不友好，对用户产生了非常严重的不良体验。后来，我着手优化这一块的程序逻辑。这篇文章就讲讲两点，一个是在不断增长模型下内存使用的优化，另一个是要对 Android SDK 的使用非常了解，多看文档与源码才行。

首先，追踪到产生这个神奇 Bug 的原因是 OOM，一种恍然大悟的感觉，那么下一步就是分析原来程序中有那些比较耗费内存的逻辑。游戏中重复进行的逻辑有两个：

- 选择单词的正确翻译，根据选择的正确与否进入下一回合
- 根据用户选择翻译的正确与否播放音频反馈

很不幸，我发现这两个重复逻辑中每一次操作都增加了内存开销，并且不能尽快合理的得到释放。这样程序运行起来到一定回合次数后必然会导致 OOM 的发生。

既然已经找到了错误的原因所在，那么就要有针对行的解决它们。首先对于第一个问题，我们先看原来程序中的逻辑：

*每一个选项使用一个 Button 控件，3 个 Button 候选项放在一个横向布局的 LinearLayout 中，然后每个回合都会为一个 LinearLayout 和 3 个 Button 分配内存。当游戏进行一定回合以后，即使频繁的引发系统 GC 也不能满足 app 对新内存的需求，进而产生 OOM*

我们看到这里内存的使用随着回合数的增加是呈线性不断增加的，这也就意味着游戏回合增长的上限。但是同样我们可以看到即使摆放满屏的 Button 像下图这样也不会产品太多内存消耗，因此可以先对极端情况的内存开销做分配申请，然后对这些 Button 进行复用来控制内存的增长。

![](/i/2015-12-18-2.png)

为了适配不同手机屏幕情景，Button 的高度宽度都要使用 Java 代码动态的计算然后添加到 DecorView，并不能通过 XML 配置。我们定义两个数组变量来存放可能用到的数量最多情况下的控件：

```java
LinearLayout[] optionLinearLayout;
Button[][] optionButtons;
```

然后在程序初始化的时候为它们分配空间：

```java
private void allocOptionViewsSpace() {
    optionLinearLayout = new LinearLayout[totalLine];
    optionButtons = new Button[totalLine][3];

    for (int i = 0; i < totalLine; i++) {
        optionLinearLayout[i] = new LinearLayout(this);
        for (int j = 0; j < 3; j++) {
            optionButtons[i][j] = new Button(this);
        }
    }
}
```

之前对消失行的 removeView 操作现在都转换成相关 view 的 visiablity 属性的改变，为了应对游戏过程中复杂的需求，对 Button 相关样式的控制全部由 java 代码动态生成。

**至此，在框架层面为 View 分配内存的操作只有在游戏初始化的过程中进行，而且大小是固定的。View 对内存的消耗并不会随着回合数的增加而增加。**

另一方面，对用户的选择选项，app 会有一个声音反馈，在这里我们使用的是 SoundPool 来播放音频。原来的代码中每次播放都进行了 load 操作，然后在 SoundPool.OnLoadCompleteListener 中播放音频。

这样做是非常不合理的，Android [官方文档](http://developer.android.com/reference/android/media/SoundPool.html#setOnLoadCompleteListener(android.media.SoundPool.OnLoadCompleteListener)) 中对 SoundPool 的描述如：

> A SoundPool is a collection of samples that can be loaded into memory from a resource inside the APK or from a file in the file system. The SoundPool library uses the MediaPlayer service to decode the audio into a raw 16-bit PCM mono or stereo stream. This allows applications to ship with compressed streams without having to suffer the CPU load and latency of decompressing during playback.

也就是说 SoundPool 会把音频文件直接 load 到内存中，并且返回一个 id，load 过程是异步进行的，而返回 id 是一个同步过程。也就是说我们可以即时拿到已经加载音频的 id，并在 SoundPool.OnLoadCompleteListener 中知道音频已经加载完毕，然后可以通过先前拿到的 id **重复**的播放这个声音，而不是每次播放必须加载，引起内存暴增。

这显然是一个因为对 SoundPool 不了解造成的严重问题，由此看来我们在写代码前需要对使用的 SDK 有相当的了解才行，往往 SDK 提供的官方文档是最靠谱的参考资料。一些相对隐蔽的信息我们需要探寻到 SDK 源码内部来了解它们到底是怎样工作的。

有关单词消消乐的优化工作并没不是显得非常高深，之所以记录下来，是要时刻提醒自己写代码一定要有内存意识，每一步都要考虑是否会造成更多的内存开销，在一些必须分配内存的情景下也一定注意不要重复开销内存。另外对已经申请到得内存要有及时释放的意识，避免过多占用。而这些都是需要长时间去学习去积累才能做的更好的。从程序逻辑原理上要避免内存泄露的出现，可以借助 LeakCanary 这样的工具做泄露检测。
