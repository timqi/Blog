- tags: [blockchain](/tags.md#blockchain)
- date: 2023-07-23

# Spacemesh PoST

本篇分析介绍 [Spacemesh](https://spacemesh.io) 的工作原理。Spacemesh 是一个基于存储空间和时间证明的区块链协议，矿工挖矿之前需要先批盘，批盘有很多参数，需要根据系统配置使用 profiler 程序选择最优方案，而且批盘过程较慢需要使用GPU，矿工挖矿过程中不需要使用GPU。

White paper: [https://drive.google.com/file/d/18I9GPebWqgpvusI1kMnAB9nayBbL-1qN/view](https://drive.google.com/file/d/18I9GPebWqgpvusI1kMnAB9nayBbL-1qN/view)

主网每 5 分钟 200 个块，每 10 分钟 400 个块。通常交易在 1.5-7 分钟内可以确认，15-20 分钟内广播到全网。Spacemesh 保障全网不超过 $\frac{1}{3}$ 存储作恶的情况下可以安全工作。

主网参数：
```
layer-duration: 5m
layer-per-epoch: 4032 # 创世参数；计算可知每个 epoch 时间为 14 天
# epoch 大小确保每个miner都能提交ATX，比如全网100000个矿工，每个layer200个块，那么每个epoch至少需要500layer
```

Spacemesh 代币 SMH 总量 `2.4 billion`。其中 0.15 billion (6.25%) 预留为开发团队收益，从创世块之后的一年开始 Vest，分 4 年完全 Vest。矿工收益共 2.25 billion（93.75%） 收益发放时间表: [https://spacemesh.io/blog/spacemesh-issuance-schedule/](https://spacemesh.io/blog/spacemesh-issuance-schedule/)。矿工收益来自基础矿挖和链上手续费，其供应总量只与当前Layer（时间）有关，挖矿收益计算公式：

$AccumulatedSubsidy = TotalSubsidy x (1- e ^ {-\lambda (Layer - GenesisLayers + 1) })$
```
TotalSubsidy: 2.25 billion
λ: 0.000 000 212 274 865 905 007
GenesisLayers: 8064，即前两个 epoch
```

相关资源
- post: 批盘工具 [https://github.com/spacemeshos/post/blob/develop/cmd/postcli/README.md](https://github.com/spacemeshos/post/blob/develop/cmd/postcli/README.md)
- 硬盘性能测试：[https://github.com/spacemeshos/post-rs](https://github.com/spacemeshos/post-rs) d70ef76f

# How to make blocks

1. 注册 ATX，根据不同的 Space-Time，ATX 上有不同的收益权重
2. 使用 ATX，节点可以发布自己的 blocks 或者参与 Hare 投票
4. 由 Hare 协议简单确定块是否有效
5. 由 Tortoise 协议最终确定块是否有效

Spacemesh 中使用 `mesh` 而不是 chain 来描述账单结果，mesh 中有一系列 Layer，每个 Layer 中有很多块。每个 Layer 中的 blocks 是按 hash 随机排序的，每个 blocks 中的 tx 也是按 hash 随机排序的。每个 tx 可以出现在不同的 blocks 中，出现该 tx 的第一个 block 被视为有效的 block。

- Layer: 每个 Layer 是一段定长时间的概念，通常是 5min，这期间会产生一系列 blocks，这些块由 Hare 协议来确定最终是否有效
- Hare: 比较快速的确定块的有效性。用来解决拜占庭问题，由矿工参与投票选出 Layer 中合法的块，做简单的校验比如时间、tx合法性；并且生成块id，投票规则等为 Tortoise 协议做基础。Hare工作在 gossip 网络上
- Tortoise: 一个比较慢，但是最终确认块是否有效的投票计数协议
- 投票：每个块都对前一个 Layer 中的块做投票，并最终由 Hare 和 Tortoise 协议确定块最终的有效性。根据 spacetime 资源不同投票有不同的 weight 加持
- PoST(Proof of Space Time): 用户确保 Spacemesh 占用存储空间的算法。PoST 向磁盘中写入了一系列特定数据并且不会删除，每次执行 PoST 时算法会根据这些数据生成一个证明确保系统占用了一定量的磁盘空间。矿工每次执行 PoET 后都需要 PoST
- PoET(Proof of Elapsed Time): 用来确保矿工连续不间断的工作了多长时间的证明，PoET 需要查询相应的 Server，不是由矿工在本地运行的。PoET 是 NiPoST 的一部分
- NiPoST(Non-interactive Proof of Space Time): 用来证明矿工消耗了一定的存储空间，并且连续运行的一段时间。矿工每次提交矿的时候需要附上 NiPoST 证明，并且需要持续提交证明

- VDF: Verifiable Delay Function, Proof of Sequential Work
- VRF: Verifiable Random Function

> Unlike a PoST, a NIPoST has only a single phase. Given an id, a space parameter S , a duration D and a challenge ch, a NIPoST is a single message that convinces a verifier that (1) the prover expended S · D space-time after learning the challenge ch. (2) the prover did not know the NIPoST result until D time after the prover learned ch.

## ATX

ATX(Activation Transaction): 一种包含了 NiPoST 证明的特殊交易，每个矿工需要在每个 epoch 中发布 ATX。如果矿工有多个存储单元，则被认为是多个矿工，并且每个矿工有一个存储单元

每个 epoch 需要保证每个 miner 都能提交 atx，atx 在当前 epoch 是不成熟的，下个 epoch 才真正有效成熟，比如当前 epoch 为 1024 layer，矿工在 layer 1700 处提交了 atx，那么这个 atx 有效的区间范围在 layer 2048 - 3072。

ATX 中包含如下信息：
- Node ID
- Sequence Number `s`：每个节点需要维护一个发布 ATX 的序号
- Preview ATX：sequence number 为 `s-1` 的 ATX ID
- Layer Index `i`: ATX 将有效的 Layer ID
- Positioning ATX $i-\Delta_{epoch}$
- Start tick `t`: ATX 开始时的 sequential work tick
- End tick `t'`: ATX 结束时的 sequential work tick
- NIPoST: 包含前面所有信息的一个证明，时间必须是 `t' - t`
- Active set size `d`: 已经激活的 atx 集合的大小，这个不是 NIPoST 的参数
- View pointers:
- Signature: 

# How to calc reward

- NiPoST 证明是如何反应存储和时间大小的
- 怎样做难度调整
- 不同的难度是怎样反馈到用户最终收益上的

# PoET

PoET 是一个去中心化的服务，Spacemesh 官方会运行这个服务，同时任何第三方也可以运行，矿工请求 PoET 服务时需要付费，也就是说运行 PoET 服务是有利润的。

PoET 是串行模型，不能做并行优化，因此使用 ASIC 加速并没有优势。PoET 计算一些列与时间相关的哈希数据，不想 SHA256 一样，主流的计算方法由能力对其进行并行加速。PoET 在 Spacemesh 中也称为 PoSW(Proof of Sequential Work)

# 命令样例

启动节点：
```
["/Applications/Spacemesh.app/Contents/node/go-spacemesh","--config    ","/Users/qiqi/Library/Application Support/Spacemesh/node-config.json","-d","/Users/qiqi/Library/Application Support/Spacemesh/node-data/7c8cef2b","--grpc-private-listener","127.0.0.1:9093"]
 ```

# 几处关键功能代码位置

Spacemesh electron app 中的参数设置：[https://github.com/spacemeshos/smapp/blob/develop/desktop/posProfiler.ts#L38](https://github.com/spacemeshos/smapp/blob/develop/desktop/posProfiler.ts#L38)

节点启动参数配置：[https://github.com/spacemeshos/smapp/blob/develop/desktop/NodeManager.ts#L365](https://github.com/spacemeshos/smapp/blob/develop/desktop/NodeManager.ts#L365)

开始挖矿由 StartSmeshing RPC 入口开始，走到 activation 模块，其中在 node 中初始化的 atxBuilder 起了重要作用，atxBuilder 的初始化调用了许多 activation 模块的功能：PostSetupManager 负责检查批盘, PostSetupManager.StartSession 是挖矿前批盘检查的入口，mgr.init.Initialize(ctx) 调用了 spacemeshos/post 仓库的批盘方法；syncer.syncer.go 负责同步区块链信息并检查 atx 的有效性。

开始挖矿的入口，开始挖矿前会检查 post 数据是否有效，如果无效的话会重新生成: [https://github.com/spacemeshos/go-spacemesh/blob/1766164895d69061457b03d0223f5c1438fbcacf/api/grpcserver/smesher_service.go#L49](https://github.com/spacemeshos/go-spacemesh/blob/1766164895d69061457b03d0223f5c1438fbcacf/api/grpcserver/smesher_service.go#L49)。

具体实现开始挖矿的类，activation.Builder：[https://github.com/spacemeshos/go-spacemesh/blob/1766164895d69061457b03d0223f5c1438fbcacf/activation/activation.go#L61](https://github.com/spacemeshos/go-spacemesh/blob/1766164895d69061457b03d0223f5c1438fbcacf/activation/activation.go#L61)

StartSmeshing: [https://github.com/spacemeshos/go-spacemesh/blob/1766164895d69061457b03d0223f5c1438fbcacf/activation/activation.go#L188](https://github.com/spacemeshos/go-spacemesh/blob/1766164895d69061457b03d0223f5c1438fbcacf/activation/activation.go#L188)

主循环之前，生成 POST 证明：[https://github.com/spacemeshos/go-spacemesh/blob/develop/activation/activation.go#L312C30-L312C30](https://github.com/spacemeshos/go-spacemesh/blob/develop/activation/activation.go#L312C30-L312C30)

Smeshing 主循环, activation.go:Builder:loop：[https://github.com/spacemeshos/go-spacemesh/blob/1766164895d69061457b03d0223f5c1438fbcacf/activation/activation.go#L357](https://github.com/spacemeshos/go-spacemesh/blob/1766164895d69061457b03d0223f5c1438fbcacf/activation/activation.go#L357)

POST参数设置：[https://github.com/spacemeshos/go-spacemesh/blob/1766164895d69061457b03d0223f5c1438fbcacf/activation/post.go#L28](https://github.com/spacemeshos/go-spacemesh/blob/1766164895d69061457b03d0223f5c1438fbcacf/activation/post.go#L28)

Hare 相关：

主要逻辑在 hare/hare.go 文件中，hare.Start 方法为主要入口，启动了 layer 切换的 tickLoop, 非法投票的 malfeasanceLoop ,以及 outputCollectionLoop 监听所有 consensus process 的消息

切换 layer 时触发的逻辑：[https://github.com/spacemeshos/go-spacemesh/blob/develop/hare/hare.go#L318](https://github.com/spacemeshos/go-spacemesh/blob/develop/hare/hare.go#L320)；设置 layerid，设置 broker 开始在新的 layer 接收消息，获取所有的 goodProposals 并在设置为新的出块投票参数，创建 consensusprocess 并启动

consensus process 的主循环：[https://github.com/spacemeshos/go-spacemesh/blob/develop/hare/algorithm.go#L276](https://github.com/spacemeshos/go-spacemesh/blob/develop/hare/algorithm.go#L276)

根据 proposals 中的 atx 计算 weight,投票的weight 由 atx中的参数确定: [https://github.com/spacemeshos/go-spacemesh/blob/develop/blocks/utils.go#L207](https://github.com/spacemeshos/go-spacemesh/blob/develop/blocks/utils.go#L207)

系统预言机决定当前节点能不能参与proposals：[https://github.com/spacemeshos/go-spacemesh/blob/develop/hare/eligibility/oracle.go#L466](https://github.com/spacemeshos/go-spacemesh/blob/develop/hare/eligibility/oracle.go#L466)
