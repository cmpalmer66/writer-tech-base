import re
import unittest

from tools.log_viewer import build_records, preprocess_lines


class LogViewerTests(unittest.TestCase):
    def test_hash_aliases_are_stable(self):
        lines = [
            "[LC][Thing][12345] Create\n",
            "HashCode=12345 again\n",
            "[LC][Thing][67890] Create\n",
        ]
        processed = preprocess_lines(lines)
        self.assertIn("[ Alice ]", processed[0])
        self.assertIn("HashCode=Alice", processed[1])
        self.assertIn("[ Bob ]", processed[2])

    def test_include_and_exclude_regex(self):
        lines = [
            "[LC][A] keep\n",
            "[LC][FormField] drop\n",
            "[XYZ] drop\n",
        ]
        processed = preprocess_lines(lines)
        include = re.compile(r"^(?=.*\[LC\]).*$")
        exclude = re.compile(r"\[FormField\]")
        records = build_records(processed, include, exclude)
        included = [r.text for r in records if r.included]
        self.assertEqual(included, ["[LC][A] keep"])


if __name__ == "__main__":
    unittest.main()
