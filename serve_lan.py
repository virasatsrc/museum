import http.server
import socketserver
import socket
import os

# Set working directory to the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

PORT = 8001

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    ip = get_ip()
    print(f"\nMuseum Gallery Server is running over HTTP!")
    print(f"--------------------------------------")
    print(f"Local Access:   http://localhost:{PORT}")
    print(f"LAN Access:     http://{ip}:{PORT}")
    print(f"--------------------------------------")
    print(f"Press Ctrl+C to stop the server.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.shutdown()
