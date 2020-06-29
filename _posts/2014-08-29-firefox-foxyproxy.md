---
title: FF 中使用 foxyproxy 与 GoAgent
category: tech
---

1. 导入证书：选项 -> 高级 -> 加密 -> 查看证书 -> 导入 -> "goagent/local/CA.crt"
<!--more-->
2. foxyproxy -> 代理服务器 -> 新建服务器 -> 代理服务器细节
3. 主机选项：127.0.0.1 端口：8087 （不要勾选 socks 代理）
4. URL 模式：勾选--不要内部网络 IP 地址使用这个代理
5. 点击确定
6. 模式订阅：点击 Go
7. 在窗口中填写 `订阅名称`、`订阅描述` 和 `订阅网址`。代理服务起选择刚才设置的 goagent 代理服务器。订阅网址： <br/>

``` python
https://autoproxy-gfwlist.googlecode.com/svn/trunk/gfwlist.txt
```

8. Format：AutoProxy 和 Obfuscate：Base64
9. 点击确定
10. 快速添加：启用、选择设置好的 goagent 代理
11. 选择工作模式：使用基于其预定义模版的代理服务器
12. 关闭
13. 重启 FireFox
