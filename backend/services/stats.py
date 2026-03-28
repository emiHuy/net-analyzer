from sqlalchemy import select, func
from db import engine
from db.models import packet_table
from db.packets import get_packets, count_packets
import ipaddress

LOCAL_NETWORKS = [
    ipaddress.ip_network('192.168.0.0/16'),
    ipaddress.ip_network('10.0.0.0/8'),
    ipaddress.ip_network('172.16.0.0/12'),
]

def _is_local(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
        if addr.is_multicast:
            return False
        for network in LOCAL_NETWORKS:
            if addr in network:
                # exclude network address and broadcast address
                if addr == network.network_address or addr == network.broadcast_address:
                    return False
                return True
        return False
    except ValueError:
        return False
    

def top_10_ips(session_id: int, limit: int = 10) -> list[dict]:
    query = (
        select(packet_table.c.src_ip, packet_table.c.dst_ip)
        .where(packet_table.c.session_id == session_id)
    )
    with engine.connect() as conn:
        results = conn.execute(query).fetchall()

    counts = {}
    for r in results:
        src = r._mapping['src_ip']
        dst = r._mapping['dst_ip']
        if _is_local(src):
            counts[src] = counts.get(src, 0) + 1
        if _is_local(dst):
            counts[dst] = counts.get(dst, 0) + 1
    sorted_ips = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [{'ip': ip, 'total': total} for ip, total in sorted_ips[:limit]]


def protocol_breakdown(session_id: int) -> list[dict]:
    query = (
        select(packet_table.c.protocol, func.count().label('total'))
        .where(packet_table.c.session_id == session_id)
        .group_by(packet_table.c.protocol)
    )
    with engine.connect() as conn:
        results = conn.execute(query).fetchall()
    return [{'protocol': r[0], 'total': r[1]} for r in results]


def packets_per_minute(session_id: int) -> list[dict]:
    minute = func.strftime('%Y-%m-%d %H:%M', packet_table.c.timestamp)
    query = (
        select(minute, func.count().label('packets_per_min'))
        .where(packet_table.c.session_id == session_id)
        .group_by(minute)
        .order_by(minute.asc())
    )
    with engine.connect() as conn:
        results = conn.execute(query).fetchall()
    return [{'time': r[0], 'total': r[1]} for r in results]


def average_packet_size(session_id: int) -> float | None:
    query = (
        select(func.avg(packet_table.c.size))
        .where(packet_table.c.session_id == session_id)
    )
    with engine.connect() as conn:
        return conn.execute(query).fetchone()[0]
    

def active_hosts(session_id: int) -> int:
    query = (
        select(packet_table.c.src_ip, packet_table.c.dst_ip)
        .where(packet_table.c.session_id == session_id)
    )
    with engine.connect() as conn:
        results = conn.execute(query).fetchall()
    
    unique_hosts = set()
    for r in results:
        src = r._mapping['src_ip']
        dst = r._mapping['dst_ip']
        if _is_local(src):
            unique_hosts.add(src)
        if _is_local(dst):
            unique_hosts.add(dst)
    return len(unique_hosts)
    

def get_all_stats(session_id: int, limit: int = 50) -> dict:
    return {
        'top_10_ips':          top_10_ips(session_id),
        'protocol_breakdown':  protocol_breakdown(session_id),
        'packets_per_minute':  packets_per_minute(session_id),
        'total_packets':       count_packets(session_id),
        'average_packet_size': average_packet_size(session_id),
        'recent_packets':      get_packets(session_id, limit),
        'active_hosts':        active_hosts(session_id),
    }
