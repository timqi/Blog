- tags: [tech](/tags.md#tech)
- date: 2015-07-01

# Gollum 基于 Git 的知识管理系统

[gollum](https://github.com/gollum/gollum) 是一款轻量级基于 `Git` 的知识管理系统，Github 中的项目 Wiki 也使用 gollum 托管。

Gollum 能够把 git 中已经 commit 的内容托管到 Web 页面上，同时提供了一个简易的 Web 编辑界面。相比于传统的笔记管理方案，Gollum 在与分享、多人协作方面更有优势，同时记录的内容文档支持 Markdown 语法使得笔记能够更加通用。

类似于 [jekyll](https://github.com/jekyll/jekyll)， gollum 的源码就是一个真正的 `Git Repository`，可以使用 git 中常用命令如 add, commit 来管理这个 Git 仓库，Gollum 将其自动托管到 Web 页面，由于文档全部存储在同一git仓库中，所以可以轻松的实现版本回退与整个知识内容的迁移。

Gollum 由 Ruby 语言开发，搭建好 **RubyGems** 环境后可以安装 Gollum：

```bash
gem install gollum -V

```

进入要托管的 git 仓库目录下执行 gollum 命令即可将内容部署到 **http://0.0.0.0:4567** 地址

使用 `gollum -h` 命令产看相关部署参数。生产环境中需要将 gollum 部署为 apache 或 nginx 等 Web Server 的 Ruby 应用。