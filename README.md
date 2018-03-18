# DoEvery

Running jobs regularly in threads.

## What is it

This is a spin-off of a closed source application. It's an easy way to start long-running processes regularly. See example.

## Example

``` 
def exampleTask(stopEv):
    # do something long running every 15 seconds
    pass

if __name__ == "__main__":
    loop = DoEvery()
    loop.RunAndRequeue(exampleTask, 15, loop.StopEvent)
    loop.Loop(threadInfoInterval=60)
```

Thats it. More options see example in DoEvents.py

## Donate

Support me with bitcoins:

![Imgur](https://i.imgur.com/ltpF0A4m.png)

1MiToswzMsrhQEfmZbLQT8PHC68E5JhJzh

Thanks.
