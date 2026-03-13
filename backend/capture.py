from scapy.all import sniff, IP
import threading
from datetime import datetime
from store import store_packet

stop_event = threading.Event()
capture_thread = None

# Capture packets being sent to and from network
def packet_callback(packet):
    if IP in packet:
        # Get source IP, destination IP, and protocol from packet
        src = packet[IP].src
        dst = packet[IP].dst
        protocol = packet[IP].proto
        print(f'IP | {src} → {dst} | Protocol: {protocol}')

        # Store packet
        store_packet({
            'src_ip': src,
            'dst_ip': dst,
            'protocol': protocol,
            'size': len(packet),
            'timestamp': datetime.now().isoformat(),
            })

# Start capturing packets in its own thread
def start_capture():
    stop_event.clear()
    capture_thread = threading.Thread(target=lambda: sniff(prn=packet_callback, store=False, stop_filter=lambda x: stop_event.is_set()))
    capture_thread.start()
    return {'start_timestamp': datetime.now().isoformat()}

# Stop capturing packets
def stop_capture():
    stop_event.set()
    return {'stop_timestamp': datetime.now().isoformat()}