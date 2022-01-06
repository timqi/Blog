---
title: 动态存储管理(续)
category: algorithm
---

[动态存储管理](/2013/10/25/dynamic-memory-management)

## 4. 伙伴系统

**伙伴系统**使操作系统的另一种动态存储管理方法。它和边界表示法类似，在用户提出申请使时，分配一块大小恰当的内存区给用户；反之在用户释放内存区时即回收。所不同的使：在伙伴系统中，无论使占用块还是空闲块其大小均为`2的k次方`。

### 4.1 可利用空间表结构

``` c++
#define m 16
typedef struct WORD_b {
<!--more-->
	WORD_b	*llink;
	int tag;
	int kval;
	WORD_b	*rlink;
	OtherType other;
} WORD_b, head; //内存字类型，节点的第一个字页称为head
typedef struct HeadNode {
	int nodesize;
	WORD_b	*first;
} FreeList[m+1];
```

### 4.2 分配算法

``` c++
WORD_b* alloc_buddy (FreeList &avail, int n) {
	// avail[0..m]为可利用空间表，n为申请分配量，若有不小于n的空闲块，
	// 则分配相应的存储块，并返回其首地址；否则返回NULL
	WORD_b *pa, *pre, *suc, *pi;
		// 查找满足分配要求的子表
	for (int k = 0; k <= m && (!avail[k].first || avail[k].nodesize<n+1); ++k);
	if (k > m) return NULL;                  // 分配失败，返回NULL
	else {                                 // 进行分配
		pa = avail[k].first;                 // 指向可分配子表的第一个结点
		pre = pa->llink;   suc = pa->rlink;  // 分别指向前驱和后继
		if (pa == suc) avail[k].first = NULL;  // 分配后该子表变成空表
	else {                               // 从子表删去*pa结点
		pre->rlink = suc;   suc->llink = pre;   avail[k].first = suc;
	}
 	for (int i=1;  avail[k-i].nodesize>=n+1;  ++i) {
		pi = pa+(int)pow(2, (k-i));  pi->rlink = pi;  pi->llink = pi;
		pi->tag = 0;  pi->kval = k-i;  avail[k-i].first = pi;
	}   // 将剩余块插入相应子表
		pa->tag = 1;  pa->kval = k-(--i);
	}
	return pa;
}
```

### 4.3 回收算法

内存回收时同样有一个相邻的空闲块归并成大块的问题。但是在伙伴系统中仅考虑护卫**伙伴**的两个空闲块的归并。

> **伙伴**：在分配时经常需要将一个大的空间块分裂成两个大小相等的存储区。这两个有统一个大块分裂出来的小块就称之为**互为伙伴**。例如起使地址p，大小2^k的内存块，其伙伴块的起始地址为：buddy(p,k) = `p+2^k`(若 p MOD 2^k+1 =0) 或 `p-2^k`(若p MOD 2^k+1 =2^k)

**伙伴系统的有点是算法简单，速度快；缺点是由于只归并伙伴而容易产生碎片**

## 5. 无用单元收集

本节讨论广义表节点的释放回收问题，解决这个问题有两条途径：

- 使用访问计数器：在所有字表或广义表上增加一个表头节点，并设立一个**计数域**，它的值为指向该子表或广义表的指针数目，只有当该值为0时，此子表才从广义表中释放
- 收集无用单元：程序运行过程中无论节点是否有用，系统均不对它进行回收，直到整个可以用空间表为空。此时中断执行程序，将不被使用的节点连成链表，而后开始执行程序

由此，收集无用单元分两部：

- 对无用单元加标志
- 对整个空间扫描，标志为0的节点连为链表

对上述的第一步标志的进行时极其困难的，我们讨论3种标志算法:

- 递归算法：遍历广义表即可，但是它需要的存储空间非常大很可能由于递归栈溢出造成内存泄漏
- 非递归算法：手动做栈进行广义表遍历，以避免内存泄漏
- 利用表节点本身的指针域标记遍历路径算法

第3种算法如下：

``` c++
void mark_list(GList GL) {
	// 遍历非空广义表GL(GL!=NULL且GL->mark==0)，
	// 对表中所有未加标志的结点加标志
	GList q = NULL, p = GL, t = NULL;  // t指示p的母表
	int finished = FALSE;
	while (!finished) {
		while (p->mark==0) {
			p->mark = 1;
			// MarkHead(p)的细化：
			q = p->ptr.hp;   // q指向*p的表头
			if (q && q->mark==0) {
				if (q->tag==ATOM) q->mark = 1;   // ATOM，表头为原子结点
 				else { //继续遍历子表
					p->ptr.hp = t;  p->tag = ATOM;  t = p;  p = q;
				}
			}
		}  // 完成对表头的标志
		q = p->ptr.tp;    // q指向*p的表尾
		if (q && q->mark==0) {   // 继续遍历表尾
			p->ptr.tp = t;  t = p;  p = q;
		} else {  // BackTrack(finished)的细化：
			while (t && t->tag==LIST) {  // LIST，表结点，从表尾回溯
			q = t;   t = q->ptr.tp;   q->ptr.tp = p;   p = q;
			}
			if (!t) finished = TRUE;   // 结束
			else {  // 从表头回溯
				q = t;   t = q->ptr.hp;   q->ptr.hp = p;
				p = q;   p->tag = LIST;
			}  // 继续遍历表尾
		}
	}
}
```

**比较上述3种算法各有利弊，第3种算法在标志时不需要附加存储，使动态空间得到充分利用，但由于在算法中每个指针的作用要改变两次因此开销相当大，而且一旦中断则导致系统瘫痪无法重新启动。而非递归算法操作简单，时间上省得多，但是然而它需要占用一定的动态空间，使动态分配所用的存储量减少**

## 5. 存储紧缩

在使用**堆**（空闲块为一段连续的地址）的系统中，由于系统的可利用空间始终是一个地址连续的存储块，因此回收时必须将所释放的空闲块合并到整个对上去才能重新使用，这就是**存储紧缩**的任务。

通常有两种做法：

- 一旦有用户释放空间即进行存储紧缩
- 直到可利用空间不够的时侯才进行存储紧缩

为实现存储紧缩首先要对占用块进行**标志**，标志算法和上节相同，其次需要进行一下4步：

1. 计算占用块的新地址
2. 修改用户的初始向量表，以便进行存储紧缩后用户的程序还能够运行
3. 检查每个占用块中存储的数据，若有指向其他存储块的指针，则需做相应更改
4. 将所有占用块迁移到新地址去，这实质上使作数据传送
