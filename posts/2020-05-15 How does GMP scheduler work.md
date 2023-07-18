- tags: [golang](/tags.md#golang)
- date: 2020-05-15

# How does GMP scheduler work

As we know that There is a runtime when Golang running. The runtime perform the scheduled tasks(goroutine) in user space rather than kernel, so it's more lightweight. It do a better tradeoff between system resource usage and performance, especially in IO tasks. In this article, I'll show you Golang scheduler's history, Goroutine scheduler GMP's design pattern, and some cases how does GMP handle.

We know why we need a scheduler in [previous article](/2020/05/14/why-we-need-scheduler/). And GM pattern also have a bad performance, to fix this problem, a GMP pattern introduced into golang.

## GMP Pattern

- **G**: goroutine
- **M**: thread, running in process kernel space
- **P**: processor, a queued goroutines

In this pattern, threads are the physical workers, scheduler should dispatch goroutines to one thread.

![GMP Pattern](/images/2020-05-15-1.jpeg)

GMP Pattern

1. **global queue**: goroutines to be executed.
2. **P, the local queue**: like the global queue, it contains goroutines to be executed; But this queue have a **max capacity 256**. It will post half of total goroutines to global queue when the local is full; And finally, Goroutine G' created by G will be queued in the same one to ensure local relation
3. **P's list**: all P's list will be created once `GOMAXPROCS` value is determined
4. **M**: running thread should acquire tasks from P's local queue, if it's empty, M will fetch goroutines from global queue to P's local or fetch from other P's queue. G is running in M, it will keep pull a new G when task will finish

**Goroutine scheduler and OS scheduler are connected using M, every M is a physical OS thread, OS scheduler dispatch M running in a real CPU core.**

## Numbers of M & P

### Numbers of P:

Determined by `GOMAXPROCS` environment variable or `GOMAXPROCS()` function in runtime package. That means there are GOMAXPROCS goroutines run concurrent at any time.

### Numbers of M:

- The max limit threads supported in golang is 10000, but OS can't create so many threads usually. So we can ignore this limitation.
- `SetMaxThreads()` function in runtime/debug package can setup the max threads count.
- **It will create a new thread once current one is blocked**.

M & P's number have no relationships. P's goroutine will run in other M or create a new M once current M is blocked. So there may be too many M even if P's number is 1.

## When to create P, M

P: After numbers of P is determined, it will be created by runtime.

M: If there are not enough M to execute P's tasks, it will be created. e.g. all M are blocked, new M will be created to run P's task

## Scheduler's Strategy

Reuse: reuse threads to avoid create,destroy thread frequently.

1. Work Stealing: steal G from P bind by other M when there are no G to run, rather destroy
2. Hand Off: transfer P to other free M when it is blocked

Concurrency: There are at more GOMAXPROCS goroutines run simultaneously. But it also set the limitation of concurrency if GOMACPROCS < CPU Cores.

Preemptive: coroutine must give up cpu time proactive. But in golang, A goroutine can be run 10ms at most each time to avoid other goroutines are hungry.

Global Goroutines Queue: M can pull goroutines from global queue when work stealing failed.

## What happened after go func(){}

![2020 05 15 How does GMP scheduler work [golang] 6d9703d4981f40559b885a50dd41e8c6/2020-05-15-2.jpeg](/images/2020-05-15-2.jpeg)

1. Create a goroutine by go func() {}.
2. There are two queues can store the G, local queue is a better choice, but if the local is full, G will be posted to global queue.
3. G must run in M, each M correspond to one P, M will pull goroutine from this P when tasks done. It will steal from other M's P or global queue if the local P is empty.
4. M keeps running to execute goroutines
5. When M is blocked, Golang will detach it from P, and run Gs in other free M or create a new one.
6. When M is resumed, T G trigger blocking, will try to fetch an free P, if no P is free, M will sleep and G will be posted to global queue.

## Lifecycle

![lifecycle](/images/2020-05-15-3.png)

lifecycle

M0: M0 is the first thread created, reference by `runtime.m0`, It do the system initial and start first G, then M0 turns to normal M, like others.

G0: G0 is the first created when M started. G0 is only used to scheduling other Gs. Every M has it's own G0, G0's memory stack is used when do system call or goroutine scheduling. the Global variable `G0` is the M0's G0.

```go
package main
import "fmt"

func main() {
    fmt.Println("Hello world")
}

```

code above will trigger workflows:

1. runtime create M0,G0 and bind
2. Scheduler init: initial M0, stack, Garbage Collection, Create and initial `GOMAXPROCS` P list
3. main function in code above is `main.main`, the `runtime.main` will invoke `main.main`, create goroutine (just called main goroutine) and push it to P's local queue.
4. start M0, M0 had bind to P, so it can get main goroutine
5. M0 set the run environment according to goroutine's stack & scheduling information
6. run G in M
7. G exist, M pull Gs util `main.main` exit, `runtime.main` will invoke Defer & Panic, finally `runtime.exit` will be invoked