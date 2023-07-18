- tags: [tech](/tags.md#tech)
- date: 2014-08-31

# Virtualbox 中清理磁盘空间

以 windows guest 为例：

一：下载 [sdelete](http://technet.microsoft.com/en-us/sysinternals/bb897443.aspx) 并将它添加进系统 PATH， 可以直接放到 C:\windows\system32 文件夹下

二：整理 guest 中的 free 空间并写入 0

```bash
sdelete -c
sdelete -z

```

三：对 host 中的 vdi 磁盘镜像处理，尝试 guest 休眠状态

```bash
vboxmanage modifyhd winxp.vdi compact

```