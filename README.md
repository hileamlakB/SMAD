# SMAD

SMAD is a `sm`all,`a`synchronous `d`istributed system that is meant to simulate logical clocks in large distirbuted system. 
The model runs on a single machine and simulates multiple machines running at different speeds, each with its own logical clock. 
The model allows messages to be passed between the virtual machines using a network queue and profiles different paramters like 
`Message queue built ups`, `response times`, `clock gaps` and so on.

## Installation
Clone the repository to your local machine using the following command:

git clone https://github.com/[username]/[repository-name].git

# Usage
To use the model, navigate to the project directory and run the main.py file using the following command:


python main.py

Once the model is initialized, each virtual machine will work according to the following specification:

On each clock cycle, if there is a message in the message queue for the machine, the virtual machine will take one message off the queue, update the local logical clock, and write in the log that it received a message, the global time (gotten from the system), the length of the message queue, and the logical clock time.
If there is no message in the queue, the virtual machine will generate a random number in the range of 1-10 and perform the following actions based on the value:
If the value is 1, send a message that is the local logical clock time to one of the other machines, update its own logical clock, and update the log with the send, the system time, and the logical clock time.
If the value is 2, send a message that is the local logical clock time to the other virtual machine, update its own logical clock, and update the log with the send, the system time, and the logical clock time.
If the value is 3, send a message that is the logical clock time to both of the other virtual machines, update its own logical clock, and update the log with the send, the system time, and the logical clock time.
If the value is other than 1-3, treat the cycle as an internal event, update the local logical clock, and log the internal event, the system time, and the logical clock value.
The lab notebook should be used to record all design decisions, observations, and reflections about the model and the results of running the model. The model should be run at least 5 times for at least one minute each time, and the logs should be examined to discuss the size of the jumps in the values for the logical clocks, drift in the values of the local logical clocks in the different machines, and the impact of different timings on such things as gaps in the logical clock values and length of the message queue.

License
This project is licensed under the MIT License. See the LICENSE file for more information.
