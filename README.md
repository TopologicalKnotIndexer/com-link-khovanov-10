# com-link-khovanov-10

[![PyPI](https://img.shields.io/pypi/v/com-link-khovanov-10.svg)](https://pypi.org/project/com-link-khovanov-10/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

`com-link-khovanov-10` is a small Python utility for generating composite link
data up to 10 crossings and computing Khovanov homology from the generated link
representations.

The package combines three steps:

1. Generate composite link representations with `com_link_gen_10`.
2. Convert each link representation to PD code with `link_rep_to_pd_code`.
3. Compute Khovanov homology with `link_khovanov`.

## Installation

Install the package directly from PyPI:

```bash
pip install com-link-khovanov-10
```

To upgrade an existing installation:

```bash
pip install --upgrade com-link-khovanov-10
```

Using a virtual environment is recommended because generated data is written to
a `data` directory next to the installed package module.

## Quick Start

Because the distribution name contains hyphens, import the package module with
`importlib`:

```python
import importlib

clk = importlib.import_module("com-link-khovanov-10.main")

# Generate composite link files and their PD codes.
clk.generate_all(total_crs=10, max_prime_cnt=3)

# Compute Khovanov homology for generated files.
clk.process_khovanov(
    dir_to_process="path/to/generated/data/directory",
    mod=1,
    res=0,
)
```

`generate_all(total_crs, max_prime_cnt)` creates a directory named like:

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

## Batch Processing

`process_khovanov(dir_to_process, mod, res)` supports simple modulo-based job
splitting. A file is processed only when:

```text
file_index % mod == res
```

For example, to split the work across four workers, run the same data directory
with:

```python
clk.process_khovanov(data_dir, mod=4, res=0)
clk.process_khovanov(data_dir, mod=4, res=1)
clk.process_khovanov(data_dir, mod=4, res=2)
clk.process_khovanov(data_dir, mod=4, res=3)
```

## Command-Line Usage

The package can also be executed as a module:

```bash
python -m com-link-khovanov-10.main
```

The interactive prompt expects two integers:

```text
mod res>>>
```

For example:

```text
mod res>>>4 0
```

The current command-line entry point is configured for the generated data set:

```text
com_link_gen_10-v0.0.4-com_link_gen-10-3
```

For other crossing counts, prime-factor limits, or generator versions, use the
Python API shown above.

## API Reference

### `generate_all(total_crs: int, max_prime_cnt: int)`

Generate all composite links for the requested crossing number and maximum
number of prime link factors. The function writes one text file per generated
link and stores the corresponding PD code in the file header.

### `process_one_file(filepath: str)`

Compute Khovanov homology for a single generated file. If the file already
contains `KHOVANOV:`, it is left unchanged.

### `process_khovanov(dir_to_process: str, mod: int, res: int)`

Compute Khovanov homology for every matching generated file in a directory,
using modulo-based filtering for parallel or distributed runs.

## Related Packages

This project relies on:

- `com_link_gen_10`
- `link_rep_to_pd_code`
- `link_khovanov`
- `tqdm`

These dependencies are expected to be available in the Python environment after
installing the package from PyPI.

## License

This project is released under the MIT License. See [LICENSE](LICENSE) for
details.
