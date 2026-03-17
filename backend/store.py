from sqlalchemy import create_engine, insert, delete, select, Table, Column, String, Integer, MetaData, func
from datetime import datetime
import os

# Determine database file location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "packets.db")

# Create SQLite database engine
engine = create_engine(f'sqlite:///{DB_PATH}')
metadata = MetaData()

# Table for capture sessions
session_table = Table(
    'sessions', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String, unique=True),
    Column('created_at', String),
)

# Table for captured packets
packet_table = Table(
    'packets', metadata,
    Column('id', Integer, primary_key=True),
    Column('session_id', Integer),
    Column('src_ip', String),
    Column('dst_ip', String),
    Column('protocol', Integer),
    Column('size', Integer),
    Column('timestamp', String),
)

# Create tables if they do not exist
metadata.create_all(engine)

def create_session(name: str) -> int:
    """Create a new capture session."""
    with engine.connect() as conn:
        result = conn.execute(insert(session_table).values(
            name=name,
            created_at=datetime.now().isoformat(),
        ))
        conn.commit()
        return result.lastrowid


def get_all_sessions():
    """Return all saved sessions."""
    query = (
        select(
            session_table.c.id,
            session_table.c.name,
            session_table.c.created_at,
            func.count(packet_table.c.id).label('packet_count')
        )
        .outerjoin(packet_table, packet_table.c.session_id == session_table.c.id)
        .group_by(session_table.c.id)
    )
    with engine.connect() as conn:
        results = conn.execute(query).fetchall()
    return [{'id': r[0], 'name': r[1], 'created_at': r[2], 'packet_count': r[3]} for r in results]


def clear_session(session_id: int):
    """Delete a session and its packets."""
    with engine.connect() as conn:
        conn.execute(delete(packet_table).where(packet_table.c.session_id == session_id))
        conn.execute(delete(session_table).where(session_table.c.id == session_id))
        conn.commit()


def store_packet(packet, session_id: int):
    """Store packet metadata."""
    with engine.connect() as conn:
        conn.execute(insert(packet_table).values(
            session_id=session_id,
            src_ip=packet['src_ip'],
            dst_ip=packet['dst_ip'],
            protocol=packet['protocol'],
            size=packet['size'],
            timestamp=packet['timestamp'],
        ))
        conn.commit()
