- tags: [tech](/tags.md#tech)
- date: 2015-10-05

# Github 的 Webhooks

在 git 中，当一个仓库有重要的事情发生，比如进行仓库的 update, push 操作的时候，会触发这个仓库中配置的特定的脚本运行。这些配置文件通常在 git 仓库的 .git/hooks/ 目录下。 git init 时默认将特定的 hooks 脚本放在这个目录并以 .sample 为后缀名，以 .sample 为后缀名的 hooks 脚本默认是不生效的，需要去掉 .sample 后缀名使相应的脚本生效。

可见 hooks 脚本为我们提供了 git 仓库状态发生改变时的响应方法。而 Webhooks 就是 Github 对托管在 Github 上的仓库或项目组放生状态变化时触发的响应动作。通过配置 Github Webhooks，我们可以知道某个项目仓库的状态变化信息。比如向一个仓库提交 push，Github 便会向配置中指定的 URL 发送一个装载特定数据的 HTTP POST 请求通知这一变化。POST 的内容是可以定制的，具体参见： [https://developer.github.com/webhooks](https://developer.github.com/webhooks/)。通过这个 POST 请求，我们可以刷新数据，构建应用甚至部署代码等。下面简是在 Github 中配置 Webhooks 的方法。

首先在你的 repo 右侧点击 settings 按钮，

![2015 10 05 Github 的 Webhooks [tech] d1c26eec80a34035b2365ed2eeee4567/2015-10-05-1.png](/images/2015-10-05-1.png)

然后选择 Webhooks & services，点击右上角的 Add webhook：

![2015 10 05 Github 的 Webhooks [tech] d1c26eec80a34035b2365ed2eeee4567/2015-10-05-2.png](/images/2015-10-05-2.png)

填写 POST 的数据格式，URL 地址和密钥后点击 Add Webhook 按钮完成配置。

接下来便服务器端接收响应 URL 地址的 POST 请求并做相应处理即可。