import socket  # Import socket module
import sys
from collections import namedtuple
import pickle
#from _thread import *
import threading
#import inspect
import time
import signal


#python server.py
# python client.py


DATA_TYPE = 0b101010101010101
DATA_SIZE = 64   #need to be modified

data_pkt = namedtuple('data_pkt', 'seq_num checksum data_type data')
ack_pkt = namedtuple('ack_pkt', 'seq_num zero_field data_type')
N = 0  # window size
MSS = 0 # maximum segment size
ACK = 0 # ACK received from server.
num_pkts_sent = 0
num_pkts_acked = 0
seq_num = 0
#print(file_content)
#print (N)
window_low = 0
window_high = int(N)-1
total_pkts = 0
RTT = 0.06
pkts = []
done_transmitting = 0
starttime = 0
stoptime= 0




ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP Foo
host = socket.gethostname()
ack_port_num = 62223
ack_socket.bind((host, ack_port_num))

lock = threading.RLock()  # for lock sth

# Carry bit used in one's combliment
def carry_checksum_addition(num_1, num_2):
    c = num_1 + num_2
    return (c & 0xffff) + (c >> 16)


# Calculate the checksum of the data only. Return True or False
def calculate_checksum(message):
   # print (message)
    # if (len(message) % 2) != 0:
    #     message += bytes("0")

    checksum = 0
    for i in range(0, len(message), 2):
        my_message = str(message)
        w = ord(my_message[i]) + (ord(my_message[i+1]) << 8)
        checksum = carry_checksum_addition(checksum, w)
    return (not checksum) & 0xfff



def pack_data(message, seq_num):
    #pkt = data_pkt(seq_num, calculate_checksum(message), DATA_TYPE, message)
    pkt = data_pkt(seq_num, calculate_checksum(message), DATA_TYPE, message)
    #packed_pkt = pack('ihh' + str(DATA_SIZE) + 's', pkt.seq_num, pkt.checksum, pkt.data_type, bytes(pkt.data,'utf-8'))
    my_list = [pkt.seq_num, pkt.checksum, pkt.data_type, pkt.data]
    packed_pkt = pickle.dumps(my_list)
    return packed_pkt


def prepare_pkts(file_content, seq_num):
    pkts_to_send = []
    seq_num = 0
    for item in file_content:   # Every MSS bytes should be packaged into segment Foo
        pkts_to_send.append(pack_data(item, seq_num))
        seq_num += 1
    return pkts_to_send
    #your code here


def socket_function(pkts):
    #print (pkts)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create a socket object

    # comment this block when ready for command line argument
    # N = input("Please enter window size N:>")
    # MSS = input("Please enter MSS in Bytes:>")
    #host = socket.gethostname()  # Get local machine name
    # print("Host:", host)
    host="192.168.1.116"
    
    port = 7735  # Reserve a port for your service.
    s.connect((host,port))
    print("connected")
    s.sendto(pkts, (host, port))
    s.close()

def timer():
    global pkts
    global window_low
    global window_high
    global total_pkts
    global ACK
    #t = threading.Timer(RTT, timer)
    #t.start()
    #print ("Timer AAAAA")
    resent_index = window_low  # resent from window_low to window_high
    time.sleep(RTT)
    if ACK == window_low:
        print ("Timeout sequence number ="+ str(ACK))
        lock.acquire()
       # print ("Timer CC")
        # print ("resent begin")
        while resent_index <= window_high and resent_index < total_pkts:
           # print ("resent "+ str(resent_index))
            # signal.alarm(0)
            # signal.alarm(int(RTT))
            #signal.alarm(0)
            #signal.setitimer(signal.ITIMER_REAL, RTT)
            #threading.Timer(RTT)
            #time.sleep(RTT)
            socket_function(pkts[resent_index])
            resent_index += 1
            print(resent_index-1)
        lock.release()
        # print("=========")
    #if done_transmitting == 1:
            #t.cancel()
            #t._delete()
            #exit()


def send_file(file_content, sock, hostname, port):
    global total_pkts
    total_pkts = len(file_content)
    #print(total_pkts)
    global pkts
    global seq_num
    global RTT
    pkts= prepare_pkts(file_content, seq_num)
    global num_pkts_sent
    #send the first window
    current_max_window = min(int(N), int(total_pkts))
    #signal.alarm(int(RTT))
    #signal.setitimer(signal.ITIMER_REAL, RTT)
    #time.sleep(RTT)
    while num_pkts_sent < current_max_window :
       # socket_function(pkts[num_pkts_sent], sock, hostname, port)
        #t = threading.Timer(RTT,socket_function("hello"))
        if ACK == 0:
            #print("ack=0, sending packet")
            #print ("num_pkts_sent"+ str(num_pkts_sent))
            socket_function(pkts[num_pkts_sent])
            #print("pakage "+str(num_pkts_sent)+"sent from first")
            #print(pkts[num_pkts_sent])
            num_pkts_sent += 1
        else:
            break
       

def ack_listen_thread(sock, host, port):
    global window_high
    global window_low
    global num_pkts_sent
    global num_pkts_acked
    global total_pkts
    global ACK
    global done_transmitting
    global stoptime
    done_transmitting = 0
    #global threading_first_window
    while True:
        #threading_first_window.stop()
        print("waiting for ack")
        data = pickle.loads(ack_socket.recv(256))
        print("received some ack")
       # print("ACK "+str(data[0]))
        # print("Wind_low "+str(window_low))
        # print("WInd_high"+str(window_high))
        # print("num_pkts_sent "+str(num_pkts_sent))
        #print("total"+str(total_pkts))
        print("sent packet"+str(num_pkts_sent))
        if data[2]=="1010101010101010":  # data[2] is ACK identifier data[0] should be ACK sequence number. Foo
            ACK = data[0]
            print (ACK)
            if ACK: #and ACK >= int(N):  # if ACK != null. Foo
                print("acked packet"+str(ACK))
                # if ACK
                lock.acquire()
                if ACK >= window_low and ACK <total_pkts:
                    #signal.alarm(0)
                    #signal.alarm(int(RTT))
                    #signal.setitimer(signal.ITIMER_REAL, RTT)
                    #time.sleep(RTT)
                    #print(window_low)
                    temp_pckts_acked = ACK - window_low
                    old_window_high = window_high
                    #print("old window high")
                    #print(old_window_high)
                    window_high = min(window_high + ACK - window_low, total_pkts-1)
                    #print("window high")
                    #print(window_high)
                    window_low = ACK
                    num_pkts_acked += temp_pckts_acked  # Acked # of packages. Foo
                    print("ACK "+str(data[0]))
                    print("Wind_low "+str(window_low))
                    print("WInd_high"+str(window_high))
                    print("num_pkts_sent "+str(num_pkts_sent))
                    for i in range(int(window_high-old_window_high)):
                    #for i in range(int(old_window_high-window_low)):
                        print("means a packet loss has happened")
                        #print(int(window_high-old_window_high))
                        socket_function(pkts[num_pkts_sent])
                        #socket_function(pkts[ACK+i])
                        print("pakage is resent "+str(num_pkts_sent)+"sent")
                        if num_pkts_sent < total_pkts-1:
                                num_pkts_sent += 1

                if ACK == total_pkts:
                    print("Done!")
                    done_transmitting = 1
                    stoptime = time.time()
                    print("Running Time:",str(stoptime-starttime))
                    exit()

                lock.release()


##
#     # # add something to listen ACK from server.
#
#




def main():
    global N
    global MSS
    global starttime
    starttime = time.time()
    # Uncomment this when ready for command line argument
    #host, port, my_test_file, N, MSS = parse_command_line_arguments()
    host="JohnnyDell"
    port=7735
    my_test_file="test1234.txt"
    N=16
    MSS=500
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create a socket object

    # comment this block when ready for command line argument
   # N = input("Please enter window size N:>")
   # MSS = input("Please enter MSS in Bytes:>")
    #N = 1
    #MSS = 1000
    #host = socket.gethostname()  # Get local machine name
    #print("Host:", host)
    port = 7735  # Reserve a port for your service.
    #my_test_file = 'test.pdf'
    # finish comment here

    global window_high
    window_high = int(N)-1
    #signal.signal(signal.SIGALRM, timer)
    threading.Timer(2, timer).start()
    try:
        file_content = []
        #test_file = open(my_test_file, 'rb')

        with open(my_test_file, 'rb') as f:
            while True:
                chunk = f.read(int(MSS))  # Read the file MSS bytes each time Foo
                if chunk:
                    file_content.append(chunk)
                else:
                    break
        #print(file_content)
        #test_file.close()
    except:
        sys.exit("Failed to open file!")
        
    send_file(file_content, s, host, port)
    threading.Thread(target=ack_listen_thread, args=(s, host, port)).start()
    s.close()  # Close the socket when done


if __name__ == "__main__":
    main()
