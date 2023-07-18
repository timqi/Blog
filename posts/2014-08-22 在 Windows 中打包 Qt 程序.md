- tags: [tech](/tags.md#tech)
- date: 2014-08-22

# 在 Windows 中打包 Qt 程序

本文中以 [hand-gesture-detection](https://github.com/qiqihyper/hand-gesture-detection) 为例打包出 Windows 平台下使用 Qt 与 Opencv 库的可执行程序

## 一 在 Qt Creator 中使用 Release 版本编译源码生成可执行文件

## 二 找出所需要的运行库

在程序可以在本地正常运行的情况下使用 [DenpendencyWalker](http://www.dependencywalker.com/) 选择 file -> opencv 选择需要打包的可执行文件即可看到这个文件运行所需要的库,如下图所示：

![2014 08 22 在 Windows 中打包 Qt 程序 [tech] a3efcfeb9ddd4172a3e3dabcc9e8c4ad/2014-08-22-1.png](/images/2014-08-22-1.png)

根据测试结果将所需要的运行库与可执行文件放在同一目录下：

![2014 08 22 在 Windows 中打包 Qt 程序 [tech] a3efcfeb9ddd4172a3e3dabcc9e8c4ad/2014-08-22-2.png](/images/2014-08-22-2.png)

## 三 runtime 错误

只打包 DenpendencyWalker 中的库会产生运行时错误，如下图：

![2014 08 22 在 Windows 中打包 Qt 程序 [tech] a3efcfeb9ddd4172a3e3dabcc9e8c4ad/2014-08-22-3.png](/images/2014-08-22-3.png)

解决办法是同时打包 Qt 插件中 platforms 运行库如下，如果程序中用到 Qt 的其他插件则需要在下面的目录中复制并打包进发布程序中

![2014 08 22 在 Windows 中打包 Qt 程序 [tech] a3efcfeb9ddd4172a3e3dabcc9e8c4ad/2014-08-22-4.png](/images/2014-08-22-4.png)

最终打包结果如下，这时程序就可以在别人电脑上运行了：

![2014 08 22 在 Windows 中打包 Qt 程序 [tech] a3efcfeb9ddd4172a3e3dabcc9e8c4ad/2014-08-22-5.png](/images/2014-08-22-5.png)