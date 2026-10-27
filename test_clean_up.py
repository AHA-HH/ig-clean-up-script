import json
import tempfile
import unittest
from pathlib import Path

from clean_up import compare, username_of


def entry(value=None, title=None, href=None):
    item = {k: v for k, v in {"value": value, "href": href}.items() if v}
    e = {"string_list_data": [item]}
    if title:
        e["title"] = title
    return e


class UsernameTests(unittest.TestCase):
    def test_value_form(self):
        self.assertEqual(username_of(entry("bob", href="https://www.instagram.com/bob/")), ("bob", "https://www.instagram.com/bob"))

    def test_title_form(self):
        self.assertEqual(username_of(entry(title="Bob", href="https://www.instagram.com/_u/Bob"))[0], "Bob")

    def test_href_only(self):
        self.assertEqual(username_of(entry(href="https://www.instagram.com/_u/bob/"))[0], "bob")

    def test_malformed(self):
        for bad in [None, {}, {"string_list_data": []}, entry(value="  ")]:
            self.assertIsNone(username_of(bad)[0])


class CompareTests(unittest.TestCase):
    def test_not_following_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            lists = Path(tmp) / "connections" / "followers_and_following"
            lists.mkdir(parents=True)
            # followers split across two files, old value-style records, mixed case and @
            (lists / "followers_1.json").write_text(json.dumps([entry("@Bob"), entry("carol")]))
            (lists / "followers_2.json").write_text(json.dumps([entry("dave"), {}]))
            # following uses the newer title-style records, with a duplicate
            (lists / "following.json").write_text(json.dumps({"relationships_following": [
                entry(title="bob"), entry(title="Zed"), entry(title="carol"), entry(title="alice"), entry(title="ALICE"),
            ]}))
            report = compare(Path(tmp))
        self.assertEqual([a["username"] for a in report["accounts"]], ["alice", "Zed"])
        self.assertEqual(report["counts"], {"following": 4, "followers": 3, "not_following_back": 2})
        self.assertEqual(report["warnings"], ["followers: skipped 1 malformed record(s)"])


if __name__ == "__main__":
    unittest.main()
