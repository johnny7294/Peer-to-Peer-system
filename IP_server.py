import socket               # Import socket module
import pickle
import sys
from collections import namedtuple
import random
import time
import datetime

PKT_SIZE = 1024
DATA_SIZE = 64
ZERO_FIELD = 0
ACK_TYPE = 1010101010101010

data_pkt = namedtuple('data_pkt', 'seq_num checksum data_type data')
ack_pkt = namedtuple('ack_pkt', 'seq_num zero_field data_type')

ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)         # Create a socket object
host = socket.gethostname()  # Get local machine name
port = 62223                 # Reserve a port for your service.
#ack_socket.bind((host, port))         # Bind to the port


def send_ack(seq_num):
    # ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)         # Create a socket object
    # host = socket.gethostname()  # Get local machine name
    # port = 62223                 # Reserve a port for your service.
    # #ack_socket.bind((host, port))         # Bind to the port
    print("ack number sent")
    print(seq_num)
    reply_message = [seq_num, "0000000000000000", "1010101010101010"]
    # print(reply_message)
    ack_socket.sendto(pickle.dumps(reply_message), (host, port))


# Carry bit used in one's combliment
def carry_checksum_addition(num_1, num_2):
    c = num_1 + num_2
    return (c & 0xffff) + (c >> 16)


# Calculate the checksum of the data only. Return True or False
def calculate_checksum(message):
    # if (len(message) % 2) != 0:
    #     message += bytes("0")

    checksum = 0
    for i in range(0, len(message), 2):
        my_message = str(message)
        w = ord(my_message[i]) + (ord(my_message[i+1]) << 8)
        checksum = carry_checksum_addition(checksum, w)
    return (not checksum) & 0xffff



def parse_command_line_arguments():
    port = sys.argv[1]
    file_name = sys.argv[2]
    prob = sys.argv[3]

    return int(port), file_name, float(prob)


def main():
    #port, output_file, prob_loss = parse_command_line_arguments()
    port =7735
    output_file="test1234567890987654.txt"
    prob_loss=0.05
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)         # Create a socket object
    host = socket.gethostname()  # Get local machine name
    #port = 7735                 # Reserve a port for your service.
    s.bind((host, port))         # Bind to the port
    #prob_loss = 0.01
    #dt = str(datetime.time().second)
    #d = random.randrange(0, 1000000)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    #output_file = 'file_'+str(timestr)+'.pdf'
    lost_seq_num = []
    print_message = []
    packet_lost = False
    exp_seq_num = 0
    while True:
        #print("here")
        
        #s.listen(1)
        #conn, addr=s.accept()
        data, addr = s.recvfrom(1000000)
        print(addr)
        print(conn)
        #peer=s.getpeername()
        #print("now here")
        #print(peer)
        #print(addr)
        data = pickle.loads(data)
        #print(addr)
        seq_num, checksum, data_type, message = data[0], data[1], data[2], data[3]
        #print("Data: ", str(message))
        print("received packet seq_num")
        print(seq_num)
        rand_loss = random.random()

        if rand_loss <= prob_loss:
            print("Packet loss, sequence number = ", seq_num)
            packet_lost = True
            if len(lost_seq_num) == 0:
                lost_seq_num.append(seq_num)
            if len(lost_seq_num) > 0:
                if seq_num not in lost_seq_num and (seq_num>min(lost_seq_num)):
                    lost_seq_num.append(seq_num)
            exp_seq_num += 0
            
        else:
            if checksum != calculate_checksum(message):
                print("Packet dropped, checksum doesn't match!")
            #else:
            if seq_num == exp_seq_num:
               # print (seq_num)
                ack_seq = int(seq_num)+1
               # print("ACK "+ str(ack_seq))
                print("sending ack for : ")
                print(ack_seq)
                send_ack(ack_seq)
                print_message.append(seq_num)
                with open(output_file, 'ab') as file:
                    file.write(message)
                exp_seq_num += 1

if __name__ == "__main__":
    main()
