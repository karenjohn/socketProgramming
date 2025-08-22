import socket
import json
import time
import os

# Manually specify the Leecher's IP address
LEECHER_IP = "196.47.232.155"  # Replace with actual Leecher IP
TrackerAddress = ('196.42.124.105', 5647)  # Replace with Tracker's actual IP
FileName = "Sample.txt"
OutputFile = f"Downloaded_{FileName}"
ChunkSize = 1024

def RequestPeer():
    """Request a list of active seeders from the Tracker."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        print("[Leecher OUTPUT] Sending 'peer_List' request to tracker...")
        sock.sendto("peer_List".encode(), TrackerAddress)

        data, _ = sock.recvfrom(1024)
        response = data.decode()
        print(f"[Leecher OUTPUT] Received peer list response: {response}")

        try:
            peers = json.loads(response).get("PEERS", [])
            return peers
        except json.JSONDecodeError as e:
            print(f"[Leecher OUTPUT] Error decoding peer list: {e}")
            return []
    except Exception as e:
        print(f"[Leecher OUTPUT] Error requesting peers: {e}")
        return []
    finally:
        sock.close()

def GetTotalChunks():
    """Requests the Seeder to determine how many chunks exist."""
    peers = RequestPeer()
    if not peers:
        print("[Leecher OUTPUT] No seeders found.")
        return 0

    # Ask the first available seeder
    for peer in peers:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            peer_host, peer_port = peer.split(":")
            peer_port = int(peer_port)

            print(f"[Leecher OUTPUT] Requesting total chunks from Seeder {peer_host}:{peer_port}...")
            sock.connect((peer_host, peer_port))
            sock.sendall(b"CHUNK_COUNT")  #  New command to get chunk count
            response = sock.recv(1024).decode().strip()
            return int(response)
        except Exception as e:
            print(f"[Leecher OUTPUT] Error requesting chunk count: {e}")
        finally:
            sock.close()
    
    return 0

def RequestChunk(peer, chunk_id):
    """Request a specific file chunk from a Seeder via TCP."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        peer_host, peer_port = peer.split(":")
        peer_port = int(peer_port)

        print(f"[Leecher OUTPUT] Connecting to seeder {peer_host}:{peer_port} to request chunk {chunk_id}...")
        sock.connect((peer_host, peer_port))

        chunk_filename = f"{FileName}_chunk{chunk_id}"
        sock.sendall(f"GET {chunk_filename}".encode())

        chunk_data = b""
        while True:
            data = sock.recv(1024)
            if not data:
                break
            chunk_data += data
        
        if b"ERROR: Chunk not found" in chunk_data:
            print(f"[Leecher OUTPUT] Chunk {chunk_id} not found on Seeder {peer_host}. Skipping.")
            return None

        print(f"[Leecher OUTPUT] Chunk {chunk_id} received from {peer_host}")
        return chunk_data
    except Exception as e:
        print(f"[Leecher OUTPUT] Error requesting chunk {chunk_id} from {peer}: {e}")
        return None
    finally:
        sock.close()

def DownloadFile():
    """Download chunks from active seeders."""
    total_chunks = GetTotalChunks()
    if total_chunks == 0:
        print("[Leecher OUTPUT] No valid chunks found. Stopping download.")
        return

    print(f"[Leecher OUTPUT] Downloading {total_chunks} chunks...")

    with open(OutputFile, "wb") as output_file:
        for chunk_id in range(total_chunks):  # ✅ Use actual number of chunks
            for peer in RequestPeer():
                chunk_data = RequestChunk(peer, chunk_id)
                if chunk_data:
                    output_file.write(chunk_data)
                    break
            else:
                print(f"[Leecher OUTPUT] Missing chunk {chunk_id}, skipping.")

    print(f"[Leecher OUTPUT] File {OutputFile} downloaded successfully!")

if __name__ == "__main__":
    DownloadFile()
