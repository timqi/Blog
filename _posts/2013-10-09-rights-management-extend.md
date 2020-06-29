---
title: Linux权限管理--扩展
category: linux
---

> [Linux权限管理--用户,组](/2013/10/09/rights-management-user/)<br/>
> [Linux权限管理--文件](/2013/10/09/rights-management-file/)

本文介绍linux权限管理部分的扩展内容
<!--more-->

## 默认权限

每个终端都有一个`umask`权限来确定新建文件和新建文件夹的的默认权限,umask使用数字权限来表示,比如022.

- 目录的默认权限是`777-umask`,文件的默认权限是`666-umask`.
- 普通用户的umask是`0002`,root用户的umask是`022`.

**默认权限减去umask的值就是所创建的文件或文件夹的权限**.那么新建文件的权限则为`666-0002=664 => rw-rw-r--`.下图为创建test文件与test1目录的:

![新文件与目录创建的默认权限](/i//2013-10-09-4.png) <center>*新文件与目录创建的默认权限*</center>

使用`umask`来设置终端的umask值:

![umask设置默认权限](/i//2013-10-09-5.png) <center>*umask设置默认权限*</center>

## 特殊权限

除了普通权限外还有三种特殊的权限:

![特殊权限](/i//2013-10-09-8.png)

设置特殊的权限:

- 设置`suid`: chmod u+s filename
- 设置`sgid`: chmod g+s filename
- 设置`sticky`: chmod o+s filename

**和普通权限一样特殊权限也可以使用数字来表示:**

- `suid = 4`
- `sgid = 2`
- `sticky = 1`
