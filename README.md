ReliableUDP
===========

Simple pure python protocol that extends UDP functionality by providing a optional "reliable mode" for handling packages.  It serves as the network protocol for a game im developing.

Besides the listening function, it implements two functions for sending messages, one that is direct and fast but unreliable (pure UDP) and other that is "reliable", guaranteeing data delivery with correct order and no duplicates.

The reliable delivery is made by requesting an "received confirmation" and then automatically resending data when confirmation is not sent back (it uses a queue for mananging order, and because it requires confirmation its not as fast as the direct method for sending multiple packets).

ReliableUDP also implements a message listener decorator to facilitate the development. It uses CustomStruct for the message serialization system. 
