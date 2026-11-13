import json
import threading
import time
import unittest
import urllib.request
from http.server import ThreadingHTTPServer

from tests.helpers import base
from stacksense.server import Handler


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.port = cls.srv.server_address[1]
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        time.sleep(0.2)

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()

    def get(self, path):
        return urllib.request.urlopen(f"http://127.0.0.1:{self.port}{path}", timeout=10)

    def test_index_served(self):
        self.assertIn("<html", self.get("/").read().decode().lower())

    def test_index_served_with_query_string_share_link(self):
        self.assertEqual(self.get("/?s=abc").status, 200)

    def test_unknown_path_is_404(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:
            self.get("/nope")
        self.assertEqual(cm.exception.code, 404)

    def test_api_returns_engine_result(self):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/api/recommend", data=json.dumps(base()).encode(), headers={"Content-Type": "application/json"}, method="POST")
        out = json.loads(urllib.request.urlopen(req, timeout=10).read())
        self.assertIn(out["status"], ("ok", "ok_with_warnings"))

    def test_api_bad_json_gives_invalid_input(self):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/api/recommend", data=b"{bad", method="POST")
        self.assertEqual(json.loads(urllib.request.urlopen(req, timeout=10).read())["status"], "invalid_input")


if __name__ == "__main__":
    unittest.main()
