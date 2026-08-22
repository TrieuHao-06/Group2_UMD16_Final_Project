# common/network_utils.py
import json

def send_message(sock, message_dict):
    """
    Chuyển Dictionary thành chuỗi JSON, gắn Header (4 bytes độ dài) và gửi qua Socket.
    """
    message_json = json.dumps(message_dict)
    message_bytes = message_json.encode('utf-8')
    message_length = len(message_bytes)
    
    # Ép độ dài thành 4 byte (big-endian)
    header = message_length.to_bytes(4, byteorder='big')
    sock.sendall(header + message_bytes)

def receive_message(sock):
    """
    Đọc 4 byte Header để biết độ dài, sau đó đọc đủ số byte payload và chuyển lại thành Dictionary.
    """
    try:
        # 1. Đọc 4 byte header
        header = sock.recv(4)
        if not header:
            return None
        
        message_length = int.from_bytes(header, byteorder='big')
        
        # 2. Đọc đủ số byte của payload (nội dung chính)
        chunks = []
        bytes_recd = 0
        while bytes_recd < message_length:
            chunk = sock.recv(min(message_length - bytes_recd, 4096))
            if chunk == b'':
                raise RuntimeError("Mất kết nối Socket")
            chunks.append(chunk)
            bytes_recd += len(chunk)
            
        message_bytes = b''.join(chunks)
        return json.loads(message_bytes.decode('utf-8'))
        
    except Exception as e:
        print(f"[NETWORK ERROR] Lỗi nhận tin: {e}")
        return None