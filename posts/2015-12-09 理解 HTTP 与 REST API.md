- tags: [tech](/tags.md#tech)
- date: 2015-12-09

# 理解 HTTP 与 REST API

## HTTP

HTTP 协议是当前互联网应用层使用最广泛的协议之一，经历了 HTTP 0.9、HTTP 1.0 的发展目前使用最广的是 HTTP 1.1 版本，当然现在 HTPP 2.0 也正在不断普及。本文就 HTTP 1.1 展开讨论。

HTTP（超文本传输协议 英文：HyperText Transfer Protocol）最初的目的是为了提供一种发布和接收 HTML 页面的方法。作为协议，HTTP 仅仅是将通信过程规范化，使客户端与服务端能够更好的理解对方想要表达的内容。HTTP 本身并不提供任何功能，只有实现了 HTTP 协议的服务端软件（如 nginx、apache 等）和客户端软件（如各种浏览器软件）才能够借助 HTTP 的规范更好的相互通信，通常我们成这个客户端为用户代理程序（User Agent）。HTTP 的 RFC 文档中并没有规定它的下层需要依赖什么通信规范，所以它理论上可以建立在任何通信协议上，但是通常情况下为了提供更加可靠的互联网连接服务，HTTP 是基于 TCP 传输层实现的，默认的 TCP 端口为 80。

HTTP 协议分为请求与响应两个部分，请求是指客户端向服务器发送的消息，响应是指服务器收到消息后向客户端返回的消息。无论是请求的消息还是响应的消息都会分为两个部分，一部分是控制信息来商议传输的文件的压缩格式，文本类型，缓存策略等这些问题；另一部分则是消息本身的真正的实体内容。

### URI

要发起请求，我们首先要知道我们想要请求内容的网络地址在哪，HTTP 协议中请求的资源都是由统一资源标识符（Uniform Resource Identifiers，URI）来标识，我们来看一个通用的 URI 示例：

> http://user:pass@host.com:8080/p/a/t/h?query=string#hash
> 

[Untitled Database](2015%2012%2009%20%E7%90%86%E8%A7%A3%20HTTP%20%E4%B8%8E%20REST%20API%20%5Btech%5D%20b8222c72088f41bca76a23898b6502e6/Untitled%20Database%204a8b7e69c4cd4bb784ec6278dd50f136.csv)

上面解析了一个完整的 URI 地址，我们将特定的 URI 字符串输入到浏览器地址栏就能够发起对这个 URI 所示资源的访问请求。

### 请求头

有了 URI 我们就知道了我们所需资源的网络地址，但是在发起网络请求之前我们仍然还需要确定一些诸如文本压缩格式，文本类型，缓存策略等等的其他控制信息，这就是一个 HTTP 请求（Request）中添加的一些头部信息。通常的 HTTP 请求头有下面这些：

[Untitled Database](2015%2012%2009%20%E7%90%86%E8%A7%A3%20HTTP%20%E4%B8%8E%20REST%20API%20%5Btech%5D%20b8222c72088f41bca76a23898b6502e6/Untitled%20Database%20449065ce61374d078306f3a5859af2d1.csv)

根据这些头信息，我们可以控制客户端与服务器之间通信的一些细节问题，也能够利用这些信息做一些网络优化。比如在数据编码方式上使用 gzip 。 Servlet 能够向支持 gzip 的浏览器返回经 gzip 编码的 HTML 页面。许多情形下这可以减少 5 到 10 倍的下载时间；

Cookie 头常用来标识不同用户身份，使得无状态的 HTTP 连接能够更好的管理不同用户的状态过程。User-Agent 头标识了用户使用什么客户端来发起的网络请求，比如 firefox、safari、chrome 等浏览器以及 Android 手机，iOS 手机等都拥有不同的 User-Agent 字段，所以服务器端能够区分出用户是使用什么客户端发起的网络请求。

### 请求方法

确定了请求地址与请求过程中的一些控制信息后，HTTP 1.1 协议中还为我们提供了八种不同的请求方法来以不同方式操作指定的资源：

[Untitled Database](2015%2012%2009%20%E7%90%86%E8%A7%A3%20HTTP%20%E4%B8%8E%20REST%20API%20%5Btech%5D%20b8222c72088f41bca76a23898b6502e6/Untitled%20Database%20e0be2310746c4b8695839300b90c4729.csv)

HTTP 服务器至少应该实现 GET 和 HEAD 方法，其他方法都是可选的。

### 响应头

服务器收到了发来的 HTPP 请求后，经过运算处理需要向客户端返回消息，这其中也包含了控制部分也就是「响应头」和正文文本的实体内容，其中常见的响应头有：

[Untitled Database](2015%2012%2009%20%E7%90%86%E8%A7%A3%20HTTP%20%E4%B8%8E%20REST%20API%20%5Btech%5D%20b8222c72088f41bca76a23898b6502e6/Untitled%20Database%203fb894b3183b47c09374862b91408030.csv)

这些响应头中仅仅是返回了控制信息，并不能决定客户端下一步的行为。真正的 Cookie 与缓存的实现还是由客户端完成的，但是客户端在实现这个控制功能的时候需要参照响应头中的信息。

对于 Cookie 的处理，客户端会取出响应头中 Set-Cookie 的信息，并在下次请求中将这些信息条加到请求头的 Cookie 里面以完成身份认证。

Cache-Control 控制缓存方面，它的取值如下：

- Public：指示响应可被任何缓存区缓存。
- Private：指示对于单个用户的整个或部分响应消息，不能被共享缓存处理。这允许服务器仅仅描述当用户的部分响应消息，此响应消息对于其他用户的请求无效。
- no-cache：指示请求或响应消息不能缓存
- no-store：用于防止重要的信息被无意的发布。在请求消息中发送将使得请求和响应消息都不使用缓存。
- max-age：指示客户机可以接收生存期不大于指定时间（以秒为单位）的响应。
- min-fresh：指示客户机可以接收响应时间小于当前时间加上指定时间的响应。
- max-stale：指示客户机可以接收超出超时期间的响应消息。如果指定 max-stale 消息的值，那么客户机可以接收超出超时期指定值之内的响应消息。

### 状态码

当你请求HTTP时，服务器会响应一个状态码来判断你的请求是否成功，然后客户端应如何继续。以下是四种不同层次的状态码：

[Untitled Database](2015%2012%2009%20%E7%90%86%E8%A7%A3%20HTTP%20%E4%B8%8E%20REST%20API%20%5Btech%5D%20b8222c72088f41bca76a23898b6502e6/Untitled%20Database%20099d28d0ce0942bb9b2214c2d8ddeed3.csv)

以下是一些最重要的状态码：

请求成功的状态码：

[Untitled Database](2015%2012%2009%20%E7%90%86%E8%A7%A3%20HTTP%20%E4%B8%8E%20REST%20API%20%5Btech%5D%20b8222c72088f41bca76a23898b6502e6/Untitled%20Database%202f89f833959a433b949c449befe54dd5.csv)

客户端错误状态码：

[Untitled Database](2015%2012%2009%20%E7%90%86%E8%A7%A3%20HTTP%20%E4%B8%8E%20REST%20API%20%5Btech%5D%20b8222c72088f41bca76a23898b6502e6/Untitled%20Database%203aadc92948074618b7eacf52b770f885.csv)

### MIME 类型

一个文档的 MIME 类型决定了打开这个文档的软件怎样使用这个文档。在 HTTP 中服务器的响应头的中包含有文档的 MIME 信息，从而客户端可以知道怎样正确的使用这个文档。

常见的 MIME 类型有：

```
text/plain（纯文本）
text/html（HTML文档）
application/xhtml+xml（XHTML文档）
image/gif（GIF图像）
image/jpeg（JPEG图像）【PHP中为：image/pjpeg】
image/png（PNG图像）【PHP中为：image/x-png】
video/mpeg（MPEG动画）
application/octet-stream（任意的二进制数据）
application/pdf（PDF文档）
application/msword（Microsoft Word文件）
application/vnd.wap.xhtml+xml (wap1.0+)
application/xhtml+xml (wap2.0+)
message/rfc822（RFC 822形式）
multipart/alternative（HTML邮件的HTML形式和纯文本形式，相同内容使用不同形式表示）
application/x-www-form-urlencoded（使用HTTP的POST方法提交的表单）
multipart/form-data（同上，但主要用于表单提交时伴随文件上传的场合）

```

比如服务器端返回了一个 html 文本信息，但是指定它的 Content-Type 为 text/plain，那么浏览器并不会渲染出来这个网页，而是以纯文本的方式来展现它；如果指定它的 Content-Type 为 text/html 那么我们就能够得到我们想要的网页；如果指定它的 Content-Type 为 application/octet-stream 那么浏览器会直接下载这个 html 文档而不做展示；

## REST

API（Application Programming Interface），它是拿来描述一个类库的特征或是如何去运用它。如今很多人参考 API 文档时，常常参考一种可能会通过网络分享你的应用数据 HTTP API，例如，新浪微博提供一个 API 能让用户在特定的格式下请求博文，以便用户方便导入到自己的应用程序中，这便是 HTTP API 的强大之处。

REST（Representational State Transfer），是用来描述创建HTTP API 的标准方法的，他把四种常用的行为（查看（view），创建(create)，编辑(edit)和删除(delete)）直接映射到 HTTP 中已实现的 GET,POST,PUT 和 DELETE 方法，并通过标准的命名来避免 URL 定义的冲突。

首先，我们可以提供让我们执行这些功能的 API：

```
http://example.com/view_categories
http://example.com/create_new_category?name=Widgetizer
http://example.com/update_category?id=123&name=Foo
http://example.com/delete_category?id=123

```

显然这里面的逻辑是非常混乱的，我们不知道这些接口的功能是什么，需要借助第三方文档，同时一个 API 中可能命名一个 URL 为/view_categories，但是另一个 API 可能就命名成 /categories/all，使逻辑非常混乱。这时候我们可以使用 REST API 来使这些接口规范化，我们使用一个例子来解释 REST：

如果我们想要查看所有分类的列表，URL 将是这个样子：

```
GET http://example.com/categories

```

用 POST 方法新建一个用来新建一个分类：

```
POST http://example.com/categories
Data:
    name = Foobar

```

用 GET 方法查看一个分类的具体内容，我们从指定的部件id中获取：

```
GET http://example.com/categories/123

```

用 PUT 方法发送新数据来更新这个分类：

```
PUT http://example.com/categories/123
Data:
    name = New name
    color = blue

```

用 DELETE 方法来删除这个分类：

```
DELETE http://example.com/categories/123

```

### REST URL 分析

可以很清晰的看到如果我们想要「list all」这种操作的时候需要 GET 访问这个分类的地址 /categories 即可，如果想要访问一个具体分类的信息，那么 GET 请求地址加上相应的 id，如 /categories/123 如果是增加一个分类，那么对分类的全局地址 /categories 发送一个 POST 请求，并提交相应的参数完成。同理，对某一个具体分类的更新与删除操作可以使用 PUT、DELETE 请求到具体分类地址如 /categories/123

当 URL 地址需要嵌套的情况，可以在每个具体元素下加深一级目录，比如：

```
/categories/123/users
/categories/123/users/123/hobbits

```

依次类推。如果最终导致 URL 过长，我们可以将后一级的内容向前提：

```
/users/123/hobbits

```

### HTTP 状态码：

上文已经讲述了 HTTP 协议中一些常用的状态码信息，我们可以根据业务需要来返回合适的状态码

### API授权与认证

在一般的网页应用中，认证操作是经常要接收用户名和密码的，然后在 session 中保存用户 ID。用户的浏览器就会保存会话中的 ID 到 cookie 中。当用户在网站上访问需要认证授权的页面时，浏览器就会发送 cookie，应用程序就会查找 seesion 会话中的 ID（如果它没有失效的话），由于用户的 ID 保存在 seesion 中，用户就可以浏览页面了。

用这个 API，就可以使用 seesion 会话保存用户记录，有时候用户想直接访问API，或是用户想自己授权其他应用程序去访问这个API，这时这种方法就会暴露用户的用户名与密码这些敏感信息。

这个问题的解决方法是在认证的基础上使用秘钥。用户输入用户名和密码以登录，应用程序就以一个特殊秘钥返回给用户以备后续之需。这个秘钥可以通入应用程序，以至于如果用户想要选择拒绝应用更进一步的接入时，可以撤回这个秘钥。OAuth 是一个开放授权标准，它允许用户让第三方应用访问该用户在某一网站上存储的私密的资源（如照片，视频，联系人列表），与以往的授权方式不同之处是 OAUTH 的授权不会使第三方触及到用户的帐号信息（如用户名与密码），即第三方无需使用用户的用户名与密码就可以申请获得该用户资源的授权，因此 OAuth 是安全的。目前网上已经有很多关于 OAuth 的实现。