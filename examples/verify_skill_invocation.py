"""Verify skill discovery and explicit loading against a synthetic local provider.

Requires a compatible absolute --codex-binary. Exercises global, project, and
tree scopes using disposable homes, local HTTP request capture and intentional
errors; no real model inference, real-home installation, provider credentials or
project data are used. Only the disposable project paths are marked trusted.
"""
import argparse
from collections import deque
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import install

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--codex-binary", type=Path, required=True)
args = parser.parse_args()
if not args.codex_binary.is_absolute() or not args.codex_binary.is_file():
    parser.error("--codex-binary must name an existing absolute executable")

def verify(directory, scope):
    home = directory / "home"
    root = directory / "workspace"
    root.mkdir(parents=True)
    members = [root]
    if scope == "tree":
        members.extend([root / "podboss", root / "group/podprocessor"])
        for member in members[1:]:
            (member / ".git").mkdir(parents=True)
    elif scope == "project":
        (root / ".git").mkdir()
    runtime_home = home if scope == "global" else root / ".codex"
    install.apply(install.plan(runtime_home, ROOT, scope=scope, root=root if scope != "global" else None,
                               repositories=["podboss", "group/podprocessor"] if scope == "tree" else None))
    home.mkdir(exist_ok=True)
    requests = queue.Queue()
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers['Content-Length']))
            requests.put(json.loads(body))
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"error":{"message":"synthetic capture only; no model inference"}}')
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    config = home / 'config.toml'
    settings = f'''model = "dk-fixture"
model_provider = "dk_fixture"
approval_policy = "never"
sandbox_mode = "read-only"
web_search = "disabled"
[model_providers.dk_fixture]
name = "Synthetic local request capture"
base_url = "http://127.0.0.1:{server.server_port}/v1"
env_key = "DK_FIXTURE_TOKEN"
wire_api = "responses"
'''
    settings += "".join(f'\n[projects.{json.dumps(str(member))}]\ntrust_level = "trusted"\n'
                        for member in members)
    config.write_text(settings + (config.read_text() if config.exists() else ""), encoding='utf-8')
    environment = dict(os.environ, CODEX_HOME=str(home), DK_FIXTURE_TOKEN='synthetic-only')
    process = subprocess.Popen([str(args.codex_binary), "app-server"], cwd=root, env=environment,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, encoding="utf-8")
    messages = queue.Queue()
    diagnostics = deque(maxlen=40)
    def read():
        for line in process.stdout:
            messages.put(json.loads(line))
    def read_errors():
        for line in process.stderr:
            diagnostics.append(line.rstrip())
    threading.Thread(target=read, daemon=True).start()
    threading.Thread(target=read_errors, daemon=True).start()
    identifiers = iter(range(1, 1000))
    def send(method, params, notification=False):
        value = dict(method=method, params=params)
        identifier = None if notification else next(identifiers)
        if not notification:
            value["id"] = identifier
        process.stdin.write(json.dumps(value) + "\n")
        process.stdin.flush()
        if identifier is not None:
            while True:
                try:
                    result = messages.get(timeout=30)
                except queue.Empty:
                    raise RuntimeError(f"Timed out waiting for {method}: {list(diagnostics)}") from None
                if result.get("id") == identifier:
                    if "error" in result:
                        raise RuntimeError(result["error"])
                    return result["result"]
    try:
        send("initialize", {"clientInfo": {"name": "dk-discovery-test", "version": "1"},
                            "capabilities": {"experimentalApi": True}})
        send("initialized", {}, notification=True)
        for cwd in members:
            result = send("skills/list", {"cwds": [str(cwd)], "forceReload": True})
            skills = [s for entry in result["data"] for s in entry.get("skills", [])
                      if s["name"] == "delegation-kit"]
            assert len(skills) == 1, skills
            expected = ((home / "skills") if scope == "global" else cwd / ".agents/skills") / "delegation-kit/SKILL.md"
            assert Path(skills[0]["path"]).resolve() == expected.resolve(), skills
            pointer = json.loads((expected.parent / "runtime.json").read_text())
            assert Path(pointer["runtime_directory"]).resolve() == (runtime_home / "delegation-kit").resolve()
            effective = send("config/read", {"cwd": str(cwd), "includeLayers": True})
            agents = effective["config"].get("agents", {})
            for role in install.ROLES:
                expected_role = runtime_home / f"delegation-kit/agents/{role}.toml"
                assert Path(agents[role]["config_file"]).resolve() == expected_role.resolve(), agents
            print(json.dumps({"scope": scope, "member": str(cwd.relative_to(directory)),
                              "skill_path_verified": True, "runtime_pointer_verified": True,
                              "loaded_roles_verified": len(install.ROLES)}))
            for selected in (False, True):
                thread = send('thread/start', {'cwd': str(cwd), 'ephemeral': True})
                assert thread['modelProvider'] == 'dk_fixture', thread
                inputs = [{'type': 'text', 'text': 'Explain this synthetic fixture briefly.'}]
                if selected:
                    inputs.insert(0, {'type': 'skill', 'name': 'delegation-kit', 'path': str(expected)})
                send('turn/start', {'threadId': thread['thread']['id'], 'input': inputs})
                body = json.dumps(requests.get(timeout=20))
                assert ('Apply DK only to the outcome' in body) == selected
                assert ('Explicitly requested coordination of bounded engineering' in body) == selected
                print(json.dumps({'scope': scope, 'explicit_selection': selected,
                                  'skill_body_in_outgoing_request': selected, 'real_inference': False}))
    finally:
        process.stdin.close()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
        process.stdout.close()
        process.stderr.close()
        server.shutdown()
        server.server_close()


with tempfile.TemporaryDirectory(prefix="dk-discovery-") as temporary:
    for scope in ("global", "project", "tree"):
        verify(Path(temporary) / scope, scope)
