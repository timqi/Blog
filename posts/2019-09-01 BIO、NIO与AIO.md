- tags: [tech](/tags.md#tech)
- date: 2019-09-01

# BIO、NIO与AIO

IO是操作系统提供的基础功能，之前介绍了[网络Server模型的演进](/2017/09/28/http-server-model/)就是基于IO的改进。在语言层面，不同语言对操作系统的IO能力进行了不同的封装与接口的统一，如Java的NIO在linux平台使用的epoll而windows平台使用的iocp，这也是Java作为高级语言层面对操作系统功能统一封装的一个体现。本文结合Java具体代码了解一下什么是BIO、NIO与AIO。

要理解不同IO模式，首先我们要回顾几个概念：

同步与异步：

- **同步**：发起调用后，响应方未处理完成响应之前则该条用不返回
- **异步**：发起调用后，响应放立即返回该调用已被接受正在处理，实际上处理并未完成，等待处理真正完成时响应方通过事件或回调通知调用方处理结果

阻塞与非阻塞：

- **阻塞**：发起调用后，调用者挂起一直等待响应
- **非阻塞**： 发起调用后，调用者不用等待，可以先去干其他的事情

我们这里都是在描述操作系统的IO能力，也是就内核进程与用户进程之间的关系。所以调用者是指用户进程，响应方指操作系统内核。同步与异步的概念是描述内核收到请求时的行为，而阻塞与非阻塞的概念是描述用户进程的处理方案。

## BIO

BIO模型的服务端通常有Acceptor线程负责监听客户连接，一旦收到连接请求则掉用`accept()`方法获取相对的socket并开启新线程专门处理这个连接，每个线程为一个socket独占，这是典型的请求-应答模型。显然是**同步阻塞**的。我们用代码实现：

```java
public class BIO {
    public static void main(String[] args) {
        try {
            ServerSocket serverSocket = new ServerSocket(8080);
            while (true) {
                Socket socket = serverSocket.accept();
                new Thread(() -> {

                    try {
                        InputStream inputStream = socket.getInputStream();
                        StringBuilder stringBuilder = new StringBuilder();
                        BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(inputStream));
                        String line = null;
                        while ((line = bufferedReader.readLine()) != null) {
                            stringBuilder.append(line);
                        }
                        String requestString = stringBuilder.toString();
                        System.out.println(requestString);

                        OutputStream outputStream = socket.getOutputStream();
                        outputStream.write(requestString.getBytes());
                        outputStream.flush();
                    } catch (IOException e) {
                        e.printStackTrace();
                    } finally {
                        try {
                            socket.close();
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                    }
                }).start();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}

```

在server环境中，线程是非常宝贵的资源，线程创建、切换、销毁的成本都非常高，而且在上面的模型中如果请求量过大，太多的连接将触发大量的线程创建操作，很容易造成服务器瞬间瘫痪。

所以在线程模型基础上提出了使用**线程池**来处理连接。即服务启动时创建线程池，监听线程收到请求时将连接封装成一个Runnable任务放进线程池处理，这样可以有效提高线程利用率，减少不必要的创建与销毁，同时线程池的任务数量可控，不至于导致服务器崩溃。

## NIO

上面即使用了线程池优化，但是连接建立后每个线程仍有很长时间处于IO等待状态，为了进一步提高线程利用率，可以让正在等待的线程处理其他工作。

Java NIO是一种同步非阻塞的I/O模型，提供了Channel、Selector、Buffer的抽象。BIO中我们通常操作Stream对象进行读和写，而NIO中的读写操作都是针对Channel进行的，Selector会定时查看Channel的集合是否有读或写的触发，如果有则处理，如果没有则等待下次轮询查看。这样便消灭了Worker线程的IO等待时间。

NIO的逻辑实际上相当于在用户态模拟了Linux OS的selector多路复用，减少了Worker线程的等待时间。

```java
public class NIO {
    public static void main(String[] args) throws IOException {
        Selector serverSelector = Selector.open();
        Selector clientSelector = Selector.open();

        // 监听客户端连接并accept，accept之后添加了Worker读监听中
        new Thread(() -> {
            System.out.println("start accept.");
            try {
                ServerSocketChannel serverChannel = ServerSocketChannel.open();
                serverChannel.socket().bind(new InetSocketAddress(8080));
                serverChannel.configureBlocking(false);
                serverChannel.register(serverSelector, SelectionKey.OP_ACCEPT);

                while (true) {
                    if (serverSelector.select(1) > 0) {
                        Set<SelectionKey> selectionKeys = serverSelector.selectedKeys();
                        Iterator<SelectionKey> iterator = selectionKeys.iterator();
                        while (iterator.hasNext()) {
                            SelectionKey key = iterator.next();

                            if (key.isAcceptable()) {
                                System.out.println("accepted.");
                                SocketChannel acceptChannel = ((ServerSocketChannel) key.channel()).accept();
                                acceptChannel.configureBlocking(false);
                                acceptChannel.register(clientSelector, SelectionKey.OP_READ);

                                iterator.remove();
                            }
                        }
                    }
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }).start();

        new Thread(() -> {
            System.out.println("start reader listening.");
            while (true) {
                try {
                    if (clientSelector.select(1) > 0) {
                        Set<SelectionKey> keys = clientSelector.selectedKeys();
                        Iterator<SelectionKey> iterator = keys.iterator();
                        while (iterator.hasNext()) {
                            SelectionKey key = iterator.next();

                            if (key.isReadable()) {
                                SocketChannel clientChannel = (SocketChannel) key.channel();
                                ByteBuffer byteBuffer = ByteBuffer.allocate(1024);
                                clientChannel.read(byteBuffer);
                                byteBuffer.flip();
                                String requestString = StandardCharsets.UTF_8.decode(byteBuffer).toString();
                                System.out.println(requestString);
                            }
                        }
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }).start();
    }
}

```

## AIO

尽管NIO中我门已经大大提高了IO效率，但是本质上还都是同步IO的实现。即在内核完成IO操作之后才能返回给用户程序，并且此时数据的读写并没有由内核完成，仍然需要用户态程序自行做读写操作。

为了进一步提升效率我们可以把IO工作进一步交给内核去做，当内核收到调用是立即返回、释放用户态进程，并进行数据IO，直到数据Buffer准备就绪已经放到用户态内存区后在通知用户的进程去处理IO数据，这就是IO的异步交互过程。

虽然AIO理论上是效率最高的，但相比与Window的iocp，Linux上的AIO实现还存在很多不稳定，效率不高的地方，比如IO数据在内核态与用户态需要两次拷贝。在面对大流量挑战时Java NIO已经有很多业务上的坑了，AIO更是不算成熟的解决方案，综合分析java上使用Netty封装的NIO方案是最好的。

另外，AIO的异步思想也带来了很多编程代码层面的挑战，比如使用了AIO的Node.js中的回调地狱，异步逻辑在处理同步问题时显得更加棘手，对此又引入了async、await的同步化语义显得不够优雅。同时Python3的AIO也使用了async、await语义，并且由于Linux 内核的AIO不构完善，Node.js 与Python3的AIO实现也止步与编程语言层面，整体不如NIO成熟。