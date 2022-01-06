---
title: 取消 AsyncTask 继续运行
category: android
---

当用户进入一个需要加载详情的页面时经常因为加载慢而退出页面，然后又点进来，这样重复多次后便会启动很多个 AsyncTask 导致错误，所以需要及时取消相应的 AsyncTask 任务。
<!--more-->

``` java
public class Task extends AsyncTask<Void, Void, Void>{

@Override
protected Void doInBackground(Void... path) {
// Task被取消了，马上退出循环
if(isCancelled()) return null;
}

@Override
public void onProgressUpdate(File... files) {
// Task被取消了，不再继续执行后面的代码

if(isCancelled()) return;
.........
}
}

UI线程:

// 保持对Task的引用

private PhotoTask task;

// 1,启动新的任务
task = new PhotoTask();
task.execute(path);

// 2, 取消任务

if (task != null && task.getStatus() == AsyncTask.Status.RUNNING) {
task.cancel(true); // 如果Task还在运行，则先取消它
}


}
}
```
