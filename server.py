from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess

PORT = 9999

#valid server url paths
URL_VIS="/visualization.html"
URL_NEW_VIS="/new-visualization"
valid_paths = ["/", "/index.html", "/incidences", URL_VIS, URL_NEW_VIS]

def make_response(path: str):
    if path.endswith("/"):
        path = path + "index.html"
    with open("."+path, 'r') as file:
        data = file.read()
        if path == "/incidences":
            return "Incidences where we could not reach a remote server:<br><br>"+str(data).replace('\n', "<br>")
        else:
            return str(data)

def on_pre_response(path: str):
    if path == URL_NEW_VIS:
        subprocess.call(["python", "buildplot.py"], stdout=subprocess.DEVNULL);
        path = URL_VIS
    return path

class ServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path in valid_paths:

            # hook to execute stuff before sending response
            # necessary e.g. for creating the newest visualization
            path = on_pre_response(self.path)

            RP = make_response(path)
            RP = str.encode(RP)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(RP)
            return

        self.send_response(404)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(str.encode(""))
        return

Handler = ServerHandler

httpd = HTTPServer(("", PORT), Handler)

print("serving at port", PORT)
httpd.serve_forever()
