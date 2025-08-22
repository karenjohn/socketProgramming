import socket
import threading
import time
import os

# Manually specify the Seeder's IP address
SEEDER_IP = "196.24.182.198"  # Replace with actual Seeder IP
SEEDER_PORT = 6000
SeederAddress = (SEEDER_IP, SEEDER_PORT)
TrackerAddress = ('196.42.124.105', 5647)  # Replace with Tracker's actual IP
FileName = "Sample.txt"
ChunkSize = 1024
chunks = []  # Store chunk names globally

def SplitFile():
    """Splits the file into chunks before serving and stores them."""
    global chunks
    chunks = []  # Reset chunk list

    if not os.path.exists(FileName):
        print(f"[Seeder OUTPUT] Error: {FileName} not found.")
        return

    with open(FileName, "rb") as file:
        chunk_id = 0
        while True:
            chunk = file.read(ChunkSize)
            if not chunk:
                break
            chunk_filename = f"{FileName}_chunk{chunk_id}"
            with open(chunk_filename, "wb") as chunk_file:
                chunk_file.write(chunk)
            chunks.append(chunk_filename)
            print(f"[Seeder OUTPUT] Created chunk: {chunk_filename}")
            chunk_id += 1

    print(f"[Seeder OUTPUT] Total chunks created: {len(chunks)}")

def RegisterWithTracker():
    """Registers this seeder with the tracker."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        msg = f"peer_Register:{SEEDER_IP}:{SEEDER_PORT}"
        sock.sendto(msg.encode(), TrackerAddress)
        print(f"[Seeder OUTPUT] Seeder registered with tracker at {SEEDER_IP}:{SEEDER_PORT}")
    except Exception as e:
        print(f"[Seeder OUTPUT] Error registering with tracker: {e}")
    finally:
        sock.close()

def SendAliveMessages():
    """Sends periodic alive messages to the tracker."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        try:
            sock.sendto(f"ALIVE:{SEEDER_IP}:{SEEDER_PORT}".encode(), TrackerAddress)
            print("[Seeder OUTPUT] Sent alive message to tracker.")
            time.sleep(5)
        except Exception as e:
            print(f"[Seeder OUTPUT] Error sending alive message: {e}")
            break
    sock.close()

def HandleFileRequests(conn):
    """Handles file chunk requests from a leecher."""
    try:
        request = conn.recv(1024).decode().strip()
        print(f"[Seeder OUTPUT] Received request: {request}")

        if request == "CHUNK_COUNT":
            # ✅ New command to return the number of chunks
            response = str(len(chunks))
            conn.sendall(response.encode())
            print(f"[Seeder OUTPUT] Sent chunk count: {response}")

        elif request.startswith("GET"):
            chunk_filename = request.split()[1]

            if chunk_filename in chunks:  # ✅ Check global chunk list
                with open(chunk_filename, "rb") as f:
                    chunk_data = f.read()
                    conn.sendall(chunk_data)  # ✅ Send full chunk before closing connection
                    print(f"[Seeder OUTPUT] Sent chunk {chunk_filename} to Leecher")
            else:
                print(f"[Seeder OUTPUT] Chunk {chunk_filename} does not exist! Sending error message.")
                conn.sendall(b"ERROR: Chunk not found")
    except Exception as e:
        print(f"[Seeder OUTPUT] Error handling file request: {e}")
    finally:
        conn.close()

def StartSeeder():
    """Starts the Seeder process."""
    RegisterWithTracker()
    threading.Thread(target=SendAliveMessages, daemon=True).start()

    # Split the file into chunks
    SplitFile()  # ✅ Ensure `chunks` is properly initialized
    if not chunks:
        print("[Seeder OUTPUT] No file chunks were created. Check if the file exists.")
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(SeederAddress)
    sock.listen(5)

    print(f"[Seeder OUTPUT] Seeder running on {SEEDER_IP}:{SEEDER_PORT} and listening for requests.")

    while True:
        conn, addr = sock.accept()
        print(f"[Seeder OUTPUT] Connection from {addr}")
        threading.Thread(target=HandleFileRequests, args=(conn,)).start()

if __name__ == "__main__":
    StartSeeder()
