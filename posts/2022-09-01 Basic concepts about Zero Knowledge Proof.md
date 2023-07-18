- tags: [blockchain](/tags.md#blockchain)
- date: 2022-09-01

# Basic concepts about Zero Knowledge Proof

This post is aimed at introducing some basic words about `Zero Knowledge Proof` . I will try to answer some basic questions in ZKP(zero knowledge proof) field to help you understand what ZKP is.

There are two roles. One is prover, and the other is the verifier. If there is a way for prover to convince the verifier that a statement about some secret information is true without revealing the secret itself, it may be interactive or non-interactive through the process. We call the proof protocol is a ZKP.

Suggest that these is a puffin in penguins. How cloud tell where the puffin is without specify the exact position. You can leave a hole in the wall. The verifier looks back from the front. And the prover should show the puffin behind the hole. So you cloud get the prover really know where the puffin is without specify the exact position of puffin.

![Untitled](/images/2022-09-01-1.png)

![Untitled](/images/2022-09-01-2.png)

![Untitled](/images/2022-09-01-3.png)

Suggest that you have a web application which has user should do login using username and password, but won’t send you origin password. So users can do a hash of password and send to server, server will also do a hash of origin password. Then you can verify the user know the password without send raw password.

## What are the applications of zero knowledge proof

- Confidential transactions on blockchains. transaction data is encrypted and a proof posted to prove it was computed correctly
- Performance optimizations for distributed application on blockchains.(i.e. ETH smart contracts) application code is executed off-chain, or by a a single node, and only a proof for its correct execution is posted to the blockchain for other parties to verify its correctness.
- Zero knowledge identity. [https://www.uport.me](https://www.uport.me/)
- Privacy-preserving verification. A borrower(prover) produces zero knowledge proof to a credit provider(verifier) that he is credit worthy without providing access to private financial records.

## A**lgorithms**

The current stats of zero knowledge algorithms

|  | Trusted Setup | Speed
(Verifier+Prover) | Proof Size | Quantum
Resistant |
| --- | --- | --- | --- | --- |
| zk-SNARKs | Yes | Middle | Smallest | No |
| zk-STARKs | No | Fastest | Biggest | Yes |
| Bulletproofs | No | Slowest | Middle | No |

## History of development

- 1985, ZKP was first proposed by S. Goldwasser, S. Micali and C. Rackoff.
- 2010, Groth implemented the first omnipotent, constant-size, non-interactive ZKP protocol based on elliptic curve bilinear mapping. Later, after continuous optimization, this protocol eventually became the famous zk-SNARKs  in the blockchain.
- 2013, the Pinocchio protocol realized minute-level proof, millisecond-level verification, and the proof size was less than 300 bytes, bringing ZKP from theroy to applicatoin. The SNARKs used by zcash later based on an improved version of Pinocchio.
- 2014, the cryptocurrency called Zerocash used a special ZKP tool zk-SNARKs to completely hide the transaction amount and both parties, focusing more on privacy, and control over transparency of transactions.
- 2017, the Zerocash team proposed a scheme to combine zk-SNARKs with smart contracts, so that transactions can be hidden in plain sight and create privacy-protecting smart contracts.

## Tools

- https://github.com/scipr-lab/libsnark,

libsnark is an open source C++ library, developed by SCIPR LAB. Coauthors who participated in several zk-SNARKs papers. libsnark has implemented several methods in papers of recent years, the most commonly used ones include BCTV14a and Groth16. Starting with the application in the anonymous digital currency Zcash, libsnark has laid the foundation for ZKP from theroretical research to large-scale engineering applications.

- https://github.com/zkcrypto/bellman

Developed by Zcash team. bellman is a rustlang library and has many improvements based on libsnark. It had implemented Groth16 algorithm in related papers, and bellman is mainly used in Zcash project.

- https://github.com/Zokrates/ZoKrates

ZoKrates is a toolbox for zkSNARKs on Ethereum. It helps you use verifiable computation in your DApp, from the specification of your program in a high level language to generating proofs of computation to verifying those proofs in Solidity.