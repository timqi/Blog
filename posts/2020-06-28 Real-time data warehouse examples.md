- tags: [tech](/tags.md#tech)
- date: 2020-06-28

# Real-time data warehouse examples

The concept of data warehouse may be traced back to last century. with the continuous growth of big data and developments of Hadoop ecosystem, offline data warehouse based on Hive/HDFS architect can rise. And recently years, Storm/Spark(Steaming)/Flink etc... real-time frameworks go up and have a rapid development. Every company need a real-time data solution in their system. In this article, we will talk about some typical real-time data architect in Chinese internet companies like Meituan,Netease and OPPO; selections of their storage and computing engines, also with layers division may inspire us in some point.

Four examples:

- Meituan Flink based real-time data warehouse platform
- Yanxuan of Netease Flink based real-time data warehouse in practical
- OPPO real-time data warehouse secrets and offline to real-time smooth migration

## Meituan Flink based real-time data warehouse platform

![2020 06 28 Real-time data warehouse examples [tech 7426cb75c8924229a7c5ec28d418b03b/2020-06-28-1.png](/images/2020-06-28-1.png)

- Lowest layer is design to collect data from different channels like Binlog of mysql, logs printed by server, IoT data... All of these data will be sent into Kafka, they're not only related to real-time computing, but also offline's
- Above the collection is the storage layer. Out of Kafka, there are also HDFS store for status data and Hbase for dimensional data
- And above is the Engines layer. Include Storm/Flink to provide common platform package and component support
- And beyond engine is the platform layer. platform will do the management in data, tasks and resources three dimension
- In the toppest layer is the applications like real-time data warehouse, machine learning, etl and event drive applet

from a functional perspective, Meituan's real-time computing platform contains jobs config\publish\status managements and resource managements. Resource management means multi-tenant resource isolation, delivery and deployment.

### traditional data warehouse model

![2020 06 28 Real-time data warehouse examples [tech 7426cb75c8924229a7c5ec28d418b03b/2020-06-28-2.png](/images/2020-06-28-2.png)

There are always 4 layers from bottom to top. ODS(Operational Data Store), DWD(Data Warehouse Detail), DWS(DWS, Data Warehouse Summary), ADS(ADS，Application Data Store) with Hive or spark for query.

### real-time data warehouse

![2020 06 28 Real-time data warehouse examples [tech 7426cb75c8924229a7c5ec28d418b03b/2020-06-28-3.png](/images/2020-06-28-3.png)

In real-time model, DWD & DWS always based on Kafka. considering of performance, dimensional data are always placed in HBase or Tair KV storage.

### Quasi-real-time data warehouse model

![2020 06 28 Real-time data warehouse examples [tech 7426cb75c8924229a7c5ec28d418b03b/2020-06-28-4.png](/images/2020-06-28-4.png)

Rather than two models above, there is a quasi-real-time model. Its characteristic is not fully based on streamings. They put the detail records in OLAP storage and do analysis with the ability of OLAP

There are 4 main differences between real-time and traditional data warehouse.

1. layer division method. offline system like use more space for time, so the layers is more than real-time system.
2. detail records storage. In offline system, HDFS is always a good choice to store. But in real-time system data are stored in message queue (like Kafka)
3. dimensional data. real-time data warehouse usually use the KV engine
4. data-processing. offline system are always based on Hive,Spark batch processing. And real-time system are mainly based on stream engine like Storm/Flink

## Yanxuan of Netease Flink based system

![2020 06 28 Real-time data warehouse examples [tech 7426cb75c8924229a7c5ec28d418b03b/2020-06-28-5.png](/images/2020-06-28-5.png)

There are different layers from bottom to top. Access layer will collect meta business data like buried point in to message queue. Then the data in the queue is also used for offline on real-time computing. Above the access layer is computing layer founded by Flink. the computed result of Flink is posted to different storage engines like HBase/MySQL/Redis/Kafka depend on different business scenes. So the storage engine is the storage layer above computing. They will provide a universal query entrance and metrics management platform called service layer. And finally, platform is serving for each business system.

In the architect above, Flink, as a real-time computing engine, is important to connect different layers. between ODS -> DWD -> DM, data streamings are all handled by Flink jobs, also with some ETL,union,aggregation operations.

## OPPO's real-time data warehouse smooth upgrade

### an offline warehouse model

![2020 06 28 Real-time data warehouse examples [tech 7426cb75c8924229a7c5ec28d418b03b/2020-06-28-6.png](/images/2020-06-28-6.png)

### real-time model

![2020 06 28 Real-time data warehouse examples [tech 7426cb75c8924229a7c5ec28d418b03b/2020-06-28-7.png](/images/2020-06-28-7.png)

Then a real-time architecture built above on Flink streaming.

### SQL, A unified interface to data

![2020 06 28 Real-time data warehouse examples [tech 7426cb75c8924229a7c5ec28d418b03b/2020-06-28-8.png](/images/2020-06-28-8.png)

Finally, every layer's tool in the data architect become to SQL.

## Reference

- [美团点评基于 Flink 的实时数仓建设实践](https://tech.meituan.com/2018/10/18/meishi-data-flink.html)
- [基于Flink的严选实时数仓实践](https://www.infoq.cn/article/Lrg1J4*tWOak2WLqKyhF)
- [知乎实时数仓实践及架构演进](https://zhuanlan.zhihu.com/p/56807637)
- [OPPO 实时数仓揭秘：从顶层设计实现离线与实时的平滑迁移](https://developer.aliyun.com/article/747830)