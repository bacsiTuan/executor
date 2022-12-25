# Executor
Fast execute task with python and less mem ops


## Why we need Thread Executor?

Python threading module is a good structure, it helps developers to folk a thread to run some background tasks.
Python have Queue mechanism to connect thread data.
But what problem??

- First, threading module folk threads but python not commit late time. Then know your thread can run, but you don't know when? It's oke fast with small traffic but when server high load you will have some problem, high pressure on memory because when you create too many thread cause slowness. `waste of time`

- Second, when you create and release threads many times, it'll increase memory and CPUs time of system. Sometime, developers did not handle exceptions and release thread. It can put more pressure to the application. `waste of resource`

## How to resolve problem??

This's my resolver.

- We create `exact` or `dynamic` number of threads. Then using `Job` - a unit bring data information to `Worker` to process. Workers don't need to release, and you only create 1 time or reset it when you update config.

- Job bring 2 importance field is: `func` and `args` and you can call them like `func(*args)` and get all the results and return on `callback` is optional.
- Your app doesn't need to create and release threads continuously
- Easy to access and using when coding.

## Disadvance?

- If you use callback then remembered to `add try catch` to handle thread leaked.
- If queue is full you need to wait for available queue slot. set `max_queue_size=0` to avoid this.
- If you restart your app, all the `Jobs` in `Queue` that have not been processed will be `lost`.

## Installtion

Now it's time you can install lib and experience

```bash
pip install thread-executor
```

## Usage : Interface list
```go
type ISafeQueue interface {
	Info() SafeQueueInfo // engine info
	Close() error // close all anything
	RescaleUp(numWorker uint) // increase worker
	RescaleDown(numWorker uint) error // reduce worker
	Run() // start
	Send(jobs ...*Job) error // push job to hub
	Wait() // keep block thread
	Done() // Immediate stop wait
}
```

### Initial
```go
    engine = CreateSafeQueue(&SafeQueueConfig{
        NumberWorkers: 3,
        Capacity: 500,
        WaitGroup: &sync.WaitGroup{},
    })
    defer engine.Close() // flush engine

    // go engine.Wait() // folk to other thread
    engine.Wait() // block current thread
```
### Send Simple Job
```go
    // simple job
    j := &Job{
        Exectutor: func(in ...interface{}) {
            // any thing
        },
        Params: []interface{1, "abc"}
    }
    engine.Send(j)
    // send mutiple job
    jobs := []*Job{
        {
             Exectutor: func(in ...interface{}) {
            // any thing
        },
        Params: []interface{1, "abc"}
        },
         Exectutor: func(in ...interface{}) {
            // any thing
        },
        Params: []interface{2, "abc"}
    }
    engine.Send(jobs...)
```

### Send Job complicated
```go
    // wait for job completed
    j := &Job{
        Exectutor: func(in ...interface{}) {
            // any thing
        },
        Params: []interface{1, "abc"},
        Wg: &sync.WaitGroup{},
    }
    engine.Send(j)
    // wait for job run success
    j.Wait()

    // callback handle async
    // you can sync when use with waitgroup
    j := &Job{
        Exectutor: func(in ...interface{}) {
            // any thing
        },
        CallBack: func(out interface{}, err error) {
            // try some thing here
        }
        Params: []interface{1, "abc"}
    }
    engine.Send(j)
```


### Send Job with groups
```go
    // prepaire a group job.
	group1 := make([]*Job, 0)
	for i := 0; i < 10; i++ {
		group1 = append(group1, &Job{
            Exectutor: func(in ...interface{}) {
                // any thing
            },
            Params: []interface{1, "abc"},
            Wg: &sync.WaitGroup{},
        })
	}
    // wait for job completed
	engine.SendWithGroup(group1...)

    engine.Wait()
```

### safequeue scale up/down

```go
    engine.ScaleUp(5)
    engine.ScaleDown(2)
```
