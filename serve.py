from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = 8000

class MyHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Optional: Add headers to prevent caching during development
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

def run():
    # ThreadingHTTPServer spawns a new thread for every incoming request
    server = ThreadingHTTPServer(('0.0.0.0', PORT), MyHTTPRequestHandler)
    print(f"Serving concurrently on http://localhost:{PORT} ...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
        server.server_close()

if __name__ == '__main__':
    run()
