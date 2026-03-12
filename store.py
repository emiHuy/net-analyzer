from sqlalchemy import create_engine, insert, delete, Table, Column, String, Integer, DateTime, MetaData

engine = create_engine('sqlite:///packets.db')
metadata = MetaData()

# Define table w/ columns and data types
packet_table = Table(
    'packets', metadata,
    Column('id', Integer, primary_key=True),
    Column('src_ip', String),
    Column('dst_ip', String),
    Column('protocol', Integer),
    Column('size', Integer),
    Column('timestamp', DateTime),
)
# Create table in database
metadata.create_all(engine)

# Stores packet in database
def store_packet(packet):
    with engine.connect() as conn:
        conn.execute(insert(packet_table).values(
            src_ip=packet['src'], 
            dst_ip=packet['dst'], 
            protocol=packet['protocol'],
            size=packet['size'],
            timestamp=packet['timestamp'],
        ))
        conn.commit()

# Deletes all packet data
def clear_packets():
    with engine.connect() as conn:
        conn.execute(delete(packet_table))
        conn.commit()

clear_packets()