- tags: [golang](/tags.md#golang)
- date: 2020-06-11

# Memory Management in Golang

Golang's memory management model is based upon tcmalloc pattern. TCMalloc is Google's customized implementation of c's `malloc` and c++'s `operator new` used for memory allocation within c or c++ code. We know that `malloc` invoked will trigger threads switch into kernel space, it's a big consumption. So TCMalloc provide thread cache capability to enhance the performance. In golang, the local cache is not specify to thread, but P, processors in GMP schedule Model.

To make a high performance memory manage system, what functions do we need to ensure efficient?

- memory pool: to avoid switch thread context between kernel space and user space
- GC: dynamic and automatic garbage collection to make memory reuse
- lock: synchronize the different process contexts ensure the correctness of program

## Small allocation module

There are 3 types of memory manager: `mcache`,`mcentral`,`mheap` in Golang. They are implemented based on the GMP pattern, introduced before, to provide high performance feature. Objects, little that 32 kb is allocated from mcentral, greater than 32 kb is rounded up to page size, and page is directly allocated from heap.

## mcache

mcache is bind to `P` in GMP pattern. It means that mcache is used for every goroutine to allocate memory. It handles a list of span(memory chunk of 32kb), called `mspan`, that contains the memory available for allocation:

![allocation with mcache](/images/2020-06-11-1.png)

allocation with mcache

There is no lock in mcache struct, because every P is bound separated and every P only handle for one goroutine at a time, and memory access is isolated. Using this local cache does not require lock and makes the allocation more efficient

**span**

The span list is divided into about 70 size classes. from 8 bytes to 32k bytes. Each span exists twice: one list is for objects that contain pointer and the other one is not contains pointer. **This distinction will make the life of the garbage collector easier since it will not have to scan the spans that do not contains any pointer**.

![span size of classes](/images/2020-06-11-2.png)

span size of classes

## mcentral

If we need allocate an object of 32 bytes. the allocator will find the span with size of 32 bytes and fit the object in the 32 bytes span:

![fit in the 32 bytes span](/images/2020-06-11-3.png)

fit in the 32 bytes span

Now you must wonder what will happen if the span does not have a free slot during the allocation. Go maintains central list of spans per size classes, named `mcentral`, with the spans that contain free objects and the one that do not:

![central list of spans](/images/2020-06-11-4.png)

central list of spans

`mcentral` maintains a double linked list of spans. Each of them has a reference to previous span and next span. A span in non-empty list means that there at least one slot is free in the list allocation, even some slot is in-use already. Indeed, when the garbage collector sweeps the memory, it could clean a part of the span, the part that marked as not used anymore, and also, the span will be put back to the non-empty list.

Program can request a span from the central list if it run out of slot.

![span replacement from mcentral](/images/2020-06-11-5.png)

span replacement from mcentral

## Allocate from HEAP

And now, go needs a way to get new spaces to the central list if none are available in the empty list. New spans will be allocated from the heap and linked to central list:

![span allocation from the heap](/images/2020-06-11-6.png)

span allocation from the heap

The heap pulls the memory from the OS if needed. The heap will pull a large chunk of memory, named `arena`. It is 64MB in the 64-bits architectures and 4MB in most of the other architectures. The arena also maps the memory page with the spans.

## Large Allocation

Large object, greater than 32 KB, is not allocated in local cache. They are rounded up to the page size and the page allocation is directly in the heap.

![large allocation directly from the heap](/images/2020-06-11-7.png)

large allocation directly from the heap

## Overview

Now we can draw a big picture of what happening at a high level during the memory allocation:

![components of the memory allocation](/images/2020-06-11-8.png)

components of the memory allocation