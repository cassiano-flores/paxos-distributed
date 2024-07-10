# Paxos Made Moderately Complex (PaxosMMC)

This repository includes the Python source code
corresponding to the Paxos code presented on http://paxos.systems.

Abrir 8 terminais, um parada cada processo.

Aplicação:

```sh
$ python env.py
```

Replicas:

```sh
$ python replica.py 5001
$ python replica.py 5002
```

Leaders:

```sh
$ python leader.py 6001
$ python leader.py 6002
```

Acceptors:

```sh
$ python acceptor.py 7001
$ python acceptor.py 7002
$ python acceptor.py 7003
```
