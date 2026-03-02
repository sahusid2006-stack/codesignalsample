from __future__ import annotations

import json
import os
import subprocess
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from src.exercises import EXERCISE_MAP, EXERCISES, LEVELS
from src.runner import run_task

ROOT = Path(__file__).resolve().parent
PROMPT_DIR = ROOT / "src" / "prompts"
STATIC_DIR = ROOT / "web" / "static"
TASK_IDS = ("task1", "task2", "task3")


def _html_index() -> str:
    sections = []
    for level in LEVELS:
        items = []
        for ex in [e for e in EXERCISES if e.level == level]:
            items.append(f'<li><a href="/exercise/{ex.exercise_id}">{ex.exercise_id} — {ex.title}</a> <small>({ex.task_id})</small></li>')
        sections.append(f"<section class='level'><h2>Level {level}</h2><ul>{''.join(items)}</ul></section>")
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>Prompt Assessment Simulator</title><link rel='stylesheet' href='/static/style.css'></head>
<body><main class='container'><h1>Prompt Engineering Assessment Simulator</h1>
<p>CodeSignal-style workflow with Claude API and hidden grading.</p>
<div class='toolbar'>
<button onclick='runVisible()'>Run Visible Tests</button>
<button onclick='runGrade()'>Run Full Grade</button>
<button onclick='resetPrompts()'>Reset Baseline Prompts</button></div>
<pre id='output' class='output'>Ready.</pre>{''.join(sections)}</main>
<script>
async function post(url){{const r=await fetch(url,{{method:'POST'}});return await r.json();}}
async function runVisible(){{const d=await post('/api/run_visible_tests');document.getElementById('output').textContent=d.output;}}
async function runGrade(){{const d=await post('/api/run_full_grade');document.getElementById('output').textContent=`${{d.summary}}\n\n${{d.output}}`;}}
async function resetPrompts(){{const d=await post('/api/reset_prompts');document.getElementById('output').textContent=d.ok?'Prompts reset.':'Reset failed.';}}
</script></body></html>"""


def _read_prompt(task_id: str) -> str:
    return (PROMPT_DIR / f"{task_id}_prompt.txt").read_text(encoding="utf-8")


def _write_prompt(task_id: str, content: str) -> None:
    (PROMPT_DIR / f"{task_id}_prompt.txt").write_text(content, encoding="utf-8")


def _html_exercise(exercise_id: str) -> str:
    ex = EXERCISE_MAP[exercise_id]
    ordered = [e.exercise_id for e in EXERCISES]
    idx = ordered.index(exercise_id)
    prev_link = f"<a class='navbtn' href='/exercise/{ordered[idx-1]}'>Previous</a>" if idx > 0 else ""
    next_link = f"<a class='navbtn' href='/exercise/{ordered[idx+1]}'>Next</a>" if idx < len(ordered) - 1 else ""
    prompt_text = _read_prompt(ex.task_id)
    system_prompt = (PROMPT_DIR / "system_prompt.txt").read_text(encoding="utf-8")
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>{ex.exercise_id}</title><link rel='stylesheet' href='/static/style.css'></head>
<body><main class='container'><a href='/'>← Back</a>
<h1>{ex.exercise_id} — {ex.title}</h1><p><b>Level:</b> {ex.level} | <b>Task:</b> {ex.task_id}</p><p><b>Goal:</b> {ex.prompt_goal}</p>
<h3>System Prompt</h3><pre class='panel'>{system_prompt}</pre>
<h3>Exercise Input</h3><pre class='panel'>{ex.input_text}</pre>
<h3>Editable Prompt: {ex.task_id}_prompt.txt</h3>
<textarea id='promptBox'>{prompt_text}</textarea>
<div class='toolbar'>
<button onclick='savePrompt()'>Save Prompt</button>
<button onclick='runExercise()'>Run This Exercise</button>
<button onclick='runVisible()'>Run Visible Tests</button>
<button onclick='runGrade()'>Submit / Full Grade</button>{prev_link}{next_link}</div>
<pre id='result' class='output'>Ready.</pre></main>
<script>
async function savePrompt(){{const prompt=document.getElementById('promptBox').value;const r=await fetch('/api/save_prompt/{ex.task_id}',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{prompt}})}});const d=await r.json();document.getElementById('result').textContent=d.ok?'Saved.':d.error;}}
async function runExercise(){{const r=await fetch('/api/run_exercise/{ex.exercise_id}',{{method:'POST'}});const d=await r.json();document.getElementById('result').textContent=d.ok?d.output:d.error;}}
async function runVisible(){{const r=await fetch('/api/run_visible_tests',{{method:'POST'}});const d=await r.json();document.getElementById('result').textContent=d.output;}}
async function runGrade(){{const r=await fetch('/api/run_full_grade',{{method:'POST'}});const d=await r.json();document.getElementById('result').textContent=`${{d.summary}}\n\n${{d.output}}`;}}
</script></body></html>"""


def _run_pytest(args: list[str], include_hidden: bool = False) -> tuple[int, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    if include_hidden:
        env["INCLUDE_HIDDEN"] = "1"
    result = subprocess.run([sys.executable, "-m", "pytest", *args], capture_output=True, text=True, cwd=ROOT, env=env)
    output = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
    return result.returncode, output


class AppHandler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: str, content_type: str = "text/html; charset=utf-8") -> None:
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, payload: dict, status: int = 200) -> None:
        self._send(status, json.dumps(payload), "application/json")

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/":
            return self._send(HTTPStatus.OK, _html_index())
        if parsed.path.startswith("/exercise/"):
            ex_id = parsed.path.split("/")[-1]
            if ex_id in EXERCISE_MAP:
                return self._send(HTTPStatus.OK, _html_exercise(ex_id))
            return self._send(HTTPStatus.NOT_FOUND, "Exercise not found")
        if parsed.path.startswith("/static/"):
            rel = parsed.path.replace("/static/", "")
            file_path = STATIC_DIR / rel
            if file_path.exists() and file_path.is_file():
                content = file_path.read_text(encoding="utf-8")
                return self._send(HTTPStatus.OK, content, "text/css; charset=utf-8")
            return self._send(HTTPStatus.NOT_FOUND, "Not found")
        self._send(HTTPStatus.NOT_FOUND, "Not found")

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8") or "{}")

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)

        if parsed.path.startswith("/api/save_prompt/"):
            task_id = parsed.path.split("/")[-1]
            if task_id not in TASK_IDS:
                return self._send_json({"ok": False, "error": "invalid task"}, 400)
            payload = self._read_json()
            _write_prompt(task_id, str(payload.get("prompt", "")))
            return self._send_json({"ok": True})

        if parsed.path.startswith("/api/run_exercise/"):
            ex_id = parsed.path.split("/")[-1]
            ex = EXERCISE_MAP.get(ex_id)
            if ex is None:
                return self._send_json({"ok": False, "error": "unknown exercise"}, 404)
            try:
                output = run_task(ex.task_id, ex.input_text)
            except Exception as exc:
                return self._send_json({"ok": False, "error": str(exc)}, 500)
            return self._send_json({"ok": True, "output": output})

        if parsed.path == "/api/run_visible_tests":
            code, output = _run_pytest(["-q", "tests/test_*_visible.py"])
            return self._send_json({"ok": code == 0, "exit_code": code, "output": output})

        if parsed.path == "/api/run_full_grade":
            code, output = _run_pytest(["-q", "tests", "tests/hidden"], include_hidden=True)
            return self._send_json({"ok": code == 0, "summary": "PASS" if code == 0 else "FAIL", "exit_code": code, "output": output})

        if parsed.path == "/api/reset_prompts":
            baseline = {
                "task1": "Classify the support message into exactly one label:\nBILLING, BUG, FEATURE_REQUEST, OTHER.\n\nHeuristics:\n- BILLING: charges, refund, invoice, payment.\n- BUG: error, crash, broken.\n- FEATURE_REQUEST: asking to add a new capability.\n- OTHER: anything else.\n\nReturn only the label and nothing else.\n\nMessage:\n{INPUT}\n",
                "task2": "Extract customer entities from the input and output JSON only.\nReturn exactly these keys:\n{\"name\":\"...\",\"email\":\"...\",\"order_id\":\"...\"}\nUse empty string if missing.\n\nOrder ID patterns can include ORD-12345 or #12345.\n\nInput:\n{INPUT}\n",
                "task3": "You will receive SNIPPET and QUESTION.\nUse only the snippet as evidence.\nIf the answer is explicitly present in the snippet, return the exact answer phrase.\nIf it is not explicitly present, return UNKNOWN.\nReturn only the final answer text.\n\n{INPUT}\n",
            }
            for task_id, content in baseline.items():
                _write_prompt(task_id, content)
            return self._send_json({"ok": True})

        self._send_json({"ok": False, "error": "not found"}, 404)


def run_server() -> None:
    port = int(os.getenv("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), AppHandler)
    print(f"Web app running at http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
