#!/usr/bin/env python3
import socket
import struct
import sys


if len(sys.argv) < 3:
    print("Usage: python <ip> <port> <blocksize>")
    sys.exit(1)
# UDP server settings
UDP_IP = sys.argv[1]
UDP_PORT = int(sys.argv[2])
BLOCKSIZE = int(sys.argv[3])

# Sets for even and odd UIDs
even_uids = set()
odd_uids = set()
uid_ip_port_mapping = {}
uid_last_sequence = {}
uid_names = {}



# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Router is listening at {UDP_IP}:{UDP_PORT}")


def uidstr(uid):
    return str(int(uid) % 1000).zfill(3)
    


    


def reset_everything(uid):
    uid_names = {}
    even_uids.clear()
    odd_uids.clear()
    uid_ip_port_mapping.clear()
    uid_last_sequence.clear()
    print(f"Resetting over a new host uid: {uid}")


def multicast_message(uid, message):

    target_set = odd_uids if uid%2 == 0 else even_uids
    for target_uid in target_set:
        if target_uid in uid_ip_port_mapping:
            target_addr = uid_ip_port_mapping[target_uid]
            sock.sendto(message, target_addr)



def process_message(message, addr):
    # Extract UID and convert it
    uid, sequence = struct.unpack('<II', message[:8])
    uidf = uidstr(uid)
    if sequence % BLOCKSIZE != 0:
        print(f"** Received out of sequence message from {uid},{addr}**")
    
    is_even_user =  uid % 2 == 0
    is_new_user = uid not in even_uids and uid not in odd_uids
    if is_new_user and is_even_user:
        reset_everything(uid)
        even_uids.add(uid)
    elif is_new_user:
        odd_uids.add(uid)
    if is_new_user:
        uid_ip_port_mapping[uid] = addr
        print(f"ODDset {odd_uids} / EVENset {even_uids}")
        print(f"UID to IP/PORT: {uid_ip_port_mapping}")

    
    if sequence > 0 and uid in uid_last_sequence and uid_last_sequence[uid] != sequence - BLOCKSIZE:
        print(f"{uidf} window: {sequence-BLOCKSIZE} was not received")
    uid_last_sequence[uid] = sequence

    if len(odd_uids) > 0 and len(even_uids) > 0:
        #check sequence
        #route
        multicast_message(uid, message)
    else:
        print(f"{uidf}, {sequence}")

while True:
    # Receive messages
    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    process_message(data, addr)


