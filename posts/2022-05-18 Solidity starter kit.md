- tags: [blockchain](/tags.md#blockchain)
- date: 2022-05-18

# Solidity starter kit

- truffle, nodejs based toolsuite for development [https://trufflesuite.com/docs/](https://trufflesuite.com/docs/)
- gananche, personal ethereum chain for testing [https://trufflesuite.com/ganache/](https://trufflesuite.com/ganache/)
- solidity [https://docs.soliditylang.org/en/v0.8.14/contracts.html](https://docs.soliditylang.org/en/v0.8.14/contracts.html)
- openzeppelin [https://github.com/OpenZeppelin/openzeppelin-contracts](https://github.com/OpenZeppelin/openzeppelin-contracts)

```jsx
npm i -g truffle
truffle init
npm init
npm i -s @openzeppelin/contracts
```

# Truffle Config

[https://trufflesuite.com/docs/truffle/reference/configuration](https://trufflesuite.com/docs/truffle/reference/configuration) 

To config truffle, `truffle-config.js` is created by `truffle init`, along with initial contract Migrations.sol, There are some commons settings 

- networks: used by truffle deploy(migrate),console commands. should specify `--network {networkKey}` argument to use the exact network config. if no argument is provided, `development` will be used by default.
- console: used by truffle console/develop, to define variable injected to console mode
- dashboard: define the host, port… used for `truffle dashboard`. It will start a webpage and let you sign transactions using metamask rather the raw privatekey or mnemonic
- macha: truffle use mocha as testing framework, so this field is config for mocha related
- compilers: specify which compiler to use to compile

**What’s the difference between `truffle console` and `truffle develop`:**

[https://trufflesuite.com/docs/truffle/getting-started/using-truffle-develop-and-the-console/#why-two-different-consoles](https://trufflesuite.com/docs/truffle/getting-started/using-truffle-develop-and-the-console/#why-two-different-consoles)

- truffle console: a basic interactive console connecting to any Ethereum client
- truffle develop: an interactive console that also spawns a development chain

## Truffle Interactive Console

[https://trufflesuite.com/docs/truffle/getting-started/interacting-with-your-contracts/](https://trufflesuite.com/docs/truffle/getting-started/interacting-with-your-contracts/)

**Differences between transactions and calls**

- calls: won’t cost gas. and return the result immediately
- transactions: will cost gas and can’t get result due to mining process. will return transaction object instead. events emitted should be captured immediately in result’s logs field

**Function call**

After got the contract instance. You can call contract’s method by name directly. Apart from parameters from abi defined. Additional one object argument contains fields such as `from,to,gas,gasPrice,value,data,nonce` can be appended at last position which to specify some onchain infos:

**Create contract instance**

contracts should be migrated manually if in development environment.

1. By deploy one: let instance = await MetaCoin.deployed()
2. By new one: let newInstance = await MetaCoin.new()
3. By address: let specificInstance = await MetaCoin.at("0x1234...");