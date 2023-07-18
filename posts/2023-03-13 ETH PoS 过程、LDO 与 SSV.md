- tags: [blockchain](/tags.md#blockchain)
- date: 2023-03-13

# ETH PoS 过程、LDO 与 SSV

# 交易上链过程

1. 用户通过钱包或者 web3 库签名目标 tx 并发送给节点 RPC API，此时用户指定 txfee，base部分燃烧掉，剩余部分作为validator的收益
2. 交易最先到达节点的执行层，验证 tx 有效后会通过 p2p 网络向全网广播，最终添加到网络大部分节点的 mempool 中；一些高级用户会将用户发送给类似 Flashbots 的 Builder 以获取定制的交易排序能力
3. ETH 网络中存在中选的出块节点，他将负责在网络中提议并广播下个区块。每个节点包括执行层、共识层、验证层。区块由执行层传递给共识层并添加PoS奖励，惩罚等共识信息后向全网广播。通信内容详见：[Connecting the Consensus and Execution Clients](https://ethereum.org/en/developers/docs/networking-layer/#connecting-clients)
4. 其他节点收到请求之后验证区块有效，并添加到本地数据库中
5. 上述过程经过全网超过 2/3的节点确认后基本确定已经出块

# 类 BFT 系统，PoS 共识

![Untitled](/images/2023-03-13-1.png)

多数 PoS 系统都是 BFT（Byzantine Fault Tolerance）的修改

1. Pre prepare：Proposer 根据既定规则，发表提案并广播
2. Prepare：Validators 收到提案，如果通过验证则广播 prepare msg，如果不通过在不作响应
3. Commit：Validator如果收到超过 2/3 节点的 prepare 后则广播 commit msg
4. Reply：Validator 收到超过 2/3 节点的 commit 后则实际执行操作

ETH 系统每 32 个块（slot）也就是6.4分钟做一次随机派选，具体介绍参考：[https://info.etherscan.com/epoch-in-ethereum/](https://info.etherscan.com/epoch-in-ethereum/)

# PBS, Proposer-builder Separation

当前ETH网络的出块逻辑是 validator 从 ETH Gossip 网络中获取 transaction，然后构建成一个 Block 并打包到 p2p 网络中。而 PBS 方案是要把这两个过程分开，block builder 只负责从用户侧获取各种交易，然后构建一个 block 传输给 block proposer，proposer 本身是无法直接看到block 内容的，他只能跟据每个 block 的收益大小向 p2p 网络提议打包利润最大的那个块。

这样做有几点原因：

- 抗审查，共识层看不到交易信息，builder的门槛又足够低，每个人都可以构建block
- 禁止一些大矿工既做选手又做裁判获取不对等竞争优势，比如 MEV
- 为 Danksharding 扩容做准备

# MEV-boost （by Flashbots)

mev-boost 是PBS 的一个实现

[https://docs.bloxroute.com/apis/mev-solution/mev-relay-for-validators](https://docs.bloxroute.com/apis/mev-solution/mev-relay-for-validators)

[https://boost.flashbots.net](https://boost.flashbots.net/)

[https://github.com/eth-educators/ethstaker-guides/blob/main/MEV-relay-list.md](https://github.com/eth-educators/ethstaker-guides/blob/main/MEV-relay-list.md)

![Untitled](/images/2023-03-13-2.png)

![Untitled](/images/2023-03-13-3.png)

# Lido 与 stETH

- 当前stake矿池有哪些

Lido 与交易所具有统治性份额 [https://dune.com/hildobby/eth2-staking](https://dune.com/hildobby/eth2-staking)

![Untitled](/images/2023-03-13-4.png)

- stETH 的流动性优势

我们知道直接在 ETH 主网 Stake 需要至少 32ETH 和运行 validator 节点，并且不能提现（Shapella 升级之前）。同时运行 validator 节点也是技术门槛非常高的，如果因为网络、性能问题导致出块故障还会造成损失，共识网络会直接从质押的 32ETH 中扣除相应罚金。

应运而生的就是 Pool 服务，托管技术细节给 Pool 处理同时避免了余额不足 32 ETH 还想参与 ETH Stake 质押的尴尬。但是此时同样有一个问题是已经质押的 ETH 无法流通，不能参与 DeFi 挖矿等。

stETH 的方案是质押 ETH 的同时像你派发等额的 stETH token，理论上 stETH 可以等额兑换成相应的 ETH，而此时 stETH 有 ETH 资产背书，即可参与到其他的 DeFi 应用中，比如 Curve： [https://curve.fi/#/ethereum/pools/steth/deposit](https://curve.fi/#/ethereum/pools/steth/deposit)

- stETH 是怎么实现每日收益派发的

![Untitled](/images/2023-03-13-5.png)

![Untitled](/images/2023-03-13-6.png)

用户余额是用户当前所占share的比例乘以当前pool 所持有的ETH总值。这里Lido.sol 合约实现了获取当前Pool所持有 ETH 总值的方法，由于这个值随着 Stake 的收益增加是会逐步增加更新的，那么也就意味着持有 stETH 用户的余额会不断增加，但是没有任何交易产生。Curve 池支持这种动态余额的收益所以质押在 Curve 的stETH 不仅能获得LP 收入还能获得 Stake 收入。但是传统的 Uniswap 的池 不支持动态余额的 Token。

![Untitled](/images/2023-03-13-7.png)

# SSV

- Stake 的单点故障问题

ETH Stake 的过程中要求 validator 只能运行一个节点，并且全天不间断在线，否则就会收到网络惩罚。但是实际工程应用中存在很多不可抗力不得不停机，比如地震自然灾害。

- SSV 的解决方案

SSV 则提出了一个方案，将 validator key 拆分成多个（可以理解为多签）并存入多个 node 无需信任的中，当其中一个 node 例行维护或者因不可抗力停机的时候，剩余的 node 可以根据手中的 key 对网络做出响应，从而实现了节点的高可用互备，今儿提高收益。

- SSV 与 Lido

质押的 ETH 并不是直接由 Lido 搭建节点，Stake 到以太主网上，而是通过第三方运营商[https://operatorportal.lido.fi/9a53ec3590be472c81ee33db6ec86689](https://operatorportal.lido.fi/9a53ec3590be472c81ee33db6ec86689) 实现的。SSV 是针对运营商（跑节点的人）提供的高可用解决方案，从 Lido 的角度出发，为实现更稳定的高收益，是希望它托管的运营商能够有高可用方案的，SSV既是一个不错的解决方案。