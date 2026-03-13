from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from stats import top_10_ips, protocol_breakdown, packets_per_minute, total_packet_count, average_packet_size, recent_packets
from capture import start_capture, stop_capture

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/stats')
def get_stats(limit: int = 100):
    return {
        'top_10_ips': top_10_ips(),
        'protocol_breakdown': protocol_breakdown(),
        'packets_per_minute': packets_per_minute(),
        'total_packets': total_packet_count(),
        'average_packet_size': average_packet_size(),
        'recent_packets': recent_packets(limit),
    }

@app.post('/capture/start')
def capture_start():
    return start_capture()

@app.post('/capture/stop')
def capture_stop():
    return stop_capture()


