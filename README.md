# cc-load-balancer

An implementation of a simple load-balancer (fifth in a series of coding challenges by John Crickett). This entails no external dependencies. The only built-ins that are used:
- `http.server`: For listening to the clients requests.
- `urllib`: For forwarding the requests to the servers.
- `typing`: For type inference.
- `gzip` & `io`: For implementing GZIP compression of responses.
- `logging`: To handle logs.
- `threading` & `time`: To run a separate thread for health checks every 10 seconds.


## Files

- `cclb.py`: The load balancer.
- `server.py`: A custom server that is run for the purpose of testing.
- `data.json`: Dummy data to be fetched for the client.
- `health_checkers.py`: To implement server cluster health checks.
- `loggers.py`: To set up logging.
- `urls.txt`: Set of URLs to hit concurrently using `curl`.


## Logic

- The use of `ThreadingHTTPServer` over `HTTPServer` ensures that for every incoming connection, a different thread is allocated. Hence, the program runs on a multithreaded approach without any race conditions.
- The program runs along with a health-check running on another thread as a daemon process. The health-check happens by periodically polling a server from the cluster of servers every 10 seconds. If any server is down or unresponsive, it is flagged.
- For every connection recieved, the server cluster is polled so that the servers can handle the requests accordingly. The server polled actually depends on the server cluster configuration, which is handled in the class `ServerCluster`. If a server is disabled due to failed health checks, the next server is considered to handle the incoming request.
- Load balancer operates on the round robin algorithm, in which every request is routed to _(i + 1) % n_ th server.
- Most necessary headers are carried over from the servers, with some headers being swapped out for the integrity of the system.
- Some inherited methods were overriden to configure and customize some application components, like logs, the Date and System header, etc.


## Usage

To test out the implementation, run the `server.py` N number of times (say, 3) in different ports: `python3 server.py 700x` (replace x by different digits: I use 7000, 7001 and 7002; that's what I have hardcoded in the load balancer program as well). If you decide to change things up, alter the `cclb.py` file as well.

After that, turn on the load balancer: `python3 cclb.py`. It runs at 8080 by default.

Finally, run the curl command to execute all the requests:

```sh
curl --compressed --parallel --parallel-immediate --parallel-max 3 --config urls.txt
```

Explanation of the command:
- It expects the responses to be compressed, due to which `--compressed` option is used. This is to support GZIP decompression. cURL natively doesn't decompress unless explicitly specified.
- It reads all URLs from the `urls.txt` file due to the `--config` option.
- Use `--parallel --parallel-immediate` to run requests concurrently (we are doing 3 at a time here, to see if multiple connections can be handled by our program).
