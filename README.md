ReliableUDP
===========

Simple pure python protocol that extends UDP functionality by providing a optional "reliable mode" for handling packages.  It serves as the network protocol for a game im developing.

It implements two functions for sending messages, one that is direct and fast but unreliable (pure UDP) and other that is "reliable", guaranteeing data delivery with correct order and no duplicates.

The reable delivery is made by requesting an "received confirmation" and then automatically resending data when confirmation is not sent back.

ReliableUDP also implements a message listener decorator to facilitate the development. It uses CustomStruct for the message serialization system. 
