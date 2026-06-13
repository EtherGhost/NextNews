import base64
import json
import os
import pathlib
import ssl
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request


ROOT = pathlib.Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env.test.local"
API_PREFIX = "/index.php/apps/news/api/v1-2"
TEST_PREFIX = "NextNewsLiveTest-"


def load_env_file():
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


load_env_file()


@unittest.skipUnless(os.environ.get("NEXTNEWS_RUN_LIVE_TESTS") == "1", "live tests are opt-in")
class LiveNextcloudNewsApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = os.environ["NEXTNEWS_TEST_SERVER"].rstrip("/")
        cls.username = os.environ["NEXTNEWS_TEST_USERNAME"]
        cls.password = os.environ["NEXTNEWS_TEST_APP_PASSWORD"]
        cls.feed_url = os.environ.get("NEXTNEWS_TEST_FEED_URL", "https://xkcd.com/rss.xml")
        cls.context = ssl.create_default_context()

    def setUp(self):
        self.created_feed_ids = []
        self.created_folder_ids = []
        self.cleanup_test_artifacts()

    def tearDown(self):
        self.cleanup_test_artifacts()

    @classmethod
    def request(cls, method, path, payload=None, form=None):
        url = cls.server + API_PREFIX + path
        data = None
        request = urllib.request.Request(url, method=method)
        token = base64.b64encode(f"{cls.username}:{cls.password}".encode("utf-8")).decode("ascii")
        request.add_header("Authorization", f"Basic {token}")
        request.add_header("Accept", "application/json")

        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            request.add_header("Content-Type", "application/json")
        elif form is not None:
            data = urllib.parse.urlencode(form).encode("utf-8")
            request.add_header("Content-Type", "application/x-www-form-urlencoded")

        try:
            with urllib.request.urlopen(request, data=data, context=cls.context, timeout=30) as response:
                body = response.read().decode("utf-8")
                return response.status, cls.parse_json(body)
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8")
            return error.code, cls.parse_json(body)

    @staticmethod
    def parse_json(body):
        if not body:
            return {}
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {"raw": body}

    def assert_success(self, status, body=None):
        self.assertGreaterEqual(status, 200, body)
        self.assertLess(status, 300, body)

    def folders(self):
        status, body = self.request("GET", "/folders")
        self.assert_success(status, body)
        return body if isinstance(body, list) else body.get("folders", [])

    def feeds(self):
        status, body = self.request("GET", "/feeds")
        self.assert_success(status, body)
        return body if isinstance(body, list) else body.get("feeds", [])

    def items_for_feed(self, feed_id):
        path = f"/items?batchSize=10&offset=0&type=0&id={feed_id}&getRead=true&oldestFirst=false"
        status, body = self.request("GET", path)
        self.assert_success(status, body)
        return body.get("items", [])

    def create_folder(self, name):
        status, body = self.request("POST", "/folders", payload={"name": name})
        self.assert_success(status, body)
        for folder in self.folders():
            if folder.get("name") == name:
                folder_id = int(folder["id"])
                self.created_folder_ids.append(folder_id)
                return folder_id
        self.fail(f"Created folder was not returned by GET /folders: {body}")

    def rename_folder(self, folder_id, name):
        status, body = self.request("PUT", f"/folders/{folder_id}", payload={"name": name})
        self.assert_success(status, body)
        self.assertTrue(any(int(folder["id"]) == folder_id and folder.get("name") == name for folder in self.folders()))

    def add_feed(self, feed_url, folder_id):
        status, body = self.request("POST", "/feeds", form={"url": feed_url, "folderId": folder_id})
        self.assert_success(status, body)
        for _ in range(10):
            for feed in self.feeds():
                if int(feed.get("folderId") or 0) == int(folder_id) and feed.get("url") == feed_url:
                    feed_id = int(feed["id"])
                    self.created_feed_ids.append(feed_id)
                    return feed_id
            time.sleep(1)
        self.fail("Created feed was not returned by GET /feeds")

    def rename_feed(self, feed_id, title):
        status, body = self.request("PUT", f"/feeds/{feed_id}/rename", payload={"feedTitle": title})
        self.assert_success(status, body)
        self.assertTrue(any(int(feed["id"]) == feed_id and feed.get("title") == title for feed in self.feeds()))

    def move_feed(self, feed_id, folder_id):
        status, body = self.request("PUT", f"/feeds/{feed_id}/move", payload={"folderId": folder_id})
        self.assert_success(status, body)
        self.assertTrue(any(int(feed["id"]) == feed_id and int(feed.get("folderId") or 0) == folder_id for feed in self.feeds()))

    def delete_feed(self, feed_id):
        status, body = self.request("DELETE", f"/feeds/{feed_id}")
        self.assertIn(status, (200, 204, 404), body)
        self.created_feed_ids = [value for value in self.created_feed_ids if value != feed_id]

    def delete_folder(self, folder_id):
        status, body = self.request("DELETE", f"/folders/{folder_id}")
        self.assertIn(status, (200, 204, 404), body)
        self.created_folder_ids = [value for value in self.created_folder_ids if value != folder_id]

    def cleanup_test_artifacts(self):
        try:
            feeds = self.feeds()
            folders = self.folders()
        except Exception:
            return

        test_folder_ids = {
            int(folder["id"])
            for folder in folders
            if str(folder.get("name", "")).startswith(TEST_PREFIX)
        }
        for feed in feeds:
            feed_id = int(feed["id"])
            title = str(feed.get("title", ""))
            folder_id = int(feed.get("folderId") or 0)
            if feed_id in self.created_feed_ids or folder_id in test_folder_ids or title.startswith(TEST_PREFIX):
                self.request("DELETE", f"/feeds/{feed_id}")

        for folder in self.folders():
            folder_id = int(folder["id"])
            if folder_id in self.created_folder_ids or str(folder.get("name", "")).startswith(TEST_PREFIX):
                self.request("DELETE", f"/folders/{folder_id}")

    def test_status_folders_feeds_and_items_are_accessible(self):
        for path, key in [
            ("/status", None),
            ("/folders", "folders"),
            ("/feeds", "feeds"),
            ("/items?batchSize=10&offset=0&type=3&id=0&getRead=true&oldestFirst=false", "items"),
        ]:
            status, body = self.request("GET", path)
            self.assert_success(status, body)
            if key:
                self.assertIn(key, body)

    def test_folder_feed_item_state_lifecycle(self):
        suffix = str(int(time.time()))
        folder_a = self.create_folder(TEST_PREFIX + suffix + "-A")
        self.rename_folder(folder_a, TEST_PREFIX + suffix + "-A-renamed")
        folder_b = self.create_folder(TEST_PREFIX + suffix + "-B")

        feed_id = self.add_feed(self.feed_url, folder_a)
        self.rename_feed(feed_id, TEST_PREFIX + suffix + "-Feed")
        self.move_feed(feed_id, folder_b)

        items = self.items_for_feed(feed_id)
        if items:
            item = items[0]
            item_id = int(item["id"])
            guid_hash = item.get("guidHash", "")
            status, body = self.request("PUT", "/items/read/multiple", payload={"items": [item_id]})
            self.assert_success(status, body)
            status, body = self.request("PUT", "/items/unread/multiple", payload={"items": [item_id]})
            self.assert_success(status, body)

            if guid_hash:
                star_payload = {"items": [{"feedId": feed_id, "guidHash": guid_hash}]}
                status, body = self.request("PUT", "/items/star/multiple", payload=star_payload)
                self.assert_success(status, body)
                status, body = self.request("PUT", "/items/unstar/multiple", payload=star_payload)
                self.assert_success(status, body)
        else:
            self.skipTest("Test feed did not expose items quickly enough for read/star live checks")

        self.delete_feed(feed_id)
        self.delete_folder(folder_a)
        self.delete_folder(folder_b)


if __name__ == "__main__":
    unittest.main(verbosity=2)
