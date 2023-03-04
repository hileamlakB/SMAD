## Introduction

This engineering notbook is developed along side the development of this project to keep track of the programmers mind state. If in the future, there is to be a bug or people (mostly myself) find this repository intersting they can look at the things that were going through the authors mind. As this is a scratch book, there isn't much of a structure and format to it, but I will try to but meaningful headers and subscections as much as possible.

## Brain storming

##### Random Implementation details

- I should have a processor class with the following methods

  - Send a message
  - Receive a message
  - Sleep

- This class should be initialized with properties like

  - clock rate - the number of operations a function will execute per second
  - port ad socket - each model process should have a socket opened ready for sending and receiing messages atleast from 50 other process,
  - logical clock
  - List of other process to send messages to
  - A file discriptor to a log clock updates

- I can either make a process brodcast a message or send to a few random process: in the spec it is required to send to one machine at random
- The queue should be running in a thread so that it isn't blocked when a process is sleeping, I don't think that is the case any ways but I will have to make sure.
- There should be a master program starting all the processes and introducing them to the other process

##### Testing

- I should have a unit test ot the class for its different methods inclusind a doc string before I implement the code like last time.
- Write the unittest after I write the structure and the doc string and then the test before the actual implementation.
- I should also have a test after impleementation is compelete to test implementation detials that were unforseen.

##### Future improvments

- Add support to do spcialized tasks like matrix multiplication to add some cool usecase to the proojects

##### Current Todos

1. Structure unit test
2. Read the time paper again
3. Write a short article on the time paper
4. Read the paper on wruting unit tests
5. Write strucute and unit tests
6. Write unit tests

## Coding

To make testing easier, for isntance to test the logging function, I found it important to isolate the logger from the actual class, and thus I have decided to create a special class called FileLogger. This is called `dependency injection`. It is something cool I learned.

This dependancy class will have the following methods, logs, close and read.

## Socket implementation

When implementing the socket connection between the process I found two options

1. Each process maintians multiple client sockets for each of the other processes so that it doesn't have to deal with the overhead of deleting and creating a new socket each time it wants to send a message. The down side is in a scalable system if there are multiple processes this will require maintaining multiple sockets, which might not be possible as there are limits to the number of open sockets an os can support. ulimt -n gives the maximum number of file discriptors in linux which will be required by sockets.
2. ible as there are limits tEach time process wants to send a message, it just creats a socket and delets it as soon as it is done. The upside, scalable, interms of number of sockets. And easy mentenance. The downside for a small simulatino like ours the overhead of destorying and creating clients everytime might be noticable.

## `:lightbulb:`Cool ideas

- To have actuall parallelism, write the processes models in python and implement the orcester program in c using the pthread liberary

## Experiments

After implementing the the small scallable distirbuted system, here are some of the tests I run.
