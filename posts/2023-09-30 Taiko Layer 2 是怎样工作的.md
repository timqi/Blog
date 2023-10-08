-  tags: [blockchain](/tags.md#blockchain)
- date: 2023-09-30

# Taiko Layer 2 是怎样工作的

![zk-rollup过程](/images/2023-09-30-zkrollup-pool.png)

zk项目现状：[https://mirror.xyz/aoraki-labs.eth/19n2rbhplGveGF1djiGDPsPZ_LWlYJpODr4byPAVSoY](https://mirror.xyz/aoraki-labs.eth/19n2rbhplGveGF1djiGDPsPZ_LWlYJpODr4byPAVSoY)

奖励计算框架：[https://docs.zkpool.io/products/introduction](https://docs.zkpool.io/products/introduction)。不同项目有不同的代币，并且同时有不同的奖励惩罚机制，作为pool应该抽象并封装完这些逻辑，暴露给用户的只是收益结算，具体的stake，bond等逻辑由矿池完成。矿池通过费率cover惩罚损失。

Taiko 是使用零知识证明的以太坊二层扩展网络。Taiko 本身运行了 patched geth 作为二层网络的主要业务逻辑，二层和以太坊主网上部署了不同的智能合约来处理二层网络的 Rollup。[https://github.com/taikoxyz/taiko-mono](https://github.com/taikoxyz/taiko-mono) 网络部署通常分为几步：

1. 生成 genesis.json 数据，包含了在 L2 上的智能合约数据以及产生创世区块所需要的数据
2. L2 成功运行以后在以太主网部署相关合约，需要用到 L2 的一些原数据，如 Rollup 合约部署地址，创世块哈希等

Taiko 是 Type1 的 zk-EVM，关于 evm type介绍：[https://vitalik.ca/general/2022/08/04/zkevm.html](https://vitalik.ca/general/2022/08/04/zkevm.html)

![Verifying blocks](/images/2023-09-30-01.png)

## Taiko 是怎样产生并证明区块有效的

Taiko 同样使用区块记录数据，那么首先就是用产生合法的 txList，每个 tx 有效性的要求和以太一层网络一样。对于在 L2 上产生有效的 `txList`，通常有效的 `txList` 满足条件：

1. 字节数小于 blockMaxTxListBytes
2. 可以适用 RLP 编码
3. tx 数量不大于 blockMaxTransactions
4. 所有 tx 消耗的 gas 总和不大于 blockMaxGasLimit

1. Proposing 是 permissionlessly的，大家都可以在 TaikoL1 合约的有效性约束下提议一个区块
2. Taiko Node 会从合约中下载区块数据并验证txList的有效性，过滤掉nonce不合法或者余额不足的tx之后作为一个有效的L2区块，如果没有有效的tx，那个L2区块将只包含一个anchor transaction

**L2 上产生的 txList 最终会进入 L1，但是智能合约无法直接访问到这些数据，EIP-4844 升级后会添加 `blobHash` opcode。blob数据是一个小于 4096项的多项式参数**

Anchor交易：L2上的每个块的第一笔交易都必须是 TaikoL2.anchor() 并且使用了合法的如入参和 gaslimit，并且调用地址是 taiko_l2 合约的地址，tx的发起者必须是 GOLDEN_TOUCH_ADDRESS，相关地址和签名数据定义在了 TaikoL2Signer [https://github.com/taikoxyz/taiko-mono/blob/db195da154e34c608f336dc906b5f89fdb5b326d/packages/protocol/contracts/L2/TaikoL2Signer.sol#L14](https://github.com/taikoxyz/taiko-mono/blob/db195da154e34c608f336dc906b5f89fdb5b326d/packages/protocol/contracts/L2/TaikoL2Signer.sol#L14) 文件中，合约调用的txfee 是0。调用函数地址是 [https://github.com/taikoxyz/taiko-mono/blob/ee2688156733d49cbf43c5178211db95a7079b26/packages/protocol/contracts/L2/TaikoL2.sol#L118](https://github.com/taikoxyz/taiko-mono/blob/ee2688156733d49cbf43c5178211db95a7079b26/packages/protocol/contracts/L2/TaikoL2.sol#L118)

结合L2上anchor tx的信息可以构建出 BlockMetadata [https://github.com/taikoxyz/taiko-mono/blob/c0d18e86a7d1c3f62297288c1c55a89aaa4591d3/packages/protocol/contracts/L1/TaikoData.sol#L105](https://github.com/taikoxyz/taiko-mono/blob/c0d18e86a7d1c3f62297288c1c55a89aaa4591d3/packages/protocol/contracts/L1/TaikoData.sol#L105) BlockMetadata的内容将作为将来ZKP电路证明的输入参数

```solidity
struct BlockMetadata {
 uint64 id;  // L2 块高
 uint64 timestamp; // L2 出块时间
 uint64 l1Height; // 对应的 L1 块高
 bytes32 l1Hash; // 对应的 L1 块哈希
 bytes32 mixHash; // 随机数，用作加盐，将做个L2的块对应高同一个L1的块中
 bytes32 txListHash; // L2 txList的哈希
 uint24 txListByteStart; // txList其实位置偏移字节数
 uint24 txListByteEnd; // txList结束为止便宜字节数
 uint32 gasLimit; // 本块最大可消耗的gas上限
 address proposer; // L2上proposer的地址
 address treasury; // L2上basefee的接受地址
 TaikoData.EthDeposit[] depositsProcessed; // L1->L2的充值处理情况
}
```

同时 Taiko 还定义了 L2 的区块头结构，这些数据不一定都在 L1上永久存储，但是区块头的hash 是zk证明的一部分，可以通过 evidence.blockHash 获取

## IProver 实现使用 ERC-(20/721/1155) 支付 Prover 的证明费用

L2区块的证明由proposer 发起新区块的提议，prover通过zk相关计算为这个区块生成proof以获得佣金。这个过程prover需要和proposer事先签订一个off-chain 合约，由proposer发起，在限定的时间里prover如果能够给出合法证明的话，即向prover转移约定好的ERC-20或相关NFT代笔。作为prover需要实现 IProver 能力，[https://github.com/taikoxyz/taiko-mono/blob/437763a729bbf02cbf588559a20cc354f19b1677/packages/protocol/contracts/L1/IProver.sol#L13](https://github.com/taikoxyz/taiko-mono/blob/437763a729bbf02cbf588559a20cc354f19b1677/packages/protocol/contracts/L1/IProver.sol#L13)

```solidity
// Import necessary libraries and interfaces
import "./IProver.sol";

// Define the ProverPool contract
contract ProverPool is IProver {

    // ERC-20 address of the payment token
    address ERC20TokenAddress;

    // Implement the onBlockAssigned function
    function onBlockAssigned(
        uint64 blockId,
        TaikoData.BlockMetadataInput calldata input,
        TaikoData.ProverAssignment calldata assignment
    ) external {
        // Decode the assignment data to retrieve signatures and other information
        (bytes memory proverSignature, uint256 tokenAmount) = decodeAssignmentData(assignment);

        // 1. Verify the prover signature is valid (off-chain verification)
        require(isValidSignature(proverSignature, input), "Invalid prover signature");

        // 2. Execute the transfer transaction
        ERC20(ERC20TokenAddress).transferFrom(tx.origin, address(this), tokenAmount);

        // Additional logic goes here
    }

    // Implement functions to decode assignment data, verify signature, etc.
}
```

## 区块证明权的竞争

Taiko 网络中 prover通过拍卖获取一串blocks的证明权，

1. 区块证明权的初始价格为：s=2*p 其中p是过去几个块价格的加权平均。并且初始拍卖价格会控制在一个合理波动范围内
2. 每个prover竞拍钱需要充值 s * max_block_gas_limit * num_blocks * 1.5 如果不能在承诺时间内提供合法证明那么拍卖的代币将被 burn掉，如果能够在约定时间内提供合法证明则相关支出将被退回
3. 系统仍会从充值的token数量，平均proof生成延迟时间，赢得证明权的区块收益率等多个维度对prover打分，来平衡单一prover在系统垄断证明权的问题

## L3 扩展

![L3](/images/2023-09-30-l3.png)

L2->L3 的扩展与 L1->L2 的扩展几乎是一样的，但是L2看上去更像是一个可以独立工作的链，即 Taiko 链，但是 L3 更多的是在某个具体应用方面的扩展

## Proposing Taiko blocks



