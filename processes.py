from multiprocessing import Process
import os
import socket
from _thread import *
import threading
import time
from threading import Thread
import random
import queue
from datetime import datetime
from pytz import timezone
 

def consumer(conn):
    print("consumer accepted connection" + str(conn)+"\n")
    sleepVal = 0.900
    while True:
        time.sleep(sleepVal)
        data = conn.recv(1024)
        # print("msg received\n")
        dataVal = data.decode('ascii')
        print("msg received:", dataVal)
        net_q.append(dataVal)
 

def producer(portVal1, portVal2):
    host= "127.0.0.1"
    port1 = int(portVal1)
    port2 = int(portVal2)
    s1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sleepVal = 0.500
    #sema acquire
    try:
        s1.connect((host,port1))
        s2.connect((host,port2))
        while True:
            time.sleep(sleepVal)
            # If code not set because queue is not empty
            if code == -1:
                continue
            elif code == 1:
                # send to one of the other machines a message that is the local logical clock time, 
                # update it’s own logical clock, and update the log with the send, the system time, and the logical clock time
                msg = "hello"
                print("Client-side connection success to port val:" + str(portVal1) + "\n")
                s1.send(msg.encode('ascii'))
            elif code == 2:
                # send to other machine a message that is the local logical clock time, 
                # update it’s own logical clock, and update the log with the send, the system time, and the logical clock time
                msg = "hello"
                print("Client-side connection success to port val:" + str(portVal2) + "\n")
                s2.send(msg.encode('ascii'))
            elif code == 3:
                # send to both other machines a message that is the local logical clock time, 
                # update it’s own logical clock, and update the log with the send, the system time, and the logical clock time
                msg = "hello"
                print("Client-side connection success to port val:" + str(portVal1) + "\n")
                print("Client-side connection success to port val:" + str(portVal2) + "\n")
                s1.send(msg.encode('ascii'))
                s2.send(msg.encode('ascii'))
            else:
                # treat the cycle as an internal event; 
                # update the local logical clock, and log the internal event, the system time, and the logical clock value.
                pass

    except socket.error as e:
        print ("Error connecting producer: %s" % e)
 
# Initialize server at sPort
def init_machine(config):
    HOST = str(config[0])
    PORT = int(config[1])
    print("starting server| port val:", PORT)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        start_new_thread(consumer, (conn,))
 
# config: [localHost, sPort, cPort, pid]
def machine(config):
    # Initialize machine
    config.append(os.getpid())
    interval = 1.0 / random.randint(1,6)
    global net_q
    net_q = queue.Queue()
    global code
    code = -1
    print(config)
    init_thread = Thread(target=init_machine, args=(config))
    init_thread.start()
    #add delay to initialize the server-side logic on all processes
    time.sleep(5)
    # extensible to multiple producers
    prod_thread = Thread(target=producer, args=(config[2],config[3]))
    prod_thread.start()
    # Run clock cycles
    starttime = time.time()
    while True:
        # run every interval s
        time.sleep(interval - ((time.time() - starttime) % interval))
        try:
            msg = net_q.get()
            global_time = datetime.now(timezone('EST'))
            # Update the local logical clock.
            # Write in the log that it received a message, the global time, the length of the message queue, and the logical clock time.
        # If queue is empty
        except:
            code = random.randint(1,10)
            if code == 1:


localHost= "127.0.0.1"
    
if __name__ == '__main__':
    port1 = 2056
    port2 = 3056
    port3 = 4056


    config1=[localHost, port1, port2, port3]
    p1 = Process(target=machine, args=(config1,))
    config2=[localHost, port2, port3, port1]
    p2 = Process(target=machine, args=(config2,))
    config3=[localHost, port3, port1, port2]
    p3 = Process(target=machine, args=(config3,))

    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()