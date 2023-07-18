- tags: [blockchain](/tags.md#blockchain)
- date: 2023-02-27

# Ethereum Shanghai Capella 升级

以太坊社区关于上海升级提现支持的介绍：[https://ethereum.org/en/staking/withdrawals/](https://ethereum.org/en/staking/withdrawals/)

上海升级主要合并了 EIP4895 StakedETH 的提现能力，当前已经在  Sepolia 测试网合并，Goerli 和 主网上线日期待定。上海升级是即巴黎升级（The Merge [https://github.com/ethereum/execution-specs/blob/master/network-upgrades/mainnet-upgrades/paris.md](https://github.com/ethereum/execution-specs/blob/master/network-upgrades/mainnet-upgrades/paris.md)）后的一次重大更新，当前ETH网络中 stake 了超过 16M 枚ETH，分布在 50w+ 个validator中。其中不凡是在 2020 年已经参与质押的，允许提现后预计可能对 ETH 价格造成一定压力。

![Untitled](/images/2023-02-27-1.png)

## 上海升级内容：

[https://github.com/ethereum/execution-specs/blob/master/network-upgrades/mainnet-upgrades/shanghai.md](https://github.com/ethereum/execution-specs/blob/master/network-upgrades/mainnet-upgrades/shanghai.md)

- [EIP-3651: Warm COINBASE](https://eips.ethereum.org/EIPS/eip-3651) 降低coinbase gas，鼓励token支付
- [EIP-3855: PUSH0 instruction](https://eips.ethereum.org/EIPS/eip-3855) 增加初始化变量为0的opcode，降低gas
- [EIP-3860: Limit and meter initcode](https://eips.ethereum.org/EIPS/eip-3860) 支持的合约大小翻倍，鼓励更大型的 DApp
- [EIP-4895: Beacon chain push withdrawals as operations](https://eips.ethereum.org/EIPS/eip-4895) StakedETH 提现
- [EIP-6049: Deprecate SELFDESTRUCT](https://eips.ethereum.org/EIPS/eip-6049) 预告 SELFDESTRUCT 指定将被废弃

## EIP-4895

没有使用传统的 Transaction 类型作为提现交易，而是在共识层上定义了新的指令 `withdrawal` 。以此降低系统复杂度，减小出错的概率。

指令的具体编码格式为：`[index, validator_index, address, amount]`。多个  withdrawl 合并打包成为 withdrawls，用于计算科验证的 withdrawls root。

## ****Staking withdrawals****

提现操作由需要 validator 配置好提现地址，并签一个 "voluntary exit” 消息并且把消息广播到 beacon 链上，然后 beacon 链将根据一个 “Sweep” 的规则按计划将 ETH 提现。

### sweep

1. 将所有 validator 编好序列，作为一个环形队列
2. 每次出块前，作为 proposer 的节点将从队列起点依次检查各 validator 是否满足提现条件，如果满足则构建一个提现指定到块里，每个块最多接收16笔提现。提现条件满足一下3点：
    1. validator 已经设置了提现地址
    2. validator 设置为可提现，或者已经退出了 stake 竞选
    3. 如果validator没有退出竞选，但是余额大于32，则仅支持提现超过32余额的部分
3. 出块金额不能自定义，只能是超过32的收益部分（这部分将根据sweep自动分发）或者是一次性全部提现。原则上提现规则是将不参与 stake 部分的金额一次提完。

同时，提现操作不消耗 gas。按上面的逻辑，每个块可提现 16 笔，根据每个块12s计算，每天可以提现 115200 个节点。也就是  3686400 枚 ETH。挤压的提现笔数与对应的时间对比表格如下所示：

![Untitled](/images/2023-02-27-2.png)

## Capella

Capella升级是信标链上支持提现消息的部分，在部署 Capella 之后，validator 可以向网络签发 update withdrawls key, voluntary 等消息