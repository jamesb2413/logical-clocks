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

def consumer(conn):
    sleepVal = 0.0
    while True:
        time.sleep(sleepVal)
        data = conn.recv(1024)
        # print("msg received\n")
        dataVal = data.decode('ascii')
        net_q.put(int(dataVal))
 
# TODO: pull out logic as helper with sockets as args with return values
def producer(log, portVal1, portVal2):
    host= "127.0.0.1"
    port1 = int(portVal1)
    port2 = int(portVal2)
    s1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sleepVal = 0.0
    global code
    #sema acquire
    try:
        s1.connect((host,port1))
        s2.connect((host,port2))
        while True:
            # Block while queue is not empty
            while code == -1:
                continue
            if code == 1:
                # send to one of the other machines a message that is the local logical clock time, 
                # update the log with the send, the system time, and the logical clock time
                msg = str(log_clock)
                helpers.write_data(log, ["Send to one", str(time.time() - START_TIME), "0", msg])
                s1.send(msg.encode('ascii'))
            elif code == 2:
                # send to other machine a message that is the local logical clock time, 
                # update the log with the send, the system time, and the logical clock time
                msg = str(log_clock)
                helpers.write_data(log, ["Send to other", str(time.time() - START_TIME), "0", msg])
                s2.send(msg.encode('ascii'))
            elif code == 3:
                # send to both other machines a message that is the local logical clock time, 
                # update the log with the send, the system time, and the logical clock time
                msg = str(log_clock)
                helpers.write_data(log, ["Send to both", str(time.time() - START_TIME), "0", msg])
                s1.send(msg.encode('ascii'))
                s2.send(msg.encode('ascii'))
            else:
                # treat the cycle as an internal event; 
                # log the internal event, the system time, and the logical clock value.
                helpers.write_data(log, ["Internal", str(time.time() - START_TIME), "0", str(log_clock)])
            code = -1

    except socket.error as e:
        print ("Error connecting producer: %s" % e)
 
# Initialize server at sPort
def init_server(config):
    HOST = str(config[0])
    PORT = int(config[1])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        start_new_thread(consumer, (conn,))
 
# config: [localHost, conPort, prodPort1, prodPort2]
def machine(config, portDict):
    # Initialize machine by passing consumer port
    conPort = config[1]
    log, clock_rate = helpers.init_log(conPort, portDict)

    global net_q
    # Queue of messages containing timestamp values
    net_q = queue.Queue()
    global code
    code = -1
    global log_clock
    log_clock = 0
    init_thread = Thread(target=init_server, args=(config,))
    init_thread.start()
    # add delay to initialize the server-side logic on all processes
    time.sleep(2)
    # extensible to multiple producers
    prod_thread = Thread(target=producer, args=(log, config[2], config[3]))
    prod_thread.start()
    time.sleep(2)
    global START_TIME 
    START_TIME = time.time()
    # Run clock cycles
    while True:
        if conPort == 2056:
            print("-----------")
        elif conPort == 3056:
            print("~~~~~~~~~~~")
        else:
            print(">>>>>>>>>>>")
        for i in range(clock_rate):
            # Update the local logical clock.
            log_clock += 1
            if not net_q.empty():
                msg_T = net_q.get(False)
                if conPort == 2056:
                    print("-msg_t", msg_T)
                elif conPort == 3056:
                    print("~msg_t", msg_T)
                else:
                    print(">msg_t", msg_T)
                log_clock = max(log_clock, msg_T + 1)
                # Write in the log that it received a message, the global time, the length of the message queue, and the logical clock time.
                helpers.write_data(log, ["Recv", str(time.time() - START_TIME), str(net_q.qsize()), str(log_clock)])
            # If queue is empty
            else:
                if conPort == 2056:
                    print("-empty")
                elif conPort == 3056:
                    print("~empty")
                else:
                    print(">empty")
                code = random.randint(1,10)
                # Block until log
                while code != -1:
                    continue
        if conPort == 2056:
            print("-----------")
        elif conPort == 3056:
            print("~~~~~~~~~~~")
        else:
            print(">>>>>>>>>>>")
        # Goal: No time leakage. Exactly 1 second between first event of one loop and first event of next loop.
        time.sleep(1.0 - ((time.time() - START_TIME) % 1.0))

localHost= "127.0.0.1"
    
if __name__ == '__main__':
    # Global ports for all processes
    port1 = 2056
    port2 = 3056
    port3 = 4056
    portDict = {'port1': port1, 'port2': port2, 'port3': port3}

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