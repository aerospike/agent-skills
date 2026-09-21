"""Both registries must receive exactly one submission: the compiled skill."""

import http.server
import json
import os
import pathlib
import shutil
import subprocess
import threading

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
REPO_URL = "https://github.com/aerospike/agent-skills"


def _run(script, *args):
    result = subprocess.run(
        [str(REPO_ROOT / "scripts" / script), "--repo-url", REPO_URL, "--dry-run", *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_openagentskill_submits_only_the_compiled_skill():
    out = _run("publish-openagentskill.sh")

    assert out.count("DRY RUN") == 1
    assert "DRY RUN aerospike:" in out
    for retired in ("aerospike-getting-started", "aerospike-development"):
        assert retired not in out


def test_openagentskill_payload_points_at_the_compiled_skill():
    out = _run("publish-openagentskill.sh")
    payload = json.loads(out[out.index("{"):out.rindex("}") + 1])

    assert payload["repository"] == REPO_URL
    assert payload["skillPath"] == "compiled-skills/aerospike/SKILL.md"
    assert payload["submissionSource"] == "agent"


def test_upskill_submits_only_the_compiled_skill():
    out = _run("publish-upskill.sh", "--ref", "main")

    assert out.count("DRY RUN") == 1
    assert f"{REPO_URL}/tree/main/compiled-skills/aerospike" in out
    assert "/skills/aerospike-development" not in out


@pytest.mark.parametrize(
    "config, should_succeed, expected",
    [
        # What the CLI actually writes. Checking the command-line name instead
        # ("submissions") matched nothing, read that as disabled, and failed a
        # correctly configured publish.
        ('{"submissionsEnabled": true}', True, "Verified submissions are enabled"),
        ('{"submissions": true}', True, "Verified submissions are enabled"),
        # The case the check exists for: submit would exit 0 while doing nothing.
        ('{"submissionsEnabled": false}', False, "refusing to"),
        ('{"submissions": false}', False, "refusing to"),
        # Neither spelling is unknown, not off. Warn and continue rather than block
        # a publish because the CLI renamed a key.
        ('{"serverUrl": "https://example.invalid"}', True, "Could not find a submissions setting"),
    ],
)
def test_upskill_checks_the_persisted_submissions_setting(
    config, should_succeed, expected, tmp_path
):
    """Runs the real config gate, with a stub CLI standing in for upskill.

    Deliberately not --dry-run: the gate only runs on a live publish, which is
    exactly why a defect in it reached production. The stub makes `upskill submit`
    a no-op, so nothing is sent anywhere.
    """
    bindir = tmp_path / "bin"
    bindir.mkdir()
    stub = bindir / "upskill"
    stub.write_text("#!/usr/bin/env bash\nexit 0\n")
    stub.chmod(0o755)

    config_path = tmp_path / "config.json"
    config_path.write_text(config)

    result = subprocess.run(
        [
            str(REPO_ROOT / "scripts" / "publish-upskill.sh"),
            "--repo-url",
            REPO_URL,
            "--ref",
            "main",
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env={
            **os.environ,
            "PATH": f"{bindir}{os.pathsep}{os.environ['PATH']}",
            "UPSKILL_CONFIG": str(config_path),
        },
    )

    output = result.stdout + result.stderr
    assert expected in output, output
    if should_succeed:
        assert result.returncode == 0, output
    else:
        assert result.returncode != 0, output


@pytest.mark.parametrize("script", ["publish-openagentskill.sh", "publish-upskill.sh"])
def test_scripts_fail_when_the_compiled_skill_is_absent(script, tmp_path):
    """A missing artifact must fail loudly rather than report a successful no-op.

    Each script derives its root from its own location, so copying scripts/ alone
    into an empty tree is what makes the compiled skill genuinely absent.
    """
    shutil.copytree(REPO_ROOT / "scripts", tmp_path / "scripts")

    result = subprocess.run(
        [str(tmp_path / "scripts" / script), "--repo-url", REPO_URL, "--dry-run"],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "compile-agents.py --write" in result.stderr


class _StubRegistry(http.server.BaseHTTPRequestHandler):
    """Accepts /skills/validate and answers /skills/submit like the real API.

    The submit response carries a status token in both places the real one does:
    ``submission.token`` and, embedded in a query string, ``submission.statusUrl``.
    """

    TOKEN = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    SUBMISSION_ID = "11111111-2222-3333-4444-555555555555"

    def do_POST(self):  # noqa: N802 - name fixed by BaseHTTPRequestHandler
        self.rfile.read(int(self.headers.get("Content-Length", 0)))
        if self.path.endswith("/skills/validate"):
            body = {"success": True}
        else:
            body = {
                "success": True,
                "submission": {
                    "id": self.SUBMISSION_ID,
                    "token": self.TOKEN,
                    "status": "submitted",
                    "skill": {"name": "aerospike"},
                    "statusUrl": (
                        f"/api/skills/submissions/{self.SUBMISSION_ID}"
                        f"?token={self.TOKEN}"
                    ),
                },
            }
        payload = json.dumps(body).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass


@pytest.fixture
def stub_registry():
    server = http.server.HTTPServer(("127.0.0.1", 0), _StubRegistry)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/api"
    finally:
        server.shutdown()
        server.server_close()


def test_receipt_records_the_submission_id_but_not_its_status_token(
    stub_registry, tmp_path
):
    """The receipt is uploaded as a workflow artifact, and this repository is
    public -- a public repository's artifacts are readable by any GitHub account.
    So the receipt is a published file, and a status token must never reach it.

    Both carriers are checked. An earlier version of this script redacted nothing,
    and `statusUrl` would still have leaked the token in a query string even if
    only the obvious `token` field had been removed.
    """
    receipts = tmp_path / "receipts.jsonl"
    result = subprocess.run(
        [
            str(REPO_ROOT / "scripts" / "publish-openagentskill.sh"),
            "--repo-url", REPO_URL,
            "--receipts", str(receipts),
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env={**os.environ, "OAS_API": stub_registry},
    )
    assert result.returncode == 0, result.stderr

    raw = receipts.read_text()
    assert _StubRegistry.TOKEN not in raw, "status token leaked into the receipt"
    assert "statusUrl" not in raw, "statusUrl embeds the token in its query string"

    receipt = json.loads(raw.strip())
    submission = receipt["response"]["submission"]
    assert submission["id"] == _StubRegistry.SUBMISSION_ID
    assert "token" not in submission
    # The rest of the response is still archived; redaction is surgical.
    assert submission["skill"]["name"] == "aerospike"
    assert receipt["registry"] == "openagentskill"


def test_the_token_never_reaches_stdout_or_stderr(stub_registry, tmp_path):
    """The log is the other public surface. The script prints a progress line per
    submission, and that line must carry the id alone."""
    result = subprocess.run(
        [
            str(REPO_ROOT / "scripts" / "publish-openagentskill.sh"),
            "--repo-url", REPO_URL,
            "--receipts", str(tmp_path / "receipts.jsonl"),
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env={**os.environ, "OAS_API": stub_registry},
    )
    assert result.returncode == 0, result.stderr
    assert _StubRegistry.TOKEN not in result.stdout + result.stderr
    assert _StubRegistry.SUBMISSION_ID in result.stdout
