---
title: 在 Qt 中使用 opencv
category: tech
---

本文讲述 Windows 环境下使用 Qt Creator 搭建 Qt 库与 opencv 库联合开发环境的过程
<!--more-->

## 一： 使用 qt 中 mingw 来编译 opencv 源码

### 1. 下载 cmake， 并添加进环境变量

打开 cmd 运行窗口输入

``` bash
set PATH=%PATH%;C:\apps\cmake-3.0.0-win32-x86\bin
```

如图：

![](/i//2014-08-18-1.png)

保证环境变量中包含 cmake 和 mingw

### 2. 使用 cmake 生成 Makefile 文件

``` bash
cmake -G "MinGW Makefiles" c:\apps\opencv\sources
```

指定 "MinGW Makefiles" 为编译器
![](/i//2014-08-18-2.png)

### 3. 使用 ming32-make 编译：

``` bash
mingw32-make
```

![](/i//2014-08-18-3.png)

### 4. 构建 opencv 链接库：

``` bash
mingw32-make install
```

![](/i//2014-08-18-4.png)

当前工作目录下的 install 文件夹即为所需要的头文件与函数库

## 二： 在 Qt Creator 中使用 Qt 图形库结合 opencv 操作 webcam

建立一个 Qwidget 工程， 在界面上放置一个 label 用来显示如片，两个 button 控摄像机的开关， 如下图所示：

![](/i//2014-08-18-5.png)

编辑头文件如下：

``` c++
fndef FRAME_H
#define FRAME_H

#include <QWidget>
#include <QTimer>
#include <QPainter>
#include <QImage>
#include <opencv2/opencv.hpp>

using namespace cv;
#define FPS 30

namespace Ui {
class Frame;
}

class Frame : public QWidget
{
    Q_OBJECT

public:
    explicit Frame(QWidget *parent = 0);
    ~Frame();

private:
    Ui::Frame *ui;
    VideoCapture cap;
    QTimer timer;
    Mat img;

private slots:
    void openCamera();
    void closeCamera();
    void readFrame();
};

#endif // FRAME_H
```

源文件：

``` c++
#include "frame.h"
#include "ui_frame.h"
#include "opencv2/opencv.hpp"

Frame::Frame(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::Frame)
{
    ui->setupUi(this);

    connect(&timer, SIGNAL(timeout()), this, SLOT(readFrame()));
    connect(ui->close, SIGNAL(clicked()), this, SLOT(closeCamera()));
    connect(ui->open, SIGNAL(clicked()), this, SLOT(openCamera()));

}

Frame::~Frame()
{
    delete ui;
}

void Frame::openCamera()
{
    cap.open(0);
    timer.start(FPS);
}

void Frame::closeCamera()
{
    timer.stop();
    cap.release();
}

void Frame::readFrame()
{
    cap >> img;
    cvtColor(img, img, CV_BGR2RGB);
    QImage im((unsigned char *)img.data, img.cols, img.rows, QImage::Format_RGB888);
    ui->pic->setPixmap(QPixmap::fromImage(im));
}
```

源码完成后在工程文件中加入相应的头文件与库进行编译：

``` c++
INCLUDEPATH += C:\apps\opencv2.4.9\include\

LIBS += -L"C:\apps\opencv2.4.9\x64\mingw\lib"
LIBS += -lopencv_core249.dll
LIBS += -lopencv_highgui249.dll
LIBS += -lopencv_imgproc249.dll
LIBS += -lopencv_legacy249.dll
LIBS += -lopencv_ml249.dll
LIBS += -lopencv_video249.dll
```

编译运行即可，结果如下：


![](/i//2014-08-18-6.png)

![](/i//2014-08-18-7.png)

**注意：**<br/>
1. 运行程序时需要将 C:\apps\opencv2.4.9\x64\mingw\bin 目录添加进系统 PATH 以保证库的完整<br/>
2. 文中用到的 Qt、cmake 和 已经编译好的 opencv 库下载地址：[附件](http://pan.baidu.com/s/1kTqmERP)
