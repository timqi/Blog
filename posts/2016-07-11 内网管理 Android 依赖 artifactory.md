- tags: [android](/tags.md#android)
- date: 2016-07-11

# 内网管理 Android 依赖 artifactory

使用过 Android Studio 的同学都知道，gradle 会自动从远程服务上下载你配置的依赖，比如

```groovy
compile 'com.squareup.okhttp3:okhttp:3.4.0'

```

简单的一句就可也在项目中使用 okhttp3.4.0 了。那么这个依赖库是从哪里的服务器上下载的呢？一般在项目的根目录下会有一个 build.gradle 文件，里面有类似的

```groovy
repositories {
  jcenter()
  // 或者 mavenCenter()
}

```

jcenter 函数是 Android Studio 内建的以 jcenter 为远程获取源的配置，jcenter 是 bintray 二进制托管分发服务平台，兼容老牌的 maven 协议，而 bintray 是 jFrog 公司的一款产品；mavenCenter 是一个老牌的 maven 中央仓库，一般 java 编写的 jar 打包文件都会从这个平台分发，尤其是 javaweb 的一些类库。

两者实际上都是遵循 maven 分发协议的公共存储仓库。那么已经有了 jcenter 和 mavenCenter 这么优秀的平台为什么还要自己搭建呢，目前我的原因是这两点：

1. 共享公司内部开发的模块，方便内部依赖在内网分发，同时避免内部代码传到外网
2. 由于众所周知的原因，下载国外服务器上的依赖很慢，通过内网将相关文件缓存一方面加快了依赖安装的速度也减轻了出口带宽压力

我选择使用 artifactory 搭建 maven 仓库。至于我为什么选择了 artifacory，是因为 artifactory 对 gradle，android 支持的更顺畅，界面也更好看更现代化一点。当然你也可以选择老牌的 nexus。

下载 artifactory 安装包：[https://www.jfrog.com/open-source/](https://www.jfrog.com/open-source/)

我选择了 rpm 包的安装方式，下载 rpm 包后执行：

```bash
rpm -ivh jfrog-artifactory-oss-4.9.0.rpm

```

artifactory 默认安装在 /opt/jfrog 目录下，进入 `/opt/jfrog/artifactory/bin` 执行

```bash
artifactoryctl start

```

即可启动 artifactory 服务，然后可以在 http://host:8081/artifactory 目录下访问 artifactory 服务了，默认的账号密码是 admin,password；可以修改 tomcat/server.xml 文件来改变服务的端口号。

至此，服务就安装完毕了。artifactory 提供了 Local，Remote，Virtual 三种类型的仓库，其中 Remote 可以代理其他的远程仓库，比如我简历的两个仓库分别代理 jcenter，mavenCenter。然后 Local 型的仓库用来存储公司内部开发的依赖；最后新建一个 Virtual 类型的虚拟仓库把 Remote 类型的 jecenter 代理仓库 mavenCenter 代理仓库和新建的 Local 型本地仓库都添加进去。然后我们就可以使用这个虚拟仓库来组织所有依赖了

![2016 07 11 内网管理 Android 依赖 artifactory [android] f88258dfe06a4cf9a48718aefc9d6eea/2016-07-11-1.png](/images/2016-07-11-1.png)

如图点击复制仓库地址，然后再 gradle 种配置

```groovy
repositories {
  maven { url "urlOfYourRepo" }
}

```

运行一下 gradle 同步就可以正常使用了

## Android 开发环境上传 library 到 artifactory

artifactory 有相应的 gradle 插件，我们可以借助插件方便的上传 library 到 artifactory 共享。

1. 在根目录的 build.gradle 种添加插件依赖

```groovy
buildscript {
  dependencies {
    classpath "org.jfrog.buildinfo:build-info-extractor-gradle:3.1.1"
  }
}

```

1. 在 library 的 build.gradle 文件处理上传 task，在 build.gradle 末尾添加

```groovy
apply from: 'https://raw.githubusercontent.com/timqi/AssertServer/master/android/maven_push.gradle'

```

1. 下载 [maven_push.properties](https://raw.githubusercontent.com/timqi/AssertServer/master/android/maven_push.properties) 到 library 根目录，并填写相关信息
2. 最后执行如下命令完成上传

```bash
./gradlew artifactoryPublish

```