- tags: [blockchain](/tags.md#blockchain)
- date: 2023-03-20

# MPC, Smart Contract Wallet 与 EIP-4337

中心化的托管钱包面临的问题在 FTX 事件后越来越显现。而传统的加密钱包管理方法又过于依赖单一私钥的保存，传输，有很多局限性，安全风险也较大。本文提到的 MPC、合约钱包目的就是为了保留去中心化优势的基础上增强易用性，安全性。

# MPC，Multi-Party Computation

MPC是一种安全计算技术，它允许多个参与方在不泄漏各自的私有数据的前提下获得真确的计算结果，并保证计算结果的隐私和安全。通常MPC的工作过程分为：

1. 数据切分：将输入数据分成多份发给不通保管方，并且保管方之间互相不知道对方的数据
2. 加密：每个参与方将自己掌管的数据做单项加密并广播给其他参与方
3. 解密：参与各方在本地对其他参与者的数据进行非对称解密，并将自己分配的数据和其他参与方的数据进行计算
4. 合并，每个参与方将自己的计算结果广播，总重可以拼接出完整结果

# MPC-TSS

OpenBlock: [https://openblock-support.zendesk.com/hc/zh-cn/articles/6991541876763-什么是-MPC-安全多方计算-和-MPC-单元-](https://openblock-support.zendesk.com/hc/zh-cn/articles/6991541876763-%E4%BB%80%E4%B9%88%E6%98%AF-MPC-%E5%AE%89%E5%85%A8%E5%A4%9A%E6%96%B9%E8%AE%A1%E7%AE%97-%E5%92%8C-MPC-%E5%8D%95%E5%85%83-)

TSS（Threshold Signature Scheme）实现了一份信息切成 n 片后，通过对其中 t 个切片的验证并可回复完成信息的算法，关于 TSS 有一个开源实现：[https://github.com/LatticeX-Foundation/opentss](https://github.com/LatticeX-Foundation/opentss)

![Untitled](/images/2023-03-20-1.png)

### 与多签的区别：

多签是在多个参与方之间共享多个密钥以避免单点故障。多签需要系统层面的支持，如BTC P2SH，并且系统很好的记录了那些密钥签署了相关交易。

TSS中只有一个密钥，这个密钥被分为多份，获取多个密钥分片，超过阈值后即可恢复密钥。

### 一个例子：

求平均工资：

- Arnold：工资$45000
- Bonnie：工资$41000
- Chen：工资$53000
- Daniel：工资$27000

![Untitled](/images/2023-03-20-2.png)

# 合约钱包

合约钱包本身一个合约账号，本身没有私钥并且受普通账号控制，但是合约钱包将钱包的逻辑如转币交由智能合约控制，那么能够实现一些高级自定义逻辑，如：

- 转币小于某个金额可以用私钥A转币，大于某个金额则需要私钥B转币
- 治理账号能够修改合约钱包中不同资金的授权账号

# EIP-4337

账户抽象：[https://eips.ethereum.org/EIPS/eip-4337](https://eips.ethereum.org/EIPS/eip-4337)

以太坊账号分为两种：一个私钥对应的普通账号（EOA）； 通过部署代码实现的合约账号。

当前系统中对账号是有典型限制的，比如闲了合约账号：

- 不能主动发起交易

限制了普通账号：

- 不能自定义签名方案，必须使用 ECDSA
- Gas必须使用 Ether支付
- 私钥就是账户，丢失私钥意味着丢失账号

EIP-2938 [https://eips.ethereum.org/EIPS/eip-2938](https://eips.ethereum.org/EIPS/eip-2938) 尝试解决这些限制，但是他对共识的改变太大，而 4337 的方案巧妙的避开了这些变化

![Untitled](/images/2023-03-20-3.png)

EIP-4337 的主要观点是为合约账号引入普通账号的能力。通过引入特殊交易，重点使用户能用使用合约自定义的鉴权过程，而不是必须使用 ECDSA 的私钥方案