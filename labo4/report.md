---
titlepage: true
title: "Laboratoire 4 : Slicing"
subtitle: "Virtualisation de réseaux informatiques"
author: [Sylvain Renaud]
date: \today
toc: true
toc-own-page: true
logo: "../logo-hes-so.jpg"
logo-width: 200
---

# Part 1 : Topology-based Slicing

## Test du code

```bash
mininet> pingall
*** Ping: testing ping reachability
h1 -> X h3 X
h2 -> X X h4
h3 -> h1 X X
h4 -> X h2 X
*** Results: 66% dropped (4/12 received)
```

On peut voir que h1 communique uniquement avec h3 et h2 uniquement avec h4, comme l'on souhaitait.

# Part 2 : Flowspace Slicing

## Test du code

Test sur le port 80 (vidéo)

```bash
mininet> h2 iperf -c h3 -p 80 -t 2 -i 1
------------------------------------------------------------
Client connecting to 10.0.0.3, TCP port 80
TCP window size: 85.3 KByte (default)
------------------------------------------------------------
[  3] local 10.0.0.2 port 42356 connected with 10.0.0.3 port 80
[ ID] Interval       Transfer     Bandwidth
[  3]  0.0- 1.0 sec  1.75 MBytes  14.7 Mbits/sec
[  3]  1.0- 2.0 sec  1.25 MBytes  10.5 Mbits/sec
[  3]  0.0- 2.0 sec  3.12 MBytes  12.9 Mbits/sec
```

Test sur le port 22 (non-vidéo)

```bash
mininet> h2 iperf -c h3 -p 22 -t 2 -i 1
------------------------------------------------------------
Client connecting to 10.0.0.3, TCP port 22
TCP window size: 85.3 KByte (default)
------------------------------------------------------------
[  3] local 10.0.0.2 port 50854 connected with 10.0.0.3 port 22
[ ID] Interval       Transfer     Bandwidth
[  3]  0.0- 1.0 sec   384 KBytes  3.15 Mbits/sec
[  3]  1.0- 2.0 sec   128 KBytes  1.05 Mbits/sec
[  3]  0.0- 2.2 sec   640 KBytes  2.39 Mbits/sec
```

On peut voir que lorsque que l'on utilise la vidéo (port 80), on passe par une connexion haut débit (environ 10Mbits/s), alors que si on fait le test avec le port 22, on passe par une connexion "bas" débit d'environ 1Mbits/s. C'est le résultat auquel nous nous attendions.
