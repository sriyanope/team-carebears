import json
import unittest
from types import SimpleNamespace

from backend.services import report


class ReportServiceParsingTests(unittest.TestCase):
    def test_parse_report_payload_normalizes_valid_json(self):
        payload = {
            "summary_narrative": "  A useful summary.  ",
            "summary_bullets": [
                {
                    "text": "  Sleep changed on 5 May. ",
                    "references": [
                        {"date_label": " 5 May ", "source_type": "VOICE_NOTE"},
                        {"date_label": "", "source_type": "medication"},
                    ],
                }
            ],
            "flags": [{"what": "  Missed dose ", "why": " Mention to doctor. "}],
        }

        parsed = report._parse_report_payload(json.dumps(payload))

        self.assertEqual(parsed["summary_narrative"], "A useful summary.")
        self.assertEqual(
            parsed["summary_bullets"],
            [
                {
                    "text": "Sleep changed on 5 May.",
                    "references": [{"date_label": "5 May", "source_type": "voice_note"}],
                }
            ],
        )
        self.assertEqual(parsed["flags"], [{"what": "Missed dose", "why": "Mention to doctor."}])

    def test_parse_report_payload_rejects_missing_bullets(self):
        payload = {
            "summary_narrative": "A useful summary.",
            "summary_bullets": [],
            "flags": [],
        }

        with self.assertRaises(ValueError):
            report._parse_report_payload(json.dumps(payload))

    def test_collect_response_text_prefers_output_text(self):
        response = SimpleNamespace(output_text='{"summary_narrative": "ok"}', output=[])

        self.assertEqual(report._collect_response_text(response), '{"summary_narrative": "ok"}')

    def test_collect_response_text_reads_nested_response_content(self):
        response = SimpleNamespace(
            output=[
                SimpleNamespace(
                    content=[
                        SimpleNamespace(text='{"summary_narrative": "ok",'),
                        SimpleNamespace(text='"summary_bullets": [], "flags": []}'),
                    ]
                )
            ]
        )

        self.assertEqual(
            report._collect_response_text(response),
            '{"summary_narrative": "ok",\n"summary_bullets": [], "flags": []}',
        )


if __name__ == "__main__":
    unittest.main()
