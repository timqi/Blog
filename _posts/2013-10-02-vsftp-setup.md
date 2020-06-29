---
title: FTP 服务器 vsftpd 安装架设
category: linux
---

本文介绍CentOS环境下利用vsftpd搭建ftp服务器的方法及其相关配置方案
<!--more-->

## 安装vsftpd

```bash
# yum install vsftpd
```

## 启动、重启、关闭vsftpd服务器

```bash
# /sbin/service/vsftpd restart
Shutting down vsftd:  [OK]
Starting vsftpd for vsftp:  [OK]
```

OK表示重启成功。启动和关闭ftp服务分别把`restart`改成`start/stop`即可。
如果是源码安装的，到安装文件夹下找到start.sh和shutdown.sh文件执行即可。

## 与vsftpd服务器有关的文件和文件夹

- vsftpd服务器的配置文件是：`/etc/vsftpd/vsftpd.conf`
- vsftpd的根目录，即ftp服务器的主目录：`/var/ftp/pub`。如果你要修改服务器目录的路径主修修改/var/ftp到别处即可。

## 添加ftp本地用户

有的`ftp服务器`需要用户名和密码才能登录是因为设置了ftp用户和权限。为了安全，`ftp用户`一般不能登录系统，只能进入ftp服务器自己的目录中。这样的用户叫做虚拟用户，并不是真正的虚拟用户，不能登录SHELL，没能力登录系统。

```bash
# /usr/sbin/adduser -d /opt/test_ftp -g ftp -s /sbin/nologin test:
```

使用命令`adduser`添加`test`用户，`-s /sbin/nologin`表示不能登录系统，`-d /opt/test_ftp`表示自己的文件夹在相应目录下，`-g ftp`指明该用户属于ftp组。

`passwd test`：为用户设置密码。

这样就添加了一个ftp用户。下面的例子帮助你进入FTP服务器：

![ftp登录](/i/2013-10-02-1.png) <center>*ftp登录*</center>

在Windows系统下使用系统 `资源管理器 `在地址栏中输入ftp://192.168.254.130 等待连接然后键入用户名与密码即可。如若保证你可以读写目录则vsftpd.conf中要做以下相应配置：

```bash
local_enable=yes
write_enable=yes
local_umask=022
```

## 匿名上传下载

修改配置文件vsftpd.conf确定有一下几行，如果明有自己加上就行。

```bash
anonymous_enable=yes
anon_upload_enable=yes
anon_mkdir_write_enable=yes
anon_umask=022
```

然后你可以新建一个文件夹设置它的权限为完全开放，任何用户可以访问修改。

```bash
# mkdir var/ftp/guest
# chmod 777 /var/ftp/guest
```

## 定制进入FTP服务器的欢迎信息

在vsftpd.conf中设置：

```bash
dirmessage_enable=yes
```

然后进入用户目录建立一个.message文件,输入欢迎信息即可(我这里写入的是Welcome to QiQi's FTP!)

![欢迎信息](/i/2013-10-02-2.png) <center>*FTP欢迎信息*</center>

将某个路径挂载到ftp服务器下供ftp用户使用叫做虚拟路径。比如将qiqi的用户目录挂载到ftp服务器中供ftp用户使用命令如下：

```bash
# mount --bind /home/gxl /var/ftp/pub #使用挂载命令
# ls /var/ftp/pub
```

![虚拟路径挂载](/i/2013-10-02-3.png) <center>*虚拟路径挂载*</center>

## vsftp的日志功能

添加下面一行到vsftpd.conf配置文件中，一般情况下该文件中有这一行，只要把这行前面的#号去掉注释即可。如果没有这一行的画自行添加上就行：

```bash
xferlog_file=/var/log/vsftpd.log
```

## 限制连接数，以及每个IP的最大连接数

修改配置文件，例如最大支持连接数100个，每个IP能支持5个连接：

```bash
max_client=100
max_per=5
```

## 限制传输速度

修改配置文件，例如让匿名用户和vsftpd上的用户(即虚拟用户)都以80KB=1024*80=81920的速度下载：

```bash
anon_max_rate=81920
local_max_rate=81920
```

## 将用户(一般指虚拟用户)限制在自己家的目录

修改配置文件：

```bash
chroot_local_user=yes
```

如果只想某些用户仅能访问自己的目录而其他用户不做限制，那么就需要在`chroot_list`文件(此文件一般在/etc/vsftpd下)中添加此用户，如果没有这个文件则需要用户自建

编辑此文件，比如将test用户添加到此文件中，那么将其写入即可，一般的话，**一个用户占一行**。

```bash
$ cat chroot_list
test
```

## 绑定某个IP到vsftpd服务器

有时候需要限制某些IP访问服务器，只允许某些IP访问，例如只允许192.168.0.33访问这个FTP，同样修改配置文件：

```bash
listen_address=192.168.0.33
```

配置vsftpd.conf文件：


## 配置vsftpd.conf：

```bash
anonymous_enable=NO            #禁止匿名
local_enable=YES                       #允许本地登录
write_enable=YES                       #允许写，如需上传，则必须
local_umask=027                        #将上传文件的权限设置为：777 local_umask
anon_upload_enable=YES          #允许虚拟用户和匿名用户上传
anon_other_write_enable=YES #允许虚拟用户和匿名用户修改文件名和删除文件
dirmessage_enable=YES
xferlog_enable=YES                      #打开日志记录
connect_from_port_20=YES
xferlog_file=/var/log/vsftpd.log     #日志存放位置
xferlog_std_format=YES              #标准日志格式
idle_session_timeout=600        #空闲连接超时
data_connection_timeout=120
ftpd_banner=Welcome to ChinaRise FTP service       #欢迎信息
guest_enable=yes                       #允许虚拟用户
guest_username=vsftpdguest #虚拟用户使用的系统账号
virtual_use_local_privs=YES     #虚拟用户拥有本地系统权限

#以上两行将虚拟用户限制在其目录下，不能访问其他目录，或者直接用chroot_local_user=YES
chroot_local_user=NO
chroot_list_enable=YES

listen=yes           #监听/被动模式
listen_port=21        #监听端口

#虚拟用户名单保存在文件/etc/vsftpd/vsftpd.chroot_list 中
chroot_list_file=/etc/vsftpd/vsftpd.chroot_list
#每个虚拟用户名的更加详细的培植保存在/etc/vsftpd/vsftpd_user_conf 中
user_config_dir=/etc/vsftpd/vsftpd_user_conf
```

### 虚拟用户其他设置

在`/etc/vsftpd/vsftpd.chroot_list `文件中写入允许登陆的虚拟用户名称，每行一个在`/etc/vsftpd/vsftpd_user_conf` 文件夹中创建一个以虚拟用户用户名命名的文件，写入：`local_root = /var/FTP/`子目录名然后在`/var/FTP`下创建一个对应的目录即可
