# com-link-khovanov-10

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

`com-link-khovanov-10` is a small Python utility for generating composite link
data up to 10 crossings and computing Khovanov homology from the generated link
representations.

The package combines three steps:

1. Generate composite link representations with `com_link_gen_10`.
2. Convert each link representation to PD code with `link_rep_to_pd_code`.
3. Compute Khovanov homology with `link_khovanov`.

## Setup

This project is intended to be used from source. Clone the repository first:

```bash
git clone https://github.com/TopologicalKnotIndexer/com-link-khovanov-10.git
cd com-link-khovanov-10
```

Then install the direct Python dependencies required by `main.py`:

```bash
python -m pip install com-link-gen-10 link-rep-to-pd-code pd-code-to-diagram link-khovanov tqdm
```

These package names use hyphens on PyPI, but they are imported with underscores
in Python:

```text
com-link-gen-10        -> import com_link_gen_10
link-rep-to-pd-code   -> import link_rep_to_pd_code
pd-code-to-diagram    -> import pd_code_to_diagram
link-khovanov         -> import link_khovanov
tqdm                  -> from tqdm import tqdm
```

You can verify the dependency installation with:

```bash
python -c "import com_link_gen_10, link_rep_to_pd_code, pd_code_to_diagram, link_khovanov, tqdm"
```

This repository itself is not published as a PyPI package; the command above
only installs its dependency packages.

Using a virtual environment is recommended because generated data is written to a
`data` directory inside this repository.

If importing this project fails with:

```text
ModuleNotFoundError: No module named 'link_khovanov'
```

install the missing dependency with:

```bash
python -m pip install link-khovanov
```

## Quick Start

Because the repository package directory contains hyphens, import the module with
`importlib` from the repository root:

```python
import importlib

if __name__ == "__main__":
    clk = importlib.import_module("com-link-khovanov-10.main")

    # Generate 10-crossing composite link files and their PD codes.
    clk.generate_all(total_crs=10, max_prime_cnt=3, process_count=16)

    # Compute Khovanov homology with four worker processes.
    clk.process_khovanov_default(process_count=16)
```

`generate_all(total_crs, max_prime_cnt, process_count)` creates a directory named
like:

```text
com_link_gen_10-v<version>-com_link_gen-<total_crs>-<max_prime_cnt>
```

Each generated file is named with a zero-padded numeric index, for example:

```text
0000001.txt
0000002.txt
0000003.txt
```

## Output Format

After generation, each file contains a PD code header followed by the original
link representation:

```text
// PD_CODE: [...]
<link representation>
```

After Khovanov processing, one or more Khovanov headers are prepended:

```text
// KHOVANOV: ...
// PD_CODE: [...]
<link representation>
```

Files that already contain `KHOVANOV:` are skipped, so interrupted runs can be
resumed safely.

## Parallel Processing

Use `generate_all(total_crs, max_prime_cnt, process_count)` to generate files
and normalize PD codes with a fixed number of worker processes:

```python
data_dir = clk.generate_all(total_crs=10, max_prime_cnt=3, process_count=8)
```

Use `process_khovanov_default(process_count)` to process the default generated
10-crossing data set with a fixed number of worker processes:

```python
clk.process_khovanov_default(process_count=8)
```

The function discovers generated `.txt` files, splits them across a
`ProcessPoolExecutor`, and updates the progress bar as each file finishes. Files
that already contain `KHOVANOV:` are still skipped by `process_one_file`, so the
parallel run can be resumed after an interruption.

For a custom generated data directory, use
`process_khovanov_parallel(dir_to_process, process_count)`:

```python
data_dir = clk.generate_all(total_crs=9, max_prime_cnt=2, process_count=8)
clk.process_khovanov_parallel(data_dir, process_count=8)
```

On Windows, put multiprocessing calls inside a script guarded by
`if __name__ == "__main__":`:

```python
import importlib


if __name__ == "__main__":
    clk = importlib.import_module("com-link-khovanov-10.main")
    clk.generate_all(total_crs=10, max_prime_cnt=3, process_count=28)
    clk.process_khovanov_default(process_count=28)
```

The older `process_khovanov(dir_to_process, mod, res)` modulo-splitting API is
still available for compatibility with existing scripts.

## Command-Line Usage

The package can also be executed as a module:

```bash
python -m com-link-khovanov-10.main
```

The interactive prompt expects one integer:

```text
process_count>>>
```

For example:

```text
process_count>>>8
```

The command-line entry point is configured for the generated 10-crossing data
set:

```text
com_link_gen_10-v<installed-com-link-gen-10-version>-com_link_gen-10-3
```

For other crossing counts, prime-factor limits, or generator versions, use the
Python API shown above.

## API Reference

### `generate_all(total_crs: int, max_prime_cnt: int, process_count: int = 1)`

Generate all composite links for the requested crossing number and maximum
number of prime link factors. The function writes one text file per generated
link, stores the corresponding PD code in the file header, and returns the
generated data directory. `process_count` controls how many worker processes are
used for PD-code conversion, normalization, and file writing.

### `process_one_file(filepath: str)`

Compute Khovanov homology for a single generated file. If the file already
contains `KHOVANOV:`, it is left unchanged.

### `get_data_dir(total_crs: int = 10, max_prime_cnt: int = 3)`

Return the generated data directory path for a crossing number and prime-factor
limit.

### `process_khovanov_default(process_count: int, total_crs: int = 10, max_prime_cnt: int = 3)`

Compute Khovanov homology for the generated data directory selected by
`total_crs` and `max_prime_cnt`. The default call only requires `process_count`.

### `process_khovanov_parallel(dir_to_process: str, process_count: int)`

Compute Khovanov homology for every generated file in a directory using
`process_count` worker processes.

### `process_khovanov(dir_to_process: str, mod: int, res: int)`

Compute Khovanov homology for every matching generated file in a directory,
using modulo-based filtering. This legacy API is kept for compatibility.

## Related Packages

Direct dependencies:

- `com-link-gen-10` / `com_link_gen_10`
- `link-rep-to-pd-code` / `link_rep_to_pd_code`
- `pd-code-to-diagram` / `pd_code_to_diagram`
- `link-khovanov` / `link_khovanov`
- `tqdm`

The direct packages pull in additional transitive dependencies automatically,
including `group-diagram-combination`, `prime-link-knot-10`, `link-rep`,
`pd-code-connected-sum`, `pd-code-components`, `pd-code-sanity`,
`javakh-interface`, and related `pd-code-*` helper packages.

## License

This project is released under the MIT License. See [LICENSE](LICENSE) for
details.
