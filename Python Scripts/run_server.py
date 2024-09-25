# from gevent.pywsgi import WSGIServer
from waitress import serve
from server_app import app
import time

# http_server = WSGIServer(('0.0.0.0',6050), app)
# http_server.serve_forever()
def run_my_server():
    while True:
        try:
            serve(app, port=6050, host="0.0.0.0", threads=4)
        except Exception as e:
            print(f"Encountered exception: {e}")
            time.sleep(2)

if __name__ == "__main__":
    run_my_server()