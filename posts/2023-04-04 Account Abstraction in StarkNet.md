- tags: [blockchain](/tags.md#blockchain)
- date: 2023-04-04

# Account Abstraction in StarkNet

# ETH 账户的特点

1. 每个账号都有一个对应的**余额**和**nonce**状态记录
2. EVM上硬编码了账号私钥验证和执行tx的逻辑
3. 需要一个地址；意味着**账号（Account）和Signer（私钥持有者）是同一个概念**

# 将账户和 Signer 解偶，即账户抽象

账号的概念用作保管资产，Signer 作为账号上资产转移权的一个验证方式。所以在账户抽象的场景下每个账户的能力可能是不同的，而传统的账号管理方式每个账户都是一样的。

解偶后可以简单的实现包含不限于以下功能

- 多签
- multicall
- 由用户选择加密曲线，而并不强制 secp256k1
- 社交恢复（MPC）
- 可以使用Token支付gasfee，项目方可以为账户支付gasfee

# StarkNet 上的账户

每个 starknet 网络的账户都是一个合约，并且必须制止下面 3 个函数：

- `__validate__`
- `__validate_declare__`
- `__execute__`

当账户收到tx请求是会优先调用 `__validate__` ，如果结果合法，将会调用 `__execute__` 。同时 sequencer 也能够根据validate的结果决定是否收手续费。

# Nonce

系统依然为每个合约账户维护了一个nonce字段，所以具有相同 hash 的 tx 可以被重复执行

![1.svg](/images/2023-04-04-1.svg)

# TX 执行过程

![2.svg](/images/2023-04-04-2.svg)

# 练习

[https://github.com/starknet-edu/starknet-accounts](https://github.com/starknet-edu/starknet-accounts)