from scapy.all import sniff, IP
from datetime import datetime
from store import store_packet

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
    
sniff(prn=packet_callback, store=False, timeout=2000)
