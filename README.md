# logical-clocks
A model of a small, asynchronous distributed system with different machines running at different and independent speeds. See Lamport 1978 Time, Clocks, and the Ordering of Events in a Distributed System.
The program runs 3 processes to model separate machines. Each process runs at a clock rate in [1,6] determined randomly during initialization. The clock rate determines the number of communication events that can happen within one second on that machine. 
Each machine listens on two sockets for messages from the other two machines, storing new messages in a queue.
Each machine keeps track have a logical clock, which is updated using Lamport's rules for logical clocks. After each instruction, the logical clock increments by 1. If one machine receives a message from another, the receiving machine updates its logical clock to the maximum of its own logical clock and the logical clock of the sending machine (after incrementing). The messages sent between machines contain the logical clock of the sending machine. The purpose of the logical clocks is to maintain a consistent partial ordering between the machines so that every causal relationship between any two events (local or across the network) has a consistent conception of logical time.
Each event is logged in a csv file for each process, so that the global time (gotten from the system), the length of the message queue, and the logical clock time can be observed.

Each virtual machine works according to the following specification:
On each clock cycle, if there is a message in the message queue for the machine the virtual machine takes one message off the queue, updates the local logical clock, and writes in the log that it received a message, the global time (gotten from the system), the length of the message queue, and the logical clock time.

If there is no message in the queue, the virtual machine should generate a random number in the range of 1-10, and

if the value is 1, send to one of the other machines a message that is the local logical clock time, update it’s own logical clock, and update the log with the send, the system time, and the logical clock time
if the value is 2, send to the other virtual machine a message that is the local logical clock time, update it’s own logical clock, and update the log with the send, the system time, and the logical clock time.
if the value is 3, send to both of the other virtual machines a message that is the logical clock time, update it’s own logical clock, and update the log with the send, the system time, and the logical clock time.
if the value is other than 1-3, treat the cycle as an internal event; update the local logical clock, and log the internal event, the system time, and the logical clock value.


Engineering Notebook: [https://www.notion.so/Logical-Clocks-Lab-Notebook-4aa4bde234c84bbe8f3be8514ea9cb1d](https://thoughtful-roarer-3a6.notion.site/Logical-Clocks-Lab-Notebook-4aa4bde234c84bbe8f3be8514ea9cb1d)

To run: `python processes.py`
