- tags: [python](/tags.md#python)
- date: 2018-07-17

# Effective Py - Miscellaneous

Now you may know the main keypoints of the python development. We will talk about some miscellaneous in python practice. Including concurrecy & parallelism, build-in modules, and collaboration, production.

## Concurrency and Parallelim

Concurrency is when computer does many different things seeming at the same time. Parallelism is actually doing many different things at the same time.

- **Use subprocess to Manage Child Processes**

Python has many libraries for running and managing child processes. The best and simplest choice for managing child processes is to use the `subprocess` build-in module. The `Popen` constructor starts the process. The `communicate` method reads the child process's output and wait for ternimination.

```python
import subprocess
proc = subprocess.Popen(['sleep', '0.3'])
while proc.poll() is None:
    print('working...')
print('Exit Status: ', proc.poll())
#working...
#working...
#...
#Exit Status:  0

```

Use subprocess module to run child processes in parallel and manage their input and output. Use	`timeout` parameter with `communicate` to avoid deadlocks.

- **Use Threads for Blocking I/O, Avoid for Parallelism**

The standard implementation of Python, CPython, enforces coherence with a mechanism call Global Interpreter Lock (GIL). The GIL prevents CPython from being affected by preemptive multithreading. It means that python threads can't run bytecode in parallel.

There are ways to get CPython to utilize multiple cores, but it doesn't work with the standard `Thread` class. But for blocking I/O tasks, Python can run seemingly in parallel. Because python use system calls, which interacting with external environment, rather block GIL.

- **Use Lock to Prevent Data Races in Threads**

Though GIL here, but it will not protect you. You're still responsible for protecting against data races between the threads in your programs. Your programs will corrupt their data stuctures if you allow multiple threads to modify the same objects without locks. `Lock` in `Thread` build-in module is the standard mutual exclusion lock implementation.

- **Use Queue to Coordinate Work Between Threads**

The `Queue` class in `queue` build-in module provides all of the functions you need to solve the problems. But you need also be aware of the many problems in building concurrent piplines: busy waiting, stopping workers, and memory explosion.

- **Consider Coroutines to Run Many Functions**

There're 3 big problems with threads.

1. require special tools to coordinate.
2. Threads require a lot of memory, about 8 MB per executing thread.
3. Threads are costly to start.

You can use coroutines to work around all these issues. They're implemented as an extension to generators. The cost of starting a generator is less than 1KB of memory.

```python
def my_coroutine():
    while True:
        received = yield
        print(received)

it = my_coroutine()
next(it)
it.send('a')
it.send('b')
#a
#b

```

Syntax in python2 seems not so elegant. you need to include an additional loop at the delegation point.

- **Consider concurrent.futures for True Parallelism**

`concurrent.futures` module provide `ThreadPollExecutor` and `ProcessPollExecutor` class. The advanced parts of the `multiprocessing` module should be avoid because they are so complex.

## Build-in Modules

- **Define Function Decorators with functools.wraps**

Use `functools.wraps` helpping your handle with some meta information of functions like `func.__name__` and debuggers.

- **Consider contextlib and with Statements for Reusable try/finally Behavior**

You can defining a new class with the sepical method `__enter__`, `__exit__`. But it's too heavy to do this. `contextlib` build-in module provides a `contextmanager` decorator that make it easy to use your own functions in with statements.

- **Use datetime instead of time for Local Clocks**

Avoid using the time module for translating between different time zones. Use the datetime built-in module along with the `pytz` module to reliably convert between times in different time zones. And always represent time in UTC and do covnersions to local time as the final step before presentation.

- **Use Built-in Algorithms and Data Structures**
- Double-ended Queue `deque`
- Ordered Dictionary `OrderedDict`
- Default Dictionary `defaultdict`
- Heap Queue `heapq`
- Bisection `bisect`
- Iterator Tools `help(itertools)`
- **Use decimal When Precision Is Paramout**

## Collaboration and Production

- **Write Docstr for Every Func, Class, Module**
- **Use Packages to Organize Modules and Provide Stable APIs**
- **Define a Root Exception**
- **Know How to Break Circular Dependencies**
- **Use Virtual Environments**
- **Consider Module-Scoped Code to Configure Deployment Environments**
- **Test Everything**
- **Consider Interactive Debugging with pdb**
- **Profile Before Optimizing**
- **User tracemalloc to Understand Memory Usage and Leaks**