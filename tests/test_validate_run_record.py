import tempfile
import unittest
from pathlib import Path

from scripts.validate_run_record import parse_fields, validate_run_record


VALID_RECORD = """# RUN-20261001-WF02-competitor-backlog

- Goal: Create an evidence-backed competitor backlog
- Workflow: WF02
- Automation level: L2
- Owner: youtube_workflow
- Supporting agents: youtube_data, content_bridge
- Status: COMPLETE
- Inputs: channel handles and keyword file
- Missing inputs: NONE
- Tools allowed: public API and local files
- Tools prohibited: paid bulk transcript
- Guardrail result: PASS
- Human approval required: NO - local output only
- Human approval status: NOT_REQUIRED
- Output paths: outputs/reports/competitor-backlog.md
- External action: NONE
- External action read-back: NOT_REQUIRED
- Feedback destination: Channel Brain
- Next owner/action: Alan reviews backlog
"""


class ValidateRunRecordTest(unittest.TestCase):
    def write_record(self, directory: str, name: str, content: str) -> Path:
        path = Path(directory) / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_parse_fields_normalizes_labels(self):
        fields = parse_fields(VALID_RECORD)
        self.assertEqual(fields["workflow"], "WF02")
        self.assertEqual(fields["automation level"], "L2")

    def test_accepts_valid_l2_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_record(
                tmp, "RUN-20261001-WF02-competitor-backlog.md", VALID_RECORD
            )
            errors = validate_run_record(path)
        self.assertEqual(errors, [])

    def test_rejects_missing_five_core_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_record(
                tmp,
                "RUN-20261001-WF02-incomplete.md",
                "# Incomplete\n- Goal: Test\n- Status: DRAFT\n",
            )
            errors = validate_run_record(path)
        joined = "\n".join(errors)
        self.assertIn("missing field: workflow", joined)
        self.assertIn("missing field: automation level", joined)
        self.assertIn("missing field: owner", joined)
        self.assertIn("missing field: human approval required", joined)
        self.assertIn("missing field: output paths", joined)

    def test_rejects_l3_without_approval(self):
        content = VALID_RECORD.replace("WF02", "WF04").replace(
            "Automation level: L2", "Automation level: L3"
        ).replace(
            "Human approval status: NOT_REQUIRED", "Human approval status: PENDING"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_record(
                tmp, "RUN-20261001-WF04-publish-video.md", content
            )
            errors = validate_run_record(path)
        self.assertIn("L3 requires Human approval status: APPROVED", errors)

    def test_rejects_completed_l3_without_read_back(self):
        content = VALID_RECORD.replace("WF02", "WF04").replace(
            "Automation level: L2", "Automation level: L3"
        ).replace(
            "Human approval status: NOT_REQUIRED", "Human approval status: APPROVED"
        ).replace(
            "External action read-back: NOT_REQUIRED",
            "External action read-back: NOT_RUN",
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_record(
                tmp, "RUN-20261001-WF04-publish-video.md", content
            )
            errors = validate_run_record(path)
        self.assertIn(
            "completed L3 Run Record requires external action read-back evidence",
            errors,
        )

    def test_rejects_filename_workflow_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_record(
                tmp, "RUN-20261001-WF01-wrong-route.md", VALID_RECORD
            )
            errors = validate_run_record(path)
        self.assertIn("filename workflow does not match field: WF02", errors)


if __name__ == "__main__":
    unittest.main()
