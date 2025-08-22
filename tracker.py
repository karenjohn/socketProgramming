import socket
import threading
import json

# Manually specify the Tracker's IP address
TRACKER_IP = "196.24.182.198"  # Replace with your actual Tracker IP
TRACKER_PORT = 12000
TrackerAddress = (TRACKER_IP, TRACKER_PORT)
Seeders = {}

def HandlePeerMessage(data, addr, sock):
    """Handles messages from peers (seeders and leechers)."""
    message = data.decode().strip()
    print(f"[Tracker OUTPUT] Received message from {addr}: {message}")

    parts = message.split(":")
    
    if len(parts) < 2 and message != "peer_List":
        print(f"[Tracker OUTPUT] Invalid message format from {addr}: {message}")
        return
    
    if message == "peer_List":
        print(f"[Tracker OUTPUT] Sending seeder list to {addr}")
        peer_list = list(Seeders.values())
        response = json.dumps({"PEERS": peer_list})
        sock.sendto(response.encode(), addr)
    
    elif parts[0] == "peer_Register":
        peer_ip, peer_port = parts[1], parts[2]
        Seeders[addr] = f"{peer_ip}:{peer_port}"
        print(f"[Tracker OUTPUT] Seeder registered: {peer_ip}:{peer_port}")
    
    elif parts[0] == "ALIVE":
        print(f"[Tracker OUTPUT] Alive message received from: {addr}")

    else:
        print(f"[Tracker OUTPUT] Invalid message from {addr}: {message}")

def StartTracker():
    """Starts the Tracker server."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(TrackerAddress)
    print(f"[Tracker OUTPUT] Tracker running on {TRACKER_IP}:{TRACKER_PORT} and waiting for connections.")

    while True:
        data, addr = sock.recvfrom(1024)
        threading.Thread(target=HandlePeerMessage, args=(data, addr, sock)).start()

if __name__ == "__main__":
    StartTracker()
