"""
Kiểm thử Hạ tầng Mạng (Network Testing)
Dự án UDM_16 – Game Caro Trực Tuyến
"""

import pytest
import socket
import struct
import json
import threading
import time
from unittest.mock import MagicMock

# GIẢ LẬP HÀM NETWORK UTILS (Thay bằng import thực tế từ common.network_utils)
# from common.network_utils import receive_data, send_data

def receive_data(sock):
    """
    Hàm đọc dữ liệu an toàn với 4-byte header (Chống dính gói).
    Giả lập lại logic của common/network_utils.py để chạy test.
    """
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    return recvall(sock, msglen)

def recvall(sock, n):
    """Hàm helper đảm bảo đọc đủ n bytes từ socket stream"""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return bytes(data)

# MOCK SOCKET DÙNG CHO KIỂM THỬ GÓI TIN

class MockSocketStream:
    """Giả lập một TCP Socket Stream để test cơ chế cắt/ghép gói tin"""
    def __init__(self, byte_stream):
        self.byte_stream = byte_stream
        self.index = 0

    def recv(self, bufsize):
        if self.index >= len(self.byte_stream):
            return b''
        chunk = self.byte_stream[self.index : self.index + bufsize]
        self.index += len(chunk)
        return chunk

# 1. TEST DÍNH GÓI & PHÂN MẢNH TCP (PACKET STICKING & FRAGMENTATION)

def test_tcp_packet_sticking():
    """
    Kịch bản: 3 gói tin JSON đến cùng một lúc và dính liền thành 1 stream duy nhất.
    Kỳ vọng: receive_data bóc tách chuẩn xác thành 3 thông điệp riêng biệt.
    """
    msgs = [
        json.dumps({"action": "join", "user": "player1"}).encode('utf-8'),
        json.dumps({"action": "move", "x": 7, "y": 7}).encode('utf-8'),
        json.dumps({"action": "chat", "msg": "Hello!"}).encode('utf-8')
    ]
    
    # Đóng gói với 4-byte header (Big Endian Unsigned Int)
    stream_data = b''
    for msg in msgs:
        stream_data += struct.pack('>I', len(msg)) + msg

    # Đẩy toàn bộ cục stream bị dính vào MockSocket
    mock_sock = MockSocketStream(stream_data)

    # Đọc lần 1
    res1 = receive_data(mock_sock)
    assert json.loads(res1.decode('utf-8'))['action'] == "join"

    # Đọc lần 2
    res2 = receive_data(mock_sock)
    assert json.loads(res2.decode('utf-8'))['x'] == 7

    # Đọc lần 3
    res3 = receive_data(mock_sock)
    assert json.loads(res3.decode('utf-8'))['msg'] == "Hello!"

def test_tcp_packet_fragmentation():
    """
    Kịch bản: Gói tin bị xé nhỏ khi truyền qua mạng (TCP Fragmentation).
    Header 4 byte và Payload bị đến làm nhiều đợt.
    """
    msg = json.dumps({"action": "ping"}).encode('utf-8')
    packet = struct.pack('>I', len(msg)) + msg
    
    # Giả lập socket trả về dữ liệu bị cắt vụn từng byte một
    class FragmentedMockSocket:
        def __init__(self, data):
            self.data = data
            self.idx = 0
            
        def recv(self, bufsize):
            if self.idx >= len(self.data): return b''
            # Chỉ trả về 1 byte hoặc tối đa 2 bytes mỗi lần đọc
            chunk = self.data[self.idx : self.idx + 2]
            self.idx += len(chunk)
            return chunk

    mock_sock = FragmentedMockSocket(packet)
    res = receive_data(mock_sock)
    assert json.loads(res.decode('utf-8'))['action'] == "ping"

# 2. TEST TẢI & KẾT NỐI ĐỒNG THỜI (CONCURRENCY / LOAD TEST)

def dummy_tcp_server(host, port, stop_event):
    """Server giả lập đơn giản để nhận kết nối từ các luồng test tải"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(100)
    server.settimeout(0.5)

    clients = []
    while not stop_event.is_set():
        try:
            conn, addr = server.accept()
            clients.append(conn)
            # Tự động gửi phản hồi xác nhận
            msg = json.dumps({"status": "connected"}).encode('utf-8')
            conn.sendall(struct.pack('>I', len(msg)) + msg)
        except socket.timeout:
            continue

    for c in clients:
        c.close()
    server.close()

@pytest.mark.timeout(10)
def test_concurrent_connections():
    """
    Kịch bản: 50 clients kết nối đồng thời tới server trong cùng 1 thời điểm.
    Kỳ vọng: Server không bị crash, không bị nghẽn (deadlock) và phản hồi đủ 50 clients.
    """
    HOST, PORT = '127.0.0.1', 8888
    stop_event = threading.Event()
    
    # Khởi chạy server giả lập trên một luồng riêng
    server_thread = threading.Thread(target=dummy_tcp_server, args=(HOST, PORT, stop_event))
    server_thread.start()
    
    time.sleep(0.5) # Đợi server sẵn sàng

    connected_count = 0
    lock = threading.Lock()

    def client_task():
        nonlocal connected_count
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST, PORT))
            
            # Kiểm tra xem có nhận được dữ liệu phản hồi từ server không
            response = receive_data(client)
            if response and json.loads(response.decode('utf-8')).get("status") == "connected":
                with lock:
                    connected_count += 1
            client.close()
        except Exception:
            pass

    # Tạo 50 luồng (50 clients) tấn công/kết nối đồng thời
    threads = []
    for _ in range(50):
        t = threading.Thread(target=client_task)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Tắt server
    stop_event.set()
    server_thread.join()

    # Kiểm tra xem toàn bộ 50 clients có kết nối và nhận phản hồi thành công không
    assert connected_count == 50, f"Chỉ có {connected_count}/50 clients kết nối thành công."