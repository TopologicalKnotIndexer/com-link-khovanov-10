import inspect
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from importlib.metadata import PackageNotFoundError, version
from multiprocessing import freeze_support

import com_link_gen_10
import link_khovanov
import pd_code_to_diagram
import link_rep_to_pd_code
from tqdm import tqdm


DIRNOW = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(DIRNOW, "data")


def _com_link_gen_version():
    try:
        parameters = inspect.signature(com_link_gen_10.get_version).parameters
        if len(parameters) == 0:
            return com_link_gen_10.get_version()
        return com_link_gen_10.get_version("com-link-gen-10")
    except Exception:
        try:
            return version("com-link-gen-10")
        except PackageNotFoundError:
            return "unknown"


def get_data_dir(total_crs: int = 10, max_prime_cnt: int = 3):
    return os.path.join(
        DATA_DIR,
        f"com_link_gen_10-v{_com_link_gen_version()}-com_link_gen-{total_crs}-{max_prime_cnt}",
    )


def generate_all(total_crs: int, max_prime_cnt: int):
    data_dir_now = get_data_dir(total_crs, max_prime_cnt)
    os.makedirs(data_dir_now, exist_ok=True)

    data_list = com_link_gen_10.com_link_gen(total_crs, max_prime_cnt)

    for idx in tqdm(range(len(data_list))):
        filepath = os.path.join(data_dir_now, f"{idx + 1:07d}.txt")
        item = data_list[idx]

        try:
            pd_code_now = link_rep_to_pd_code.link_rep_to_pd_code(item)
            pd_code_now = pd_code_to_diagram.pd_code_sanity(pd_code_now)[1] # get normalized pd_code
        except Exception as e:
            print(f"Exception when calculate: \n{item}")
            raise e

        with open(filepath, "w") as fp:
            fp.write("// PD_CODE: " + str(pd_code_now) + "\n" + item)

    return data_dir_now


def _indexed_generated_files(dir_to_process: str):
    if not os.path.isdir(dir_to_process):
        raise FileNotFoundError(dir_to_process)

    indexed_files = []
    for filename in os.listdir(dir_to_process):
        if not filename.endswith(".txt"):
            continue

        file_stem = filename[:-len(".txt")]
        if not file_stem.isdigit():
            continue

        filepath = os.path.join(dir_to_process, filename)
        indexed_files.append((int(file_stem), filepath))

    indexed_files.sort(key=lambda item: item[0])
    return indexed_files


def process_one_file(filepath: str):
    if not os.path.isfile(filepath):
        raise AssertionError()

    with open(filepath, "r") as fp:
        old_content = fp.read()

    if old_content.find("KHOVANOV:") != -1:
        return

    pd_code = None
    for line in old_content.split("\n"):
        if line.find("PD_CODE:") != -1:
            pd_code = eval(line.split("PD_CODE:")[-1].strip())
            break

    if pd_code is None:
        raise AssertionError()

    khovanov_list = link_khovanov.link_khovanov(pd_code)
    new_content_prefix = "".join([
        "// KHOVANOV: " + str(one_khovanov) + "\n"
        for one_khovanov in khovanov_list
    ])

    with open(filepath, "w") as fp:
        fp.write(new_content_prefix + old_content)


def process_khovanov(dir_to_process: str, mod: int, res: int):
    if mod <= 0:
        raise ValueError("mod must be a positive integer")
    if res < 0 or res >= mod:
        raise ValueError("res must satisfy 0 <= res < mod")

    filelist = []
    for file_index, filepath in _indexed_generated_files(dir_to_process):
        if file_index % mod == res:
            filelist.append(filepath)

    for filepath in tqdm(filelist):
        process_one_file(filepath)


def process_khovanov_parallel(dir_to_process: str, process_count: int):
    process_count = int(process_count)
    if process_count <= 0:
        raise ValueError("process_count must be a positive integer")

    filelist = [filepath for _, filepath in _indexed_generated_files(dir_to_process)]
    if len(filelist) == 0:
        return

    if process_count == 1:
        for filepath in tqdm(filelist):
            process_one_file(filepath)
        return

    worker_count = min(process_count, len(filelist))
    with ProcessPoolExecutor(max_workers=worker_count) as executor:
        futures = [executor.submit(process_one_file, filepath) for filepath in filelist]
        for future in tqdm(as_completed(futures), total=len(futures)):
            future.result()


def process_khovanov_default(process_count: int, total_crs: int = 10, max_prime_cnt: int = 3):
    process_khovanov_parallel(get_data_dir(total_crs, max_prime_cnt), process_count)


if __name__ == "__main__":
    freeze_support()
    process_count = int(input("process_count>>>"))
    process_khovanov_default(process_count)
