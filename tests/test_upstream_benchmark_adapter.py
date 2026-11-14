"""Small adapter fixtures only: no upstream C compilation or execution."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


MODULE = Path(__file__).resolve().parents[1]/"experiments/adapters/upstream_labrador/adapter.py"
spec = importlib.util.spec_from_file_location("upstream_benchmark_adapter", MODULE)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


def fixture(target):
    # Minimal textual patch sites, deliberately not a runnable C implementation.
    if target == "greyhound":
        body = ("  polcomctx ctx;\n  polcomprf pi;\n  prncplstmnt st;\n  witness wt;\n"
                "  polcom_commit(&ctx,s,len);\n  polcom_commit(&ctx,s,len);\n"
                "  composite_prove_polcom(&p,&pi,&ctx,x,y);\n")
        calls = "  len = 1 << 19;\n  ret = test_polcom(len);\n  if(ret) goto end;\n  ret = test_pack(len);\n  if(ret) goto end;\n"
    else:
        body = "    n[i] = 1<<"+("11" if target == "chihuahua" else "16")+";\n"
        if target == "dachshund":
            body += ("  simple_prove(&st1,&wt1,&pi0,&com,&st0,&wt0,0);\n"
                     "  prove(&st2,&wt2,&pi1,&st1,&wt1,0);\n"
                     "  composite_prove_simple(&p,&com,&st,&wt);;\n")
        calls = "  ret = test_twolayer();\n  if(ret) goto end;\n  ret = test_pack();\n  if(ret) goto end;\n"
    return (body+"  ret = verify(&st,&wt);\n"+calls+
            "end:\n  free_comkey();\n  return ret;\n}\n").encode()


def inputs():
    files = {f"test_{t}.c": fixture(t) for t in adapter.TARGETS}
    files.update({"README": b"Requires the AVX512 instruction set.\n",
                  "LICENSE": b"Apache License Version 2.0\n",
                  "Makefile": b"-std=c2x -march=native -mtune=native -O3 -flto=auto\n",
                  "pack.c": b"unchanged library fixture\n", "pack.h": b"header\n",
                  "data.h": b"parameters\n", "labrador.c": b"library\n",
                  "randombytes.c": b"OS entropy\n"})
    identity = {"commit": adapter.PIN, "clean": True,
                "files": {n: {"mode": "100644", "pinned_sha256": adapter.digest(v)}
                          for n, v in files.items()}}
    return files, identity


class UpstreamAdapterTests(unittest.TestCase):
    def test_patch_markers_follow_all_real_checks(self):
        for target in adapter.TARGETS:
            with self.subTest(target=target):
                patched = adapter.patch_test(target, fixture(target)).decode()
                self.assertIn("ret = verify(&st,&wt);", patched)
                self.assertIn("return ret ? EXIT_FAILURE : EXIT_SUCCESS;", patched)
                self.assertEqual(patched.count("LABRADOR_ADAPTER_STAGE_OK"), 2)
                self.assertEqual(patched.count("LABRADOR_ADAPTER_SUCCESS"), 1)
                self.assertIn("1 << 10" if target == "greyhound" else "1<<10", patched)
                if target != "chihuahua":
                    self.assertIn("LABRADOR_ADAPTER_CALL_FAILED", patched)
        self.assertIn("NOT native binary R1CS", adapter.RELATIONS["dachshund"])

    def test_patch_fails_closed_on_changed_anchor_or_bad_size(self):
        with self.assertRaises(adapter.PreparationError):
            adapter.patch_test("chihuahua", fixture("chihuahua").replace(b"1<<11", b"1<<12"))
        for value in (0, 9, 20, True, 10.0):
            with self.subTest(value=value), self.assertRaises(adapter.PreparationError):
                adapter.patch_test("chihuahua", fixture("chihuahua"), value)

    def test_source_requirements_and_pin_rejection(self):
        files, _ = inputs()
        adapter.validate_source_metadata(files)
        with self.assertRaises(adapter.PreparationError):
            adapter.validate_source_metadata({**files, "README": b"no feature requirement"})
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp).resolve()
            with patch.object(adapter, "_git", side_effect=[str(source).encode(), b"wrong-pin\n"]):
                with self.assertRaisesRegex(adapter.PreparationError, "Expected clean upstream pin"):
                    adapter.read_pinned_checkout(source)
            with patch.object(adapter, "_git", side_effect=[str(source).encode(), adapter.PIN.encode(), b" M test.c\n"]):
                with self.assertRaisesRegex(adapter.PreparationError, "not clean"):
                    adapter.read_pinned_checkout(source)

    def test_prepare_copies_only_to_new_external_directory(self):
        files, identity = inputs()
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base/"source"
            source.mkdir()
            for name, data in files.items():
                (source/name).write_bytes(data)
            before = {p.name: p.read_bytes() for p in source.iterdir()}
            with patch.object(adapter, "read_pinned_checkout", return_value=(files, identity)):
                plan = adapter.prepare(source, base/"work", base/"artifacts", dry_run=False)
            self.assertEqual(before, {p.name: p.read_bytes() for p in source.iterdir()})
            self.assertEqual((base/"work/pack.c").read_bytes(), files["pack.c"])
            self.assertFalse((base/"work/.git").exists())
            self.assertEqual(plan["status"], "prepared_not_executed")
            self.assertEqual(set(plan["modified_files"]), {f"test_{t}.c" for t in adapter.TARGETS})
            self.assertIsNone(plan["actual_serialized_proof_bytes"])
            self.assertEqual(json.loads((base/"artifacts/manifest.json").read_text()), plan)
            with self.assertRaises(adapter.PreparationError):
                adapter.prepare(source, base/"work", base/"new-artifacts")

    def test_dry_run_and_path_boundaries(self):
        files, identity = inputs()
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base/"source"
            source.mkdir()
            with patch.object(adapter, "read_pinned_checkout", return_value=(files, identity)):
                plan = adapter.prepare(source, base/"work", base/"artifacts")
            self.assertFalse((base/"work").exists())
            self.assertEqual(plan["status"], "dry_run_not_executed")
            for work in (source/"nested", base, adapter.REPO_ROOT/"vendor-test"):
                with self.subTest(work=work), self.assertRaises(adapter.PreparationError):
                    adapter.validate_destinations(source, work, base/"new-artifacts")

    def test_hardware_gate_rejects_avx2_only_and_mixed_cpus(self):
        low = adapter.capability_report("Linux", "x86_64", "flags : avx2 aes\n")
        self.assertEqual(low["status"], "unsupported_capability")
        self.assertEqual(low["execution_status"], "blocked-hardware")
        high = "flags : "+" ".join(adapter.REQUIRED_FLAGS)+"\n"
        self.assertEqual(adapter.capability_report("Linux", "x86_64", high)["status"], "cpu_capability_present")
        self.assertEqual(adapter.capability_report("Linux", "x86_64", high+"flags : avx2\n")["status"], "unsupported_capability")
        self.assertEqual(adapter.capability_report("Windows", "AMD64", high)["status"], "unsupported_capability")

    def test_result_requires_returncode_stage_checks_and_no_errors(self):
        log = ("Dachshund Pack size: 12.50 KB\n"
               "LABRADOR_ADAPTER_STAGE_OK dachshund two_layer\n"
               "LABRADOR_ADAPTER_STAGE_OK dachshund composite\n"
               "LABRADOR_ADAPTER_SUCCESS dachshund\n")
        result = adapter.check_result("dachshund", 0, log, "")
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["upstream_printed_size_estimates"][0]["estimated_KiB"], 12.5)
        self.assertIsNone(result["actual_serialized_proof_bytes"])
        for ret, out, err in ((1, log, ""), (-4, log, ""), (0, log, "ERROR: failed"),
                              (0, log.replace("two_layer", "missing"), ""),
                              (0, log+"LABRADOR_ADAPTER_SUCCESS dachshund\n", "")):
            with self.subTest(ret=ret, out=out, err=err):
                self.assertEqual(adapter.check_result("dachshund", ret, out, err)["status"], "failed")


if __name__ == "__main__":
    unittest.main()
