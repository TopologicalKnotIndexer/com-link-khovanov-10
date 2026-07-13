# Composite Link Khovanov Pipeline

Generate composite-link representations and compute their Khovanov homology.

## Installation

```bash
pip install com-link-khovanov-10
```

## Quick start

Run `python com-link-khovanov-10/main.py` or import the module from a checkout.

PD codes are lists of four-entry crossings. Each arc label must occur exactly twice. Functions validate their inputs and do not mutate caller-owned PD-code lists unless explicitly documented.

## Development

Use Python 3.10 or newer for Python packages. Build distributions with `poetry build`. Run the package's tests or examples before publishing. C++ projects require a modern standards-compliant compiler.

## License

MIT. See `LICENSE`.
