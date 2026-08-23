# Hermes Agent + Hermes WebUI

This repo contains a working setup of **Hermes Agent** (the self-improving AI agent by
[Nous Research](https://github.com/NousResearch/hermes-agent)) together with
**Hermes WebUI** ([nesquena/hermes-webui](https://github.com/nesquena/hermes-webui)),
a browser interface for chatting with the agent.

It was set up on **native Windows** (no WSL/Docker required) and verified end-to-end
with a live model call.

## What's where

| Piece                | Location (this machine)                                             |
|----------------------|---------------------------------------------------------------------|
| Hermes Agent install | `%LOCALAPPDATA%\hermes` (config, keys, data, agent source)          |
| Hermes config        | `%LOCALAPPDATA%\hermes\config.yaml`                                 |
| API keys (never committed) | `%LOCALAPPDATA%\hermes\.env`                                  |
| Hermes WebUI (this repo) | `hermes-webui/` (cloned from upstream, no nested `.git`)        |
| WebUI state          | `%LOCALAPPDATA%\hermes\webui`                                       |

## Quick start

### 1. Install Hermes Agent (once)

Native Windows (PowerShell):

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

Linux / macOS / WSL2:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

### 2. Add a model provider

OpenRouter is pre-configured (`model.provider: openrouter`). Put your key in
`%LOCALAPPDATA%\hermes\.env`:

```
OPENROUTER_API_KEY=sk-or-v1-...
```

Pick a model (free-tier default used here):

```bash
hermes config set model.default nvidia/nemotron-3-super-120b-a12b:free
# or any model ID from https://openrouter.ai/models
```

Verify:

```bash
hermes -z "say hi"          # one-shot CLI test
hermes doctor               # health check
```

### 3. Start the WebUI

From this repo, in PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\hermes-webui\start.ps1
```

Then open <http://127.0.0.1:8787>.

> Windows note: the native launcher (`start.ps1`) auto-discovers the Hermes agent
> install and its Python venv at `%LOCALAPPDATA%\hermes\hermes-agent`. The Linux
> bootstrap (`hermes-webui/bootstrap.py`) is not supported on native Windows yet.

### 4. (Optional) Secure it

The WebUI binds to `127.0.0.1` and has **no password** by default. To add one:

```powershell
$env:HERMES_WEBUI_PASSWORD = "choose-a-strong-password"
powershell -ExecutionPolicy Bypass -File .\hermes-webui\start.ps1
```

## Environment knobs (WebUI)

| Variable | Default | Purpose |
|---|---|---|
| `HERMES_WEBUI_PORT` | `8787` | Port |
| `HERMES_WEBUI_HOST` | `127.0.0.1` | Bind address (`0.0.0.0` = LAN, set a password!) |
| `HERMES_WEBUI_PASSWORD` | — | Password auth |
| `HERMES_HOME` | `%LOCALAPPDATA%\hermes` | Hermes home |

## Notes

- The OpenRouter key lives only in `%LOCALAPPDATA%\hermes\.env` — it is **not** in
  this repo.
- The default model was left on a free OpenRouter tier; add credits to
  <https://openrouter.ai/settings/credits> and switch models in the WebUI (or with
  `hermes model`) when ready.
