---
title: 我看推荐算法
category: tech
---

本文展示了作为公司内部分享的有关推荐算法的一些观点，可能大多数情况下一个简单的推荐模型才是我们更想要的。在前期初创阶段与其花大力气搞推荐系统不如思考一下当年 Twitter 的核心算法：
<!--more-->

```sql
SELECT * FROM tweets
WHERE user_id IN
  (SELECT source_id
   FROM followers
   WHERE destination_id = ?)
ORDER BY created_at DESC
LIMIT 20
```

<object data="/i/2016-06-22-recommendaion-algorithm.pdf" type="application/pdf" width="100%" height="550px">
<a href="/i/2016-06-22-recommendaion-algorithm.pdf">recommendaion-algorithm.pdf</a>
</object>
