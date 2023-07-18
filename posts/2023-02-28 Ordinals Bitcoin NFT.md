- tags: [blockchain](/tags.md#blockchain)
- date: 2023-02-28

# Ordinals Bitcoin NFT

Bitcoin 大多数情况下我们认为是同质化的，也就是说这个 Bitcoin 和另外一个 Bitcoin 没什么区别，是一样的，等价值的。但是基于 Bitcoin 的 UTXO 记账模式，我们依照一些方法对系统中产生的每一个 Bitcoin Satoshi 编上号，那么两个不同的 sats 就有区别了。这也是 Bitcoin 非同质化的基础。

Ordinals 的核心是定义了一套对 btc 上每一 sats 的描述方法，并且维护了一个追踪每一 sats 从挖出开始的流转索引。并且配套实现了以 sats 为单位的钱包管理；mint、transfer、explorer 等

## 描述方法：

- 整数描述 `[2099994106992659](https://ordinals.com/sat/2099994106992659)` ：按挖出来的每一聪的排序对聪编号
- 浮点描述`[3891094.16797](https://ordinals.com/sat/3891094.16797)`：浮点之前是块高，浮点之后是该块挖出聪的序号
- 维度 `[3°111094′214″16797‴](https://ordinals.com/sat/3%C2%B0111094%E2%80%B2214%E2%80%B316797%E2%80%B4)`：

```sql
A°B′C″D‴
│ │ │ ╰─ Index of sat in the block
│ │ ╰─── Index of block in difficulty adjustment period
│ ╰───── Index of block in halving epoch
╰─────── Cycle, numbered starting from 0
```

- 供应的百分比`[99.99971949060254%](https://ordinals.com/sat/99.99971949060254%25)`：btc总供应量的百分比

BIP 介绍：[https://github.com/casey/ord/blob/master/bip.mediawiki](https://github.com/casey/ord/blob/master/bip.mediawiki)

## Inscriptions**/Mint**

铭刻一件艺术品（NFT）就是将特定的 sats 与艺术品的文件内容绑定，然后把这个 sats 存储到 UTXOs 中，ord 钱包会根据 ordinals 描述方法将特定的 sats 转出到目标地址。铭刻的内容是完全存储在链上的，艺术品本身有 MIME Type 和 Content，这部分数据用 Taproot 脚本存储在 Wintness 部分，并且可以享受存储优惠。

由于 Taproot 交易只能花 Taproot 的 Outputs，所有 Inscriptions 分为两个阶段 commit/reveal。在 commit 交易中，创建包含艺术品内容的 Output；在 reveal 交易中，只有使用该艺术品的文件内容才能解锁，把之前创建的包含艺术品内容的 Output 花掉。通常我们认为艺术品存储在 Output 的第一个 sats 中。艺术品文件内容本身的序列化方法为：

```sql
OP_FALSE
OP_IF
  OP_PUSH "ord"
  OP_1
  OP_PUSH "text/plain;charset=utf-8"
  OP_0
  OP_PUSH "Hello, world!"
OP_ENDIF
```

### 例子：

以 Bitcoin Punks 为例：[https://ordinals.com/inscription/38b0816a368284d8fa6e669b173956d29db733ddae9b8eb18291dc11958b88e3i0](https://ordinals.com/inscription/38b0816a368284d8fa6e669b173956d29db733ddae9b8eb18291dc11958b88e3i0) 

![Untitled](/images/2023-02-28-1.png)

Reveal TXID 是 `38b0816a368284d8fa6e669b173956d29db733ddae9b8eb18291dc11958b88e3`  

![Untitled](/images/2023-02-28-2.png)

艺术品的ID 为 `38b0816a368284d8fa6e669b173956d29db733ddae9b8eb18291dc11958b88e3i0` . 也就是 TXIDi0，在这个 Tx Output 中的第一个 sats

## 问题

Ord索引存储占用非常大，而且索引将成的速度非常慢，当前块高778648

![Untitled](/images/2023-02-28-3.png)