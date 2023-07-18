- tags: [blockchain](/tags.md#blockchain)
- date: 2018-11-24

# EOS nodeos启动过程

本文从源码的角度看 EOS 是怎样工作的，代码分析基于版本 [59626f1e6](https://github.com/EOSIO/eos/tree/59626f1e6361df3b715e926ee13a9a8e84d177af)，请读者自行获取，本文假设你对 EOS工作过程,C++ 等基础知识已经有一定了解。文中可能涉及错误请发邮件到 [i@timqi.com](mailto:i@timqi.com?subject=EOS%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%E9%94%99%E8%AF%AF) 反馈。

尝试编译源码 `./eos_build.sh`，按照提示操作通常没有什么问题。EOS 使用 cmake 组织编译逻辑。我们首先大致理清源码中各目录是什么：

```
├── Docker #构建docker镜像相关
├── contracts #一些系统关键合约如 eosio.token, eosio.system 和样例、测试合约
│   ├── eosio.bios #控制账号的资源分配，API权限不清等
│   ├── eosio.msig #多签支持合约
│   ├── eosio.sudo
│   ├── eosio.system #提供买卖RAM，抵押获取CPU，NET等系统服务   
│   ├── eosio.token #token管理合约
│   ├── eosiolib #为编写EOS合约提供C++ API
│   └── ...
├── eosio_build.sh #编译eos
├── eosio_install.sh #安装eos
├── eosio_uninstall.sh #卸载eos
├── externals #WebAssembly和C++一些外部工具类
├── libraries #主要代码库，我们重点分析
│   ├── appbase #应用基础框架，组织插架初始化、启动等
│   ├── builtins #编译器支持工具
│   ├── chain #区块链相关
│   ├── chainbase #供区块链使用的db
│   ├── fc #工具类
│   ├── softfloat #浮点运算相关支持
│   ├── testing 
│   ├── utilities #测试相关
│   ├── wabt
│   └── wasm-jit #webasembly相关
├── plugins #插件相关代码，如chain_api,history_api,http,mongo_db,wallet...等
├── programs #生成EOS相关各种命令行二进制文件
│   ├── CMakeLists.txt
│   ├── cleos #生成 cleos
│   ├── eosio-abigen #生成 eosio-abigen
│   ├── eosio-blocklog #生成 eosio-blocklog
│   ├── eosio-launcher #生成 eosio-launcher
│   ├── keosd #生成 keosd
│   └── nodeos #生成 nodeos
├── scripts #工具脚本，看文件名能猜个大概
├── tests #系统测试，大多是python脚本
├── tools
├── unittests #单元测试文件
└── ...

```

我们从 nodeos 的入口 main 函数开始 [programs/nodeos/main.cpp](https://github.com/EOSIO/eos/blob/59626f1e63/programs/nodeos/main.cpp#L93)。

```cpp
int main(int argc, char** argv)
{
   try {
      app().set_version(eosio::nodeos::config::version);
      // 系统注册 history_plugin 插件
      app().register_plugin<history_plugin>();

      auto root = fc::app_path();
      app().set_default_data_dir(root / "eosio/nodeos/data" );
      app().set_default_config_dir(root / "eosio/nodeos/config" );
      http_plugin::set_defaults({
         .address_config_prefix = "",
         .default_unix_socket_path = "",
         .default_http_port = 8888
      });
      if(!app().initialize<chain_plugin, http_plugin, net_plugin, producer_plugin>(argc, argv))
         return INITIALIZE_FAIL;
      
      ... 添加日志代码

      app().startup();
      app().exec();
   } catch( /* 错误处理 */ ) {
   }

   return SUCCESS;
}

```

`app()` 在 [libraries/appbase/application.cpp](https://github.com/eosio/appbase/blob/f3a63c1c04/application.cpp#L79) 中定义

```cpp
application& application::instance() {
   static application _app;
   return _app;
}
application& app() { return application::instance(); }

```

这是一个单例模式，`app()` 每次都返回同一个 _app 对象。

可以看到 nodeos 默认注册了 history_plugin, chain_plugin, http_plugin, net_plugin, producer_plugin 五个 autostart_plugins。然后调用 application 的 initialize 方法。在 application 的 initialize 方法中对一些配置参数进行初始化并且调用默认启动插件和 --plugin 参数传入插件的 initialize 方法。然后执行 application::startup 调用这些插件的 startup 方法。然后在 application::exec 中使用 `io_serv->run()` 开启 io 循环并注册接收到 SIGINT，SIGTERM，SIGPIPE 信号时停止程序。

```cpp
template<typename... Plugin>
bool                 initialize(int argc, char** argv) {
    return initialize_impl(argc, argv, {find_plugin<Plugin>()...});
}

bool application::initialize_impl(int argc, char** argv, vector<abstract_plugin*> autostart_plugins) {
   // 解析 help version data-dir config-dir ... 等参数并存储
   ...

   // 调用从命令行 --plugin 参数传入的 plugin 的 initialize 进行初始化
   if(options.count("plugin") > 0)
   {
      auto plugins = options.at("plugin").as<std::vector<std::string>>();
      for(auto& arg : plugins)
      {
         vector<string> names;
         boost::split(names, arg, boost::is_any_of(" \t,"));
         for(const std::string& name : names)
            get_plugin(name).initialize(options);
      }
   }
   try {
       // 初始化 history_plugin, chain_plugin, http_plugin, net_plugin, producer_plugin 五个插件
      for (auto plugin : autostart_plugins)
         if (plugin != nullptr && plugin->get_state() == abstract_plugin::registered)
            plugin->initialize(options);
      bpo::notify(options);
   } catch (...) {
      std::cerr << "Failed to initialize\n";
      return false;
   }

   return true;
}

void application::startup() {
   try {
      for (auto plugin : initialized_plugins)
         plugin->startup();
   } catch(...) {
   }
}

void application::exec() {
    // 监听到 SIGINT, SIGTERM, SIGPIPE 时退出程序
   std::shared_ptr<boost::asio::signal_set> sigint_set(new boost::asio::signal_set(*io_serv, SIGINT));
   sigint_set->async_wait([sigint_set,this](const boost::system::error_code& err, int num) {
     quit();
     sigint_set->cancel();
   });

   std::shared_ptr<boost::asio::signal_set> sigterm_set(new boost::asio::signal_set(*io_serv, SIGTERM));
   sigterm_set->async_wait([sigterm_set,this](const boost::system::error_code& err, int num) {
     quit();
     sigterm_set->cancel();
   });

   std::shared_ptr<boost::asio::signal_set> sigpipe_set(new boost::asio::signal_set(*io_serv, SIGPIPE));
   sigpipe_set->async_wait([sigpipe_set,this](const boost::system::error_code& err, int num) {
     quit();
     sigpipe_set->cancel();
   });

    // 开启事件循环
   io_serv->run();

   shutdown(); /// perform synchronous shutdown
}

```

至此 app 事件循环就启动了，EOS 插件化架构非常清晰易读。接下来我们从各模块分别来看。