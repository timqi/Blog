---
title: Lock in Golang
category: golang
---

Golang recommends using channel to do communicating between goroutines. The idea of channel comes from data flow. But in some scenarios, using  channel is too heavy to implement, mutex is a better solution.  There are two kinds of locks in Golang, `sync.Mutex`,`sync.RWMutex`. The difference between Mutex and RWMutex is that RWMutex is a reader/writer mutual exclusion lock, the lock can be held by an arbitrary number of readers or a single writer, readers don't have to wait for each other, They only have to wait for writers holding the lock.
<!--more-->

**Lock()**: only one go routine read/write at a time by acquiring the lock.

**RLock()**: multiple go routine can read(not write) at a time by acquiring the lock.

```golang
package main

import (
    "fmt"
    "sync"
    "time"
)

func main() {

    a := 0

    lock := sync.RWMutex{}

    for i := 1; i < 10; i++ {
        go func(i int) {
            lock.Lock()
            fmt.Printf("Lock: from go routine %d: a = %d\n",i, a)
            time.Sleep(time.Second)
            lock.Unlock()
        }(i)
    }

    b := 0

    for i := 11; i < 20; i++ {
        go func(i int) {
            lock.RLock()
            fmt.Printf("RLock: from go routine %d: b = %d\n",i, b)
            time.Sleep(time.Second)
            lock.RUnlock()
        }(i)
    }

    <-time.After(time.Second*10)
}
```

## Q&A

1. When a go-routine has already acquired a RLock(), can another go-routine acquire a Lock() for write or it has to wait until RUnlock() happens?

> To acquire a Lock() for write it has to wait until RUnlock()

2. What happens when someone already acquired Lock() for map ,will other go-routine can still get RLock()

> if someone X already acquired Lock(), then other go-routine to get RLock() will have to wait until X release lock (Unlock())

3. Assuming we are dealing with Maps here, is there any possibility of "concurrent read/write of Map" error can come?

> Map is not thread safe. so "concurrent read/write of Map" can cause error.
> See following example for more clarification:

```golang
package main

import (
    "fmt"
    "sync"
    "time"
)

func main() {
    lock := sync.RWMutex{}

    b := map[string]int{}
    b["0"] = 0

    go func(i int) {
        lock.RLock()
        fmt.Printf("RLock: from go routine %d: b = %d\n",i, b["0"])
        time.Sleep(time.Second*3)
        fmt.Printf("RLock: from go routine %d: lock released\n",i)
        lock.RUnlock()
    }(1)

    go func(i int) {
        lock.Lock()
        b["2"] = i
        fmt.Printf("Lock: from go routine %d: b = %d\n",i, b["2"])
        time.Sleep(time.Second*3)
        fmt.Printf("Lock: from go routine %d: lock released\n",i)
        lock.Unlock()
    }(2)

    <-time.After(time.Second*8)

    fmt.Println("*************************************8")

    go func(i int) {
        lock.Lock()
        b["3"] = i
        fmt.Printf("Lock: from go routine %d: b = %d\n",i, b["3"])
        time.Sleep(time.Second*3)
        fmt.Printf("Lock: from go routine %d: lock released\n",i)
        lock.Unlock()
    }(3)

    go func(i int) {
        lock.RLock()
        fmt.Printf("RLock: from go routine %d: b = %d\n",i, b["3"])
        time.Sleep(time.Second*3)
        fmt.Printf("RLock: from go routine %d: lock released\n",i)
        lock.RUnlock()
    }(4)

    <-time.After(time.Second*8)
}
```

## Concurrent safe about map

Before Golang 1.6, concurrent read is OK, concurrent write is not OK, but write and concurrent read is OK. Since Golang 1.6, map cannot be read when it's being written. So After Golang 1.6, concurrent access map should be like:

```golang
package main

import (
    "sync"
    "time"
)

var m = map[string]int{"a": 1}
var lock = sync.RWMutex{}

func main() {
    go Read()
    time.Sleep(1 * time.Second)
    go Write()
    time.Sleep(1 * time.Minute)
}

func Read() {
    for {
        read()
    }
}

func Write() {
    for {
        write()
    }
}

func read() {
    lock.RLock()
    defer lock.RUnlock()
    _ = m["a"]
}

func write() {
    lock.Lock()
    defer lock.Unlock()
    m["b"] = 2
}
```