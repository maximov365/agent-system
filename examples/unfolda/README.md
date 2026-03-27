# Unfolda — Reference Project Configuration

This directory contains the full Unfolda project configuration as a reference
implementation for the agent system.

Unfolda is a web-based SaaS service that transforms EPUB books into structured
formats for reading and understanding in a foreign language.

## Usage

To instantiate the agent system with the Unfolda configuration:

```bash
cp examples/unfolda/project.config.yaml .
cp -r examples/unfolda/docs/ docs/
python setup.py
```

To run the Unfolda round-trip test:

```bash
cp examples/unfolda/test_setup.py .
python test_setup.py
```

## Contents

- `project.config.yaml` — Full project configuration (pipeline, domain rules, brand, analytics events, etc.)
- `test_setup.py` — Round-trip test verifying rendered output matches golden hashes
- `docs/` — Complete Unfolda documentation (PRD, architecture, features, tasks, decisions, brand)
