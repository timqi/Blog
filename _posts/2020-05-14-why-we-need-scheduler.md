---
title: Why we need a Scheduler
category: golang
---

As we know that There is a runtime when Golang running. The runtime perform the scheduled tasks(goroutine) in user space rather than kernel, so it's more lightweight. It do a better tradeoff between system resource usage and performance, especially in IO tasks. In this article, I'll show you Golang scheduler's history, Goroutine scheduler GMP's design pattern, and some cases how does GMP handle.
<!--more-->

## Single process age

We do not need a scheduler in single process age. all task should be processed serialized. There are obvious shortcomings in this pattern.

1. There only one process, Computer must process tasks one by one. 
2. CPU time will be wasted when process is blocking.

## Multiprocess/Multithread age

To solve the blocking problem, we can make cpu execute other tasks when current process blocking. and also, we create a method, divide cpu time into very small time slice(10ms probably) and run tasks with time limit, to ensure all tasks could be executed. And it seems all tasks running at the same time due to the time slice is very small.

![process scheduling](/i/2020-05-14-1.png)

At the same time, CPU has to handle context switch hold by processes, to create,switch,destroy a process will cost much system resources. So the CPU effective usage rate may be low in high concurrency situation. In linux system, Although threads a more light weight, they are the basic unit of CPU scheduling. Schedule cost is similar to process in principle.

## Coroutine

More process/thread caused other problems

1. high memory usage. 4GB virtual memory will be used per process in 32bit system. And each thread will cost more 4MB at least.
2. high CPU usage when context switch.

Engineers found that most consumption happened in kernel space. We know that a process have "user space" and "kernel space", process will enter kernel space when system call invoke or time slice limit tigger... But from OS's view, do not care which state it is, process controlled by OS using a data structure called `PCB Process Control Block`. We can call code run in kernel space Thread, and call code run in user space `Coroutine`. OS can't see coroutine's working state, it only care about thread or the PCB structure.

![thread coroutine](/i/2020-05-14-2.png)

So to reduce the consumption in kernel space, shall we bind multiple coroutines to one thread? Of course yes. If we add a `schedule layer` between thread and coroutine, to bind N coroutines to one thread, we get a `N:1` pattern. 

**N:1**

In this case, we can do most of jobs in user space rather switch to kernel frequently. But once thread blocked, all coroutine can't work. And multicore CPUs can't run full rate in only one physical thread.

**N:M**

Continue to optimize scheduler, We can bind N coroutines to M physical threads. More complicated scheduler can combine the performance of multithreads and lightweight of coroutines.

![M:N](/i/2020-05-14-3.png)

The difference between thread & coroutine schedule is thread schedule is preemptive, and coroutine is collaborative, coroutine should free the CPU proactive.

## Goroutine

In coroutine mode, developer should release the CPU proactively. This may cause problem when one coroutine hold CPU for a long time, and other coroutine is hungry.

So in golang, scheduler is preemptive, tasks in golang named `goroutine`, communicate to share data by channel. `goroutines can run when other goroutine in the same thread blocked, runtime will help you do the scheduling, you have noting to do.`. It is implemented for multiple concurrency scenery, like multiprocess vs single process. Goroutine retain the advantages of coroutine and have a higher performance.

A goroutine can be setup by only `4KB` memory. It's very lightweight.

## Deprecated goroutine Scheduler

We have already know the relationship between thread and goroutine, the key point here is `The Scheduler`.

Scheduler used now in golang is redesigned in 2012, because there was performance problems, so it is deprecated. Here is a brief introduction to the working principle of this scheduler.

- **G**: Goroutine
- **M**: Machine, thread in kernel space

![GM Scheduler](/i/2020-05-14-4.png)

Use a global queue, It has disadvantages:

1. To create,destroy,schedule a G , M need do a fierce lock competition
2. Transfer G between M will cause more extra consumption. For example, M create a new goroutine G', to execute G', it should be pushed into queue and run in other M', G has relation with G', so the local performance is poor here
3. Frequently system calls cause thread block increase the system consumption

Next article, we will talk about how to improve the model for a better productive performance.