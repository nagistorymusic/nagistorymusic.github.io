"""確認用のローカルサーバー（動画のシーク・ループに必要な Range リクエストに対応）

使い方:  python tools/dev-server.py   →  http://localhost:8765/design/concepts/
"""
import os
import re
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8765


class RangeHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        self.range = None
        m = re.match(r"bytes=(\d*)-(\d*)$", self.headers.get("Range", ""))
        path = self.translate_path(self.path)
        if not m or not os.path.isfile(path):
            return super().send_head()
        size = os.path.getsize(path)
        start = int(m.group(1)) if m.group(1) else max(0, size - int(m.group(2)))
        end = int(m.group(2)) if m.group(1) and m.group(2) else size - 1
        end = min(end, size - 1)
        if start > end:
            self.send_error(416)
            return None
        f = open(path, "rb")
        f.seek(start)
        self.range = end - start + 1
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(self.range))
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()
        return f

    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def copyfile(self, source, outputfile):
        if not getattr(self, "range", None):
            return super().copyfile(source, outputfile)
        left = self.range
        while left > 0:
            chunk = source.read(min(64 * 1024, left))
            if not chunk:
                break
            try:
                outputfile.write(chunk)
            except (BrokenPipeError, ConnectionResetError):
                break
            left -= len(chunk)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    handler = partial(RangeHandler, directory=ROOT)
    print(f"http://localhost:{PORT}/design/concepts/")
    ThreadingHTTPServer(("127.0.0.1", PORT), handler).serve_forever()
