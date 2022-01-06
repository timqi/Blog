---
title: 后序遍历的非递归算法
category: algorithm
---

树的先序，中序，后序遍历在递归调用中可以很简单的实现。经过对递归调用遍历方法的递归栈分析可以手动对树进行开栈遍历，以避免因树过大而造成的溢出错误。
<!--more-->

在遍历的非递归算法中先序与中序不需要保存递归的入口信息即可实现。而在后序遍历中，由于需要分别查看左右子节点的信息后才能决定是否能访问根节点数据，因此需要**在栈中保存遍历的入口信息**。首先给出树的定义

``` c++
typedef struct BiTNode {
    TElemType data;
    struct BiTNode *lchild, *rchild;
} BiTNode, *BiTree;
```


## 递归遍历方法

我们先给出先序遍历的源代码

``` c++
Status pre_oder_traverse(BiTree t, Status (* visit)(TElemType e) )
{
    if(t) {
        if( visit(t->data) )
            if( pre_oder_traverse(t->lchild, visit) )
                if(pre_oder_traverse(t->rchild, visit))
                    return done;
        return ERROR;
    }
    return done;
}
```

先序遍历是先访问根节点，然后遍历左子树，再遍历右子树。本算法中定义`pre_oder_traverse()`为先序遍历树，首先判断二叉树t是否为空，若空则返回，否则先访问根节点数据，然后先序遍历左子树，再先序遍历有子树。若改为中序，后序只需将3个if语句顺序调整即可。

**可见在递归算法中实现遍历的代码很简单**

## 非递归遍历方法

在给递归遍历方法中要用到`栈`，我们选用`C++ STL`变准模版类型。

### 非递归中序遍历

首先，我们给出相对简单的中序遍历算法。在中序遍历中不需要保存栈相关的入口信息。

``` c++
Status in_oder_traverse(BiTree t, Status (* visit)(TElemType e))
{
    stack<BiTree>s; BiTree p = t;
    s.push(p);
    while( ! s.empty() ) {
        while((p = s.top()) != NULL) {
            s.push(p->lchild);
        }
        s.pop();
        if( ! s.empty() ) {
            p = s.top(); s.pop();
            if( ! visit(p->data) ) err_return("Error at Visit.", ERROR);
            s.push(p->rchild);
        }
    }
    return done;
}
```

`C++ STL`标准模版中定义以下函数

- `s.empty()`:若栈为空则返回true，否则返回false
- `s.push()`:压入操作
- `s.top()`:返回栈顶元素，不弹出
- `s.pop()`:弹出栈顶元素

本算法中先向左遍历至树的左尽头，然后弹出NULL元素。判断栈是否为空，不为空的话访问根节点数据然后再向右遍历。

### 非递归后序遍历

在非递归后序遍历中入栈时我们需要保存栈的入口信息。因此我们为入栈节点做如下定义。

``` c++
typedef enum {L, R} TagType;
typedef struct {
    BiTree ptr;
    TagType tag;
} StackNode;
```

使用`tag`元素保存访问入口信息。后序遍历算法定义如下

``` c++
Status post_oder_traverse(BiTree t, Status (* visit)(TElemType e))
{
    stack<StackNode>s; BiTree p = t;
    StackNode node;

    do {
        while( p != NULL ) {
            node.ptr = p;
            node.tag = L;
            s.push(node);
            p = p->lchild;
        }
        while( ! s.empty() && s.top().tag == R ) {
            node = s.top(); s.pop();
            p = node.ptr;
            if( ! visit(p->data)) err_return("Error at Visit.",ERROR);
        }
        if( ! s.empty() ) {
            s.top().tag = R;
            p = s.top().ptr->rchild;
        }
    }while( ! s.empty() );
}
```

此算法中首先向左遍历至树尽头并在此过程中保存遍历节点的信息为`L`，如果栈非空且栈顶节点的右子节点已访问过则访问其根节点数据。然后判断若栈非空则访问节点的右子节点并且保存tag为`R`。当栈空时则树的所有节点都经过访问。

**非递归遍历是对递归遍历算法的递归栈进行分析后按照相应规则手动模拟递归栈的工作过程，在后序中用到更详尽的栈的信息，因此需要对栈节点再定义**
