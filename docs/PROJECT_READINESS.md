# Project readiness

Use the project-owned `quality/profile.json` to diagnose a failed local launch or
prepare a project for real verification. In a child project:

```sh
python3 .agent-system/profile.py doctor
python3 .agent-system/profile.py doctor --probe
python3 .agent-system/profile.py doctor --verify-launch
```

In this repository use `tools/profiles/profile.py`. Plain `doctor` only inspects
declared paths and resolves executables; it does not run commands, install tools,
read user configuration/credentials, start servers or contact the network.
Existing profiles work without a readiness section and report undeclared details
as unknown. Exit 0 means inspection found no declared prerequisite failure, not
that the application is working. Exit 1 means a missing prerequisite or failed
explicit check; exit 2 means invalid configuration/arguments.

An optional `readiness` section has the following shape. Adapt the paths and
commands to the actual project; this is a schema example, not an installed recipe:

```json
{
  "requirements": [{
    "id": "frontend", "executable": "node", "paths": ["node_modules"],
    "help": "Install dependencies using this project's lockfile and documented Node version."
  }],
  "model": {"requested": "gpt-6-astra", "reasoning_effort": "medium", "service_tier": "standard"},
  "launch": {
    "command": ["npm", "run", "dev"], "cwd": ".", "defined_by": ["package.json"],
    "url": "http://127.0.0.1:3000/", "expected_text": "My application",
    "verification_check": "browser-journey"
  }
}
```

`verification_check` must name a configured check in the same profile. The launch
command is displayed for use by the developer/agent; doctor never starts it
implicitly. Model intent is documentation, not effective Codex configuration;
the observed model/effort/tier remains null until the host supplies evidence.
Check the actual model picker and available host tools during the task. Do not
read private transcripts to infer capabilities or subscribe to another service.

`--probe` explicitly sends one HTTP GET to the declared local endpoint, without
proxies, credentials or redirects. Only HTTP on 127.0.0.1, ::1 or localhost is
accepted; localhost is connected to 127.0.0.1. Reads are size-limited with socket
timeouts. Optional `expected_text` checks identity in the first 64 KiB of UTF-8
response text. A response, even from the right app, does not prove JavaScript,
buttons, backend integration, accessibility, performance or visual quality.

`--verify-launch` executes the named project check **fresh**, through the existing
quality runner. Review that check and its server lifecycle before running it. For
web projects use the browser runner's server configuration and journey assertions;
do not add a second server manager. It must use isolated fixtures, refuse an
unrelated occupied port and stop processes it owns. A failed check stays failed.
Evidence names the executed check and its log; `check_passed` covers only that
check's assertions. Visual review remains `not_performed` until captures are viewed.

For native/device projects, declare the relevant build/launch/device checks. Do
not invent an HTTP endpoint as a substitute. An absent launch contract is visible
and does not prevent running other configured checks.

Opening an ES-module web application via `file://` is not its supported launch.
Use the documented server URL and exercise the primary action before delivery.
Keep launch instructions beside the application's entry point; examples remain
optional framework fixtures and are never installed as child application code.
