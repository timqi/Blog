- tags: [blockchain](/tags.md#blockchain)
- date: 2023-03-11

# Layer0 Layer1 Layer2

ETH 的演化一直以来是区块链行业的一个重要线索，ETH 生态爆发之后他的弊端逐渐显现，提升性能是 ETH 开发中的重要目标。为此开发者提出多链扩容和Rollup的方案，这两个方案也对应了基本的 Layer0、Layer2 的概念。

![Untitled](/images/2023-03-11-1.png)

- **Layer0：模块化区块链；跨链通信**
- **Layer1：一般意义上的公链**
- **Layer2：Layer1 兼容的 Rollup 链**

![Untitled](/images/2023-03-11-2.png)

## Layer0

Layer0 主要是使用 **跨链通信** （注意不是token跨链业务）将区块链的元素模块化，标准化，从而能是把任务并行起来以提高性能的解决办法。跨链通信主要解决多个链之间需要通信的问题。

- LayerZero 项目：[https://layerzero.network](https://layerzero.network/)

[https://layerzeroscan.com](https://layerzeroscan.com/)

```sql
function send(
  uint16 _chainId,                   // the destination chainId
  bytes calldata _destination,       // the destination contract address
  bytes calldata _payload,           // the raw bytes of your payload
  address payable _refundAddress,    // where additional gas is refunded
  address paymentAddr,               // optional
  bytes calldata txParameters        // airdrop native gas
)
```

通常意义上的跨链桥是搭一个中心化的服务监控不同链的区块状态，需要跨链的用户与这个中心化的节点交互，然后节点再不同链上分别处理不同的业务。但是在Layer0里的跨链通信通常是指原因的链与链之间的通信，比如LayerZero协议，它在不同链上分别搭建了节点，需要调用哪个链的能力是直接写在合约代码里的，因而具备各种去中心化优势。

- Cosmos、Celestia

Celestia 早起提出了将区块链数据可用性抽象并复用的模块化方案。通过共识机制来保存数据状态，不参与执行与计算层面的问题。其他开发这就能够以Rollup的形式将计算结果状态同步的 Celestia这个有安全保证的链上进而将数据网络层与计算执行成抽开，相当于做了一个区块链的RDS

Cosmos更近一步，模块化区块链的思路主要是将 网络、共识层、包括应用层的账号、交易、签证这些基础封装并抽取出来，提供一套SDK，开发者可以使用这套SDK实现“一键发链”。然后 Cosmos 提供了多链之间的一个通信协议 IBC使Comos成为一个Hub来同步不同链之间的消息、调用。开发者新开发的链注册到 Comos 的这个生态中即组成了这个大生态。

## Layer1

我们熟知的底层区块链都是Layer1，如 BTC，ETH，BSC 以及APT、AVAX、SOL等；具备通常我们认为的区块链的所有特征

公链本身很依赖开发者生态，用户生态。并不看好新功能具备比ETH更好的生态前景。但是各公链在新技术不断尝试，验证。这些技术的落地效果最终也会影响ETH生态在技术性能上的提升。

- Avalanche

定义了新的共识算法 ，由 Slush、Snowflake、Snowball 和 Avalanche 四个阶段组成，Avalanche系统中有多条子链各自明确的负责不同功能，实现了 4500TPS的性能

- Aptos

Aptos是有Libra团队打造的，使用DiemBFT共识，基于Move生态的区块系统

## Layer2

![Untitled](/images/2023-03-11-3.png)

layer2 的概念基本又回到了 ETH 本身，指以 Rollup 的方式将计算的最终状态比如某个地址余额多少币 存储在 ETH 链上，从而释放了二层链上的计算性能，也在一层链上保障链安全性。

### Optimistic Rollups

乐观Rollup即如其名，假设二层链上计算的结果是正确的，数据Rollup到Layer1 的时候有一个冻结期，这期间每个人都可以公开验证Rollup的数据是否计算正确了，如果发现计算结果错误那么将对相应的计算节点做惩罚。冻结期内无法转币，也就以为着ETH从二层转到一的层的时候不是即时到账的。

OP **的工作逻辑** 

- CanonicalTransactionChain (CTC) 合约作为Rollup数据存储，每隔几十秒就会有来着二层的数据提交过来以待验证
- 区块生成主要由sequencer执行，没有mempool不涉及交易排序，实时处理用户的交易成功或拒绝，sequencer是一个相对非常中心化的服务
- 用户可以跨过sequencer使用ETH交易直接向CTC提交一层数据，但是手续费较高

[https://etherscan.io/address/0x5e4e65926ba27467555eb562121fac00d24e9dd2](https://etherscan.io/address/0x5e4e65926ba27467555eb562121fac00d24e9dd2)

### zk Rollups

通过严谨的数学逻辑以很低的成本快速保证二层网络传来的数据一定是对的，或者错误。zk算发的具体过程过于复杂，可以参考 下面文章，这里就不过多赘述。

[2022.09.04 zk-SNARKs 证明过程](2022%2009%2004%20zk-SNARKs%20%E8%AF%81%E6%98%8E%E8%BF%87%E7%A8%8B%2027578037eb3f401b8b8eb015e6beeca1.md)

相比 Optimise Rollups，zk在逻辑上是更完备的，并且有理论支撑其正确性，所以从二层回传到一层的状态可以即时同步到一层上，也就是说从zk的二层转币回来可以即时到账。但是缺点就是由于zk的计算量之大性能相比op更差一点。

## ETH 分片

![Untitled](/images/2023-03-11-4.png)

ETH 2.0 本身也定义了自身扩容方案，即分片

- beacon 链实现了 PoS 逻辑，并验证执行层（原ETH主链、Geth）的计算是否正确
- 为提高数据可用性，代码可用性 ETH将先行数据分为 64 片，运行在每一片上的 validator 不用需要存储其他片的数据，但是他们可以通过协议获取其他分片的数据