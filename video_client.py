
from PIL import Image, ImageTk
# video_client.py
import cv2
import socket
import pickle
import struct
import numpy as np
import threading

class VideoClient:
    def __init__(self):
        self.running = False
        self.current_socket = None
        self.current_frame = None
        self.frame_ready = threading.Event()
        self.connection_timeout = 3
        
    def connect(self, host, port=8089):
        if self.current_socket:
            self.disconnect()
            
        try:
            print(f"Connecting to camera on {host}...")
            self.current_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.current_socket.settimeout(self.connection_timeout)
            self.current_socket.connect((host, port))
            self.current_socket.settimeout(None)
            self.running = True
            threading.Thread(target=self.receive_video, daemon=True).start()
            print("Connected to camera server")
            return True
        except socket.timeout:
            print(f"Connection to {host} timed out")
            self.disconnect()
            return False
        except Exception as e:
            print(f"Failed to connect to camera on {host}: {e}")
            self.disconnect()
            return False
        
    def receive_video(self):
        data = b""
        payload_size = struct.calcsize("Q")
        
        while self.running:
            try:
                while len(data) < payload_size:
                    packet = self.current_socket.recv(4*1024)
                    if not packet:
                        print("No data received")
                        return
                    data += packet
                    
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q", packed_msg_size)[0]
                
                while len(data) < msg_size:
                    data += self.current_socket.recv(4*1024)
                    
                frame_data = data[:msg_size]
                data = data[msg_size:]
                
                # Decompress JPEG frame
                frame_buffer = pickle.loads(frame_data)
                frame = cv2.imdecode(np.frombuffer(frame_buffer, np.uint8), cv2.IMREAD_COLOR)
                if frame is not None:
                    self.current_frame = frame
                    self.frame_ready.set()
                else:
                    print("Failed to decode frame")
            except Exception as e:
                print(f"Error receiving video: {e}")
                break
                
        self.disconnect()
                
    def get_frame(self):
        if self.frame_ready.wait(timeout=1.0):
            self.frame_ready.clear()
            return self.current_frame.copy() if self.current_frame is not None else None
        return None
        
    def disconnect(self):
        print("Disconnecting video client")
        self.running = False
        if self.current_socket:
            try:
                self.current_socket.close()
            except:
                pass
            self.current_socket = None