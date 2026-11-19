# Contributing

This repository is a standalone copy of experiment 02 from the [Copilot Agent Experiments catalogue](https://github.com/rahul-bachina/copilot-agent-experiments). Small fixes are welcome. An adaptation for a named firm is a conversation, not a pull request full of that firm's data.

## Run the checks

Python 3.10 or newer.

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest tests/ -v --tb=short
python scripts/governance_checks.py
python scripts/build_llms_full.py --check
```

If you change `README.md` or a document listed in `scripts/build_llms_full.py`, regenerate `llms-full.txt`:

```bash
python scripts/build_llms_full.py
```

## Boundaries

- Synthetic complaints only. Do not add a real complaint, a real customer, or a secret.
- Autonomy stays at A0, A1, or A2. A3 is rejected by `schemas/agent-manifest.schema.json`.
- Do not enable a send, a production write, an uphold, a reject, redress, or a vulnerability label.
- DISP dates stay in `src/disp_clock.py`. Do not move that arithmetic into a prompt.
- Use Microsoft Foundry. The retired product name is allowed only in a "formerly" note.
- Write in UK English.

## Asking for an adaptation

Use the issue template **Request an adaptation for my organisation**. Say which systems you use and which approval chain you need. Leave customer data out of the issue.

The weekly sync from the hub does not overwrite `README.md`, `llms.txt`, `llms-full.txt`, or the other paths in `.sync-ignore`.
