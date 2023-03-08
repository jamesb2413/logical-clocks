from multiprocessing import Process
import os
import socket
from _thread import *
import threading
import random
import time
from threading import Thread
import queue
from datetime import datetime
from pytz import timezone

import helpers

# Send a message based on roll of 1-10
def send_roll(log, roll_10, s1, s2):
    # Send: 1 -> 2, 2 -> 3, or 3 -> 1
    if roll_10 == 1:
        msg = str(logic_clock)
        data = helpers.write_data(log, ["Send to one", str(time.time() - START_TIME), "0", msg])
        s1.send(msg.encode('ascii'))
    # Send: 1 -> 3, 2 -> 1, or 3 -> 2
    elif roll_10 == 2:
        msg = str(logic_clock)
        data = helpers.write_data(log, ["Send to other", str(time.time() - START_TIME), "0", msg])
        s2.send(msg.encode('ascii'))
    # Send to both
    elif roll_10 == 3:
        msg = str(logic_clock)
        data = helpers.write_data(log, ["Send to both", str(time.time() - START_TIME), "0", msg])
        s1.send(msg.encode('ascii'))
        s2.send(msg.encode('ascii'))
    # 4-10: Internal event
    else:
        data = helpers.write_data(log, ["Internal", str(time.time() - START_TIME), "0", str(logic_clock)])
    return data

def init_threads(log, config, net_q):
    # Initialize server and consumers
    server_thread = Thread(target=init_server, args=(config, net_q))
    server_thread.start()
    time.sleep(2)

    # Initialize producers
    prod_thread = Thread(target=producer, args=(log, config[2], config[3]))
    prod_thread.start()
    time.sleep(2)

# Initialize server and consumers at sPort
def init_server(config, net_q):
    HOST = str(config[0])
    PORT = int(config[1])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        start_new_thread(consumer, (conn, net_q))

def consumer(conn, net_q):
    sleepVal = 0.0
    while True:
        time.sleep(sleepVal)
        data = conn.recv(1024)
        # print("msg received\n")
        dataVal = data.decode('ascii')
        net_q.put(int(dataVal))
 
def producer(log, portVal1, portVal2):
    host= "127.0.0.1"
    port1 = int(portVal1)
    port2 = int(portVal2)
    s1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sleepVal = 0.0
    global roll_10
    #sema acquire
    try:
        s1.connect((host,port1))
        s2.connect((host,port2))
        while True:
            # Block while queue is not empty
            while roll_10 == -1:
                continue
            # Send a message based on roll of 1-10
            send_roll(log, roll_10, s1, s2)
            # Reset roll to -1 to wait until next empty queue
            roll_10 = -1

    except socket.error as e:
        print ("Error connecting producer: %s" % e)
 
# Main logic of program. config: [localHost, conPort, prodPort1, prodPort2]
def machine(config, portDict):
    # Initialize machine by passing consumer port
    conPort = config[1]
    log, clock_rate = helpers.init_log(conPort, portDict)

    # Queue of messages containing timestamp values
    net_q = queue.Queue()
    global logic_clock
    logic_clock = 0
    # Random roll out of 10, -1 if queue is not empty
    global roll_10
    roll_10 = -1

    # Initialize server, consumers, and producers
    init_threads(log, config, net_q)

    # Run clock cycles
    global START_TIME 
    START_TIME = time.time()
    while True:
        for i in range(clock_rate):
            # Update the logical clock
            logic_clock += 1
            # Receive message
            if not net_q.empty():
                msg_T = net_q.get(False)
                logic_clock = max(logic_clock, msg_T + 1)
                helpers.write_data(log, ["Recv", str(time.time() - START_TIME), str(net_q.qsize()), str(logic_clock)])
            # If queue is empty
            else:
                roll_10 = random.randint(1,10)
                # Block until event is logged
                while roll_10 != -1:
                    continue
        # sleep for remainder of 1 second
        time.sleep(1.0 - ((time.time() - START_TIME) % 1.0))
    
if __name__ == '__main__':
    # Global ports for all processes
    port1 = 2056
    port2 = 3056
    port3 = 4056
    portDict = {'port1': port1, 'port2': port2, 'port3': port3}
    localHost= "127.0.0.1"

    config1=[localHost, port1, port2, port3]
    p1 = Process(target=machine, args=(config1, portDict))
    config2=[localHost, port2, port3, port1]
    p2 = Process(target=machine, args=(config2, portDict))
    config3=[localHost, port3, port1, port2]
    p3 = Process(target=machine, args=(config3, portDict))

    start_time = time.time()
    p1.start()
    p2.start()
    p3.start()

    while True:
        if time.time() - start_time > 60.0:
            p1.terminate()
            p2.terminate()
            p3.terminate()
            print("killed")
            break

    p1.join()
    p2.join()
    p3.join()