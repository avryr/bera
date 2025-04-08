import pyfldigi
import random
import time
import socket
import threading
import sys, os
import select
import logging
import string
from pymongo import MongoClient
from datetime import datetime
import pytz


# Configuration - ADJUST THESE AS NEEDED
ip_address = "localhost" # IP of remote host, most likely Tailscale. Default to localhost for testing.
PORT = 12345            # Port for internet communication
MODE = "QPSK250"          # Modem mode (e.g., BPSK31, BPSK63, RTTY)
CARRIER_FREQ = 1500     # Audio carrier frequency (Hz)
PACKET_SIZE = 100       # Number of bits per packet
NUM_PACKETS = 1        # Number of packets to send for testing
TX_DELAY = 2            # Add a delay between send and listen to allow RX machine to catch up
SQUELCH = 25             # Squelch Level

# HACK: put these here to make them global, just to avoid passing them from the thread
ber = 0.0
all_expected_data=b''
all_received_data=b''

# Logging configuration
logging.basicConfig(level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_random_hex_chars(num_chars):
    """Generates a string of random hexadecimal characters."""
    hex_chars = ''.join(random.choice('0123456789ABCDEF') for _ in range(num_chars))
    return hex_chars

def bit_error_rate(sent_bits, received_bits):
    """Calculates the bit error rate between two strings of bits, accounting for missing bits."""
    # Convert both strings to binary
    sent_bin = ''.join(format(ord(c), '08b') for c in sent_bits)
    received_bin = ''.join(format(ord(c), '08b') for c in received_bits)
    
    # Initialize variables for tracking errors and positions
    num_errors = 0
    sent_index = 0
    received_index = 0
    
    # Compare bits while accounting for missing bits
    while sent_index < len(sent_bin) and received_index < len(received_bin):
        if sent_bin[sent_index] != received_bin[received_index]:
            num_errors += 1
            # Check if the next bit in sent_bin matches the current bit in received_bin
            if sent_index + 1 < len(sent_bin) and sent_bin[sent_index + 1] == received_bin[received_index]:
                sent_index += 1  # Skip the missing bit in sent_bin
            # Check if the next bit in received_bin matches the current bit in sent_bin
            elif received_index + 1 < len(received_bin) and received_bin[received_index + 1] == sent_bin[sent_index]:
                received_index += 1  # Skip the missing bit in received_bin
        sent_index += 1
        received_index += 1
    
    # Account for any remaining bits in the longer string as errors
    num_errors += abs(len(sent_bin) - len(received_bin))
    
    # Calculate the bit error rate
    max_len = max(len(sent_bin), len(received_bin))
    ber = num_errors / max_len
    return ber


def send_data(fldigi_client, data_chars, tx_delay):
    """Sends data over the fldigi interface."""

    data_to_send = data_chars
    logger.info(f"Sending: {data_to_send}")

    # Clear the transmit buffer before transmitting
    fldigi_client.text.clear_tx()

    # fldigi.main.send requires a string, but we built a bit string.  The radio
    # doesn't care, and this is just bits anyway.
    fldigi_client.main.send("\r"*10 + data_to_send + "^r", block=True, timeout=30) # Send and return to RX mode (that's what the ^r does)
    time.sleep(tx_delay)  # Give the reciever a moment to get ready


def receive_data(fldigi_client, timeout=10):
    """Receives data from the fldigi interface with a timeout."""
    start_time = time.time()
    received_data = b""
    # Clear the RX window and make a dummy read to make sure we're starting fresh
    fldigi_client.text.clear_rx()
    fldigi_client.text.get_rx_data()
    while (time.time() - start_time) < timeout and fldigi_client.main.get_trx_state() != "RX":
        pass #wait for RX mode
    
    start_time = time.time() #reset start time for actual RX timeout
    consecutive_empty_reads = 0
    while (time.time() - start_time) < timeout:
        new_data = fldigi_client.text.get_rx_data()
        if new_data:
            received_data += new_data
            #fldigi_client.text.clear_rx()
            start_time = time.time() # Reset the timeout on each new char
            consecutive_empty_reads = 0
        else:
            consecutive_empty_reads += 1
            if consecutive_empty_reads >= 25 and len(received_data) > 0:
                break
        time.sleep(0.05) # Don't churn the CPU
    # Strip everything up until the first \r, then strip \r
    received_data = received_data[received_data.find(b"\r") + 1:]
    received_data = received_data.strip(b"\r")
    return received_data
    


def handle_client_connection(conn, fldigi_client, is_sender):
    """Handles communication with the other instance."""
    try:
        conn.setblocking(0)  # Set the connection to non-blocking
        conn.settimeout(30)  # Set a timeout of 30 seconds for the connection

        if is_sender:
            for _ in range(NUM_PACKETS):
                ready = select.select([conn], [conn], [], 1)  # Check for both read and write readiness with a timeout
                
                if ready[1]: # Socket is ready to write
                    data_chars = generate_random_hex_chars(PACKET_SIZE // 8)
                    sent_data = data_chars.encode('utf-8') # consistent type (bytes) for sending.
                    conn.sendall(sent_data)
                    logger.info(f"Sent chars over network: {sent_data}")

                    send_data(fldigi_client, data_chars, TX_DELAY)
                    
                    # Wait for the all clear to send the next packet
                    while True:
                        ready = select.select([conn], [], [], 1)
                        if ready[0]:
                            try:
                                ack = conn.recv(3) # Expecting b"ACK"
                                if ack == b"ACK":
                                    break
                            except socket.error:
                                 logger.warning("Socket Error, attempting to move on")
                                 break
                            
                        time.sleep(0.1)
                else:
                    logger.warning("Sender socket not ready to write, skipping packet.")
                time.sleep(0.1) # a small delay to prevent a tight loop.

            # Send a signal to the receiver indicating that all packets have been sent
            conn.sendall(b"DONE")
            logger.info("Sent DONE signal to receiver.")

        else:  # Receiver
            all_expected_data = b""
            all_received_data = b""
            while True:
                ready = select.select([conn], [], [], 1)  # Check for read readiness with a timeout
                if ready[0]: #socket is ready to read
                    data = conn.recv(PACKET_SIZE // 8) # We are sending bytes over the network
                    if data == b"DONE":
                        logger.info("Received DONE signal from sender.")
                        break
                    logger.info(f"Received chars over network: {data}")
                    if not data:
                        logger.error("Receiver: No data received on socket. Connection closed?")
                        break

                    expected_chars = data.decode('utf-8', errors='ignore')
                    all_expected_data += expected_chars.encode('utf-8')

                    received_text = receive_data(fldigi_client)
                    received_chars = received_text
                    # If received text is empty, lower the Squelch by 5
                    if len(received_text) == 0:
                        fldigi_client.main.squelch_level -= 5
                        logger.info(f"Lowering Squelch to {fldigi_client.main.squelch_level}")
                    all_received_data += received_chars

                    logger.info(f"Received over radio: {received_text}")

                    conn.sendall(b"ACK")  # Send ACK after processing each packet.
                else:
                    logger.warning("Receiver socket not ready to read, skipping packet.")
                time.sleep(0.1) # a small delay to prevent a tight loop.

            # Compare all received data after the sender is done
            ber = bit_error_rate(all_expected_data.decode('utf-8', errors='ignore'), all_received_data.decode('utf-8', errors='ignore'))
            logger.info(f"Expected data: {all_expected_data.decode('utf-8', errors='ignore')}")
            logger.info(f"Received data: {all_received_data.decode('utf-8', errors='ignore')}")
            logger.info(f"Overall Bit Error Rate: {ber:.4f}")
    except (BrokenPipeError, ConnectionResetError) as e:
        logger.error(f"Connection error: {e}")
    finally:
        conn.close()
        logger.info("Connection closed.")


def start_server(fldigi_client, is_sender):
    """Starts the server to listen for connections."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow address reuse
    server_socket.bind(('', PORT))
    server_socket.listen(1)
    logger.info(f"Listening on port {PORT}")

    conn, addr = server_socket.accept()
    logger.info(f"Connected by {addr}")
    handle_client_connection(conn, fldigi_client, is_sender)
    server_socket.close()

def connect_to_server(fldigi_client, is_sender, ip_address):
    """Connects to the server."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((ip_address, PORT))
        logger.info(f"Connected to {ip_address}:{PORT}")
        handle_client_connection(client_socket, fldigi_client, is_sender)
    except ConnectionRefusedError:
        logger.critical(f"Connection refused. Ensure the other instance is running and listening as a server on {ip_address}:{PORT}")
        sys.exit(1)  # Exit the program if connection fails
    finally:
        client_socket.close()


def main():
    """Default main function to initialize fldigi and start the communication."""

    if len(sys.argv) < 2 or sys.argv[1] not in ('send', 'receive'):
        print("Usage: python " + sys.argv[0] + " <send|receive>")
        sys.exit(1)

    is_sender = sys.argv[1] == 'send'

    # Initialize the fldigi client
    try:
        # if receive, port 7363
        # if send, port 7362
        fldigi = pyfldigi.Client('localhost', 7363 if is_sender else 7362)
        # set tx timeout to 9 seconds
        fldigi.txmonitor.xmit_timeout = 9
        # turn off AFC
        fldigi.main.afc = False
    except ConnectionRefusedError:
        logger.critical("Connection refused. Ensure fldigi is running and connected.")
        sys.exit(1)
    fldigi.modem.name = MODE
    fldigi.modem.carrier = CARRIER_FREQ
    fldigi.main.squelch_level = SQUELCH
    # Clear the receive and send windows
    fldigi.text.clear_rx()
    fldigi.text.clear_tx()

    # Start server or connect to server based on command-line argument
    if is_sender:
        # Give the receiver a chance to start up
        time.sleep(2)
        thread = threading.Thread(target=connect_to_server, args=(fldigi, is_sender, ip_address))
        thread.start()
    else:
        thread = threading.Thread(target=start_server, args=(fldigi, is_sender, ip_address))
        thread.start()

    thread.join() # Wait for send/receive to complete

    logger.info("Test complete.")


def makeMeasurement(is_sender, timestamp, ip):
    """Runs the experiment in headless mode without relying on command line arguments."""
    ip_address = ip
    # Initialize the fldigi client
    try:
        # if receive, port 7363
        # if send, port 7362
        fldigi = pyfldigi.Client('localhost', 7362)
        # set tx timeout to 9 seconds
        fldigi.txmonitor.xmit_timeout = 9
        # turn off AFC
        fldigi.main.afc = False
    except ConnectionRefusedError:
        logger.critical("Connection refused. Ensure fldigi is running and connected.")
        sys.exit(1)
    fldigi.modem.name = MODE
    fldigi.modem.carrier = CARRIER_FREQ
    fldigi.main.squelch_level = SQUELCH
    # Clear the receive and send windows
    fldigi.text.clear_rx()
    fldigi.text.clear_tx()

    # Start server or connect to server based on the is_sender parameter
    if is_sender:
        thread = threading.Thread(target=connect_to_server, args=(fldigi, is_sender, ip_address))
        thread.start()
    else:
        thread = threading.Thread(target=start_server, args=(fldigi, is_sender, ip_address))
        thread.start()

    thread.join() # Wait for send/receive to complete

    logger.info("Test complete.")

    # Connect to MongoDB and save the results
    try:
        # MongoDB connection details
        mongo_client = MongoClient(os.environ["MONGODB_URI"])
        db = mongo_client['Bera']
        collection = db['Radio']
                
        # Create document with test results
        result_doc = {
            'timestamp': timestamp,
            'mode': MODE,
            'bitsPerPacket': PACKET_SIZE,
            'numPackets': NUM_PACKETS,
            'bitErrorRate': ber,
            'expectedData': all_expected_data.decode('utf-8', errors='ignore'),
            'receivedData': all_received_data.decode('utf-8', errors='ignore')
        }
                
        # Insert the document into the collection
        result = collection.insert_one(result_doc)
        logger.info(f"Results saved to MongoDB with ID: {result.inserted_id}")
    except Exception as e:
        logger.error(f"Failed to save results to MongoDB: {e}")

# Example usage of headless_mode function
# headless_mode(True, datetime.now(tz=pytz.utc))
if __name__ == "__main__":
    main()
