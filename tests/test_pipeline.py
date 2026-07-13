from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import tempfile
from types import ModuleType
import unittest
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "com-link-khovanov-10" / "main.py"

# The application dependencies are tested in their own repositories. Supply
# minimal modules here so these tests remain focused and do not require a
# locally installed native Khovanov backend.
fake_generator = ModuleType("com_link_gen_10")
fake_generator.get_version = lambda *_: "test"
fake_generator.com_link_gen = lambda *_: []
fake_khovanov = ModuleType("link_khovanov")
fake_khovanov.link_khovanov = lambda pd_code: []
fake_evaluator = ModuleType("link_rep_to_pd_code")
fake_evaluator.link_rep_to_pd_code = lambda document: []
sys.modules["com_link_gen_10"] = fake_generator
sys.modules["link_khovanov"] = fake_khovanov
sys.modules["link_rep_to_pd_code"] = fake_evaluator

SPEC = spec_from_file_location("com_link_khovanov_pipeline", MODULE_PATH)
pipeline = module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(pipeline)


class PipelineTests(unittest.TestCase):
    def test_pd_literal_is_never_executed(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "executed"
            document = Path(directory) / "0000001.txt"
            document.write_text(
                "// PD_CODE: __import__('pathlib').Path(%r).touch()\n" % str(marker),
                encoding="utf-8",
            )
            with self.assertRaises((ValueError, SyntaxError)):
                pipeline.process_one_file(str(document))
            self.assertFalse(marker.exists())

    def test_khovanov_prefix_is_atomic_and_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            document = Path(directory) / "0000001.txt"
            document.write_text("// PD_CODE: [[1, 1, 2, 2]]\nbody\n", encoding="utf-8")
            with patch.object(
                pipeline.link_khovanov, "link_khovanov", return_value=["q+t"]
            ):
                pipeline.process_one_file(str(document))
                first = document.read_text(encoding="utf-8")
                pipeline.process_one_file(str(document))
            self.assertEqual(document.read_text(encoding="utf-8"), first)
            self.assertTrue(first.startswith("// KHOVANOV: q+t\n// PD_CODE:"))

    def test_generation_removes_stale_numeric_files(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(pipeline, "DATA_DIR", directory), patch.object(
                pipeline.com_link_gen_10,
                "com_link_gen",
                return_value=["first", "second"],
            ), patch.object(
                pipeline.link_rep_to_pd_code,
                "link_rep_to_pd_code",
                return_value=[[1, 1, 2, 2]],
            ):
                output = Path(pipeline.get_data_dir(2, 1))
                output.mkdir(parents=True)
                (output / "0000099.txt").write_text("stale", encoding="utf-8")
                pipeline.generate_all(2, 1, process_count=1)
                self.assertEqual(
                    sorted(path.name for path in output.glob("*.txt")),
                    ["0000001.txt", "0000002.txt"],
                )

    def test_worker_count_rejects_bool_float_and_zero(self):
        for value in (True, 1.5, 0, -1):
            with self.assertRaisesRegex(ValueError, "positive integer"):
                pipeline._worker_count(value)


if __name__ == "__main__":
    unittest.main()
