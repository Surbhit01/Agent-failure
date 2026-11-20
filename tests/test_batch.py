import json
import unittest
from pathlib import Path


class TaskFileTests(unittest.TestCase):
    def test_tasks_well_formed(self):
        tasks = [json.loads(line) for line in Path("tasks/benign.jsonl").read_text().splitlines()]
        self.assertEqual(len(tasks), 20)
        self.assertEqual(len({t["id"] for t in tasks}), 20)  # ids are unique
        self.assertTrue(all(set(t) == {"id", "category", "prompt"} for t in tasks))


if __name__ == "__main__":
    unittest.main()
