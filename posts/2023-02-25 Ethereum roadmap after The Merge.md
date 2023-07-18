- tags: [blockchain](/tags.md#blockchain)
- date: 2023-02-25

# Ethereum roadmap after The Merge

早在2015年，以太坊社区就发布了4个关于以太坊发展的重要阶段[https://blog.ethereum.org/2015/03/03/ethereum-launch-process](https://blog.ethereum.org/2015/03/03/ethereum-launch-process)：Frontier, Homestead, Metropolis, Serenity 。现在回顾来看每一部走来确实一部震撼史诗，不得不佩服V神等当时的远见，而且多年来能够按照Roadmap一步步落地，难得可贵。2022.09.15 The Merge 升级转 PoS 之后，ETH实质上进入 Serenity 阶段。本文将大致回顾一下ETH历史发展的几个阶段，并重点结合V神规划聊聊ETH今后的几个重要升级。

## Frontier

跑通基本的 ETH 链，矿工能够正常出块，上线 ETH 代币并支持基本的 DApp 开发运行流程。

这个阶段每个块的 gas 消耗限制在了 5k，并且在 2015.07.09 进行了 “Frontier thawing” 升级将每个块的 gas 消耗上限提高到 21k。并且这次升级引入了难度炸弹，为将来转 PoS 做基础

## Homestead

从 “Homestead”升级，即块高 [1,150,000](https://etherscan.io/block/1150000)  2016.03.14 处开始。主要升级了 EVM 和开发者相关的 EIPs，提高了开发者友好度，为 EVM 生态打基础

## Metropolis

从“Byzantium”升级，即块高 [4,370,000](https://etherscan.io/block/4370000) 2017.10.16 处开始。Metropolis 阶段经历了3次重大升级，Byzantium、Constantinople、Istanbul 均以帝国名字命名，这几次升级增提升了以太坊网络的性能，完善各种网络开发的周边工具

### - Byzantium 拜占庭

[4,370,000](https://etherscan.io/block/4370000) 2017.10.16 主要更新了：

- 块奖励由 5 变成 3
- 将难度炸弹推迟了一年
- 支持无状态改变的合约调用
- 添加了2层扩容、zk相关的加密方法支持

### - **Constantinople 君士坦丁堡**

[7,280,000](https://etherscan.io/block/7280000) 2019.02.28 主要更新了：

这次升级优化了Gas消耗，添加了与未创建的地址的交互的能力。

### - ****Istanbul 伊斯坦布尔****

[9,069,000](https://etherscan.io/block/9069000) 2019.12.08 主要更新了：

继续优化Gas消耗，并且增强了抗DoS能力。同时这次升级增加了基于zk-SNARKS 和 STARKS二层扩容方案支持

## Serenity

以上，到Istanbul升级，ETH 基本完成了Homestead阶段的目标，进入到Serenity阶段，这个阶段的目标以转PoS降低能耗，加子链加二层增强系统容量为主。这个阶段的几个重大升级多以Devconf举办地点命名。

当前，ETH 已经经过几次重大升级，完成了 The Merge，转到 PoS 出块。其中的升级包括：

- Beacon Chain Genesis：2020.12.01. 完成了 16384 次 32 个ETH Stake的充值操作，Beacon链最终于 2020.12.01日激活
- Berlin：[12,244,000](https://etherscan.io/block/12244000) 2021.04.15 继续优化一些opcode 的gas消耗，并且支持多类型 Transaction
- **London:** [12,965,000](https://etherscan.io/block/12965000) 2021.08.05 升级 [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559)
- [Arrow Glacier](https://ethereum.org/en/history/#arrow-glacier),  [Gray Glacier](https://ethereum.org/en/history/#gray-glacier) 两次推迟难度炸弹，延期了 The Merge上线时间
- Bellatrix：2022.09.06 升级Beacon链支持 The Merge，最终PoW难度定为 58750000000000000000000
- **Paris：2022.09.15 The Merge**

## After The Merge

The Merge 之后，ETH 转到 PoS 出块，降低了能源消耗。同时V神也为 ETH 的后续发展规划做了介绍，其中绿色部分是当前完成进度

[https://twitter.com/VitalikButerin/status/1588669782471368704/photo/1](https://twitter.com/VitalikButerin/status/1588669782471368704/photo/1) 

![Untitled](/images/2023-02-25-1.png)

### The Surge

支持二层 Sharding，达到 10w  TPS容量

主要升级内容是 [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844) 。ETH 2.0 最终形态之前的过渡方案，引入了可验证的 Blob 交易类型，笔 Calldata更便宜，每个Blob Slot可以承载 1MB 数据，用以验证二层网络上的交易是否合法。

相关项目：二层项目：Op,Arbitrum,zkSync, [https://l2beat.com/scaling/tvl](https://l2beat.com/scaling/tvl)

### The Scourge

重点解决夹汉堡的问题。通过 PBS 协议，把区块构建者和网络维护者分开，从而避免从交易发出到上链过程中由于ETH链路上带来的损耗问题。

相关项目：Flashbots，BloxRoute

### The Verge

这次升级的主角是 zk 算法的落地应用，使整个系统能够以很低的成本快速验证交易是否有效。V神预计，到时zk领域的算法已经成熟，并且产生了相关ASIC芯片，个人认为在充分市场竞争的条件下个厂商推出的验证设备效率是几乎相同的，这里面存在现在矿池模式的业务

相关项目：Scroll, zkSync, Ploygon

### The Purge, The Splurge

这个阶段重点在一些历史技术实现不完美的地方修修补补，比如数据爆炸带来的问题，定期清除1年以上的旧数据，进一步提升 zk 验证性能等