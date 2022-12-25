# Executor
Fast execute task with python and less mem ops

## Installation
```bash
pip install thread-executor
```

## Why we need Thread Executor?

Python threading module is a good structure, it helps developers to folk a thread to run some background tasks.
Python have Queue mechanism to connect thread's data.
So what is the problem??

- First, threading module folk threads but python not commit late time. Knowing your thread will run, but don't know when? It's fast with small traffic but when server is high load you will have some problem, high pressure on memory because creating too many threads cause slowness. `waste of time`

- Second, when you create and release threads many times, it'll increase memory and CPUs time of system. Sometime, developers did not handle exceptions and release thread. It can put more pressure to the application. `waste of resource`

## How to resolve problem??

This's my resolver.

- We create `exact` or `dynamic` number of threads. Then using `Job` - a unit bring data information to `Worker` to process. Workers don't need to release, and you only create 1 time or reset it when you update config.

- Job brings 2 importance fields: `func` and `args` and you can call them by `func(*args)` and get all the results and return on `callback` is optional.
- Your app doesn't need to create and release threads continuously
- Easy to access and use when coding.

## Disadvance?

- If you use `callback` then remembered to `add try catch` to handle thread leaked.
- If queue is full you need to wait for available queue slot. set `max_queue_size=0` to avoid this.
- If you restart your app, all the `Job in Queue` that have not been processed will be `lost`.


## Usage : Interface list
```python
send(job: Job) -> None # Push a job to the queue
wait() -> None # wait for all jobs to be completed without blocking each other
scale_up(number_threads: int) -> None # scale up number of threads
scale_down(self, number_threads: int) -> None # scale down number of threads
```

### Initial
```python
from executor.safe_queue import Executor, Job

engine = Executor(number_threads=10, max_queue_size=0)
```
### Send Simple Job
```python
import time

def test_exec(*args, **kwargs):
    time.sleep(3)
    print(args)
    return [1, 2, 3]


def test_exec1(*args, **kwargs):
    print(kwargs)
    time.sleep(2)
    return {"a": 1, "b": 2, "c": 3}

engine.send(Job(func=test_exec, args=(1, 2), kwargs={}, callback=None, block=False))
engine.send(Job(func=test_exec1, args=(), kwargs={"time": 1}, callback=None, block=False))
engine.send(Job(func=test_exec1, args=(), kwargs={}, callback=None, block=False))
engine.send(Job(func=test_exec1, args=(), kwargs={}, callback=None, block=False))
engine.send(Job(func=test_exec1, args=(), kwargs={}, callback=None, block=False))
engine.wait()
```

### Send Job with callback
```python
def call_back(result):
    print(result)
    
for i in range(5):
    engine.send(Job(func=test_exec1, args=(), kwargs={"time": 1}, callback=call_back, block=False))
engine.wait()
```


### Thread scale up/down

```python
engine.scale_up(3)
engine.scale_down(3)
```
