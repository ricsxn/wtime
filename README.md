# wtime
Working time watcher

This python code allows to monitor working time providing real time statistics such as:

Start time    : The time the worker has started

Working time  : The time the worker has to perform (excluding pause time)

Pause time    : The time allowed for the lunch break

Current time  : The time when the user is extracting statistics

Current elapse: How much time the worker has already performed

Due time      : The time when the user accomplishes her work

Remaining time: How much time the worker has to perform yet

Ticket time   : The necessary time to gain the ticket

Ticket at     : The time when ticket will be gained

Ticket remain : How much time the worker needs to gain ticket


Execution

./wtime.py <start_time_hour> <start_time_minute> [start_time_seconds]

Working parameters such as: working time, pause time, ticket time, etc must be configured modifying the code or wtime class variable members.

# wtime2
Working time watcher, to be used in case working time has been splitted in two intervals (morning+afternoon)

./wtime2.py t1 [[[t2] t3] t4]

Where tx is a timestamp in the form of HH:MM:SS

# wtime3
This version works exactly like wtime2 integrating the new calculation using the wtime object. This version is used by the wtimegui wich provides a tkinter based GUI.


