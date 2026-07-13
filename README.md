# Composite Link Khovanov Pipeline

Generate composite links up to a crossing bound and compute their integral Khovanov homology.

## Installation

This repository is an application checkout. Install the released TopLink packages first, then run its Python module.

## Usage example

```python
from importlib.util import module_from_spec, spec_from_file_location

spec = spec_from_file_location("pipeline", "com-link-khovanov-10/main.py")
pipeline = module_from_spec(spec)
spec.loader.exec_module(pipeline)

folder = pipeline.generate_all(10, 3, process_count=8)
pipeline.process_khovanov_parallel(folder, process_count=8)
print(folder)
```

## Algorithm

Generation enumerates multisets of prime factors whose total crossing count is at most the requested bound. It enumerates spanning connection schemes between factor components, evaluates each textual link representation with oriented connected sums, and writes canonically numbered PD codes. Khovanov processing enumerates component orientations, removes duplicate homology strings, and prepends the results to each numbered file. Work is distributed with `ProcessPoolExecutor` while filenames remain deterministic.

## Input conventions

A PD code is represented as a list of four-entry crossings. Arc labels normally occur exactly twice. Public functions validate inputs and return new values rather than mutating caller-owned data unless their API explicitly says otherwise.

## External software

- A C++14 compiler is required by the Khovanov backend on its first run.
- No Java runtime is required by the current backend.
- Enough disk space for the generated dataset; the full `10_3` run contains 7,790 text files.

## Development

Run examples and package checks before release. Python packages require Python 3.10 or newer. Build PyPI artifacts with:

```bash
poetry check
poetry build
```

## License

MIT. See `LICENSE`.
