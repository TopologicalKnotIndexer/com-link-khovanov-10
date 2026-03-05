import link_khovanov
import link_rep_to_pd_code
import com_link_gen_10
from tqdm import tqdm

import os

DIRNOW = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(DIRNOW, "data")

def generate_all(total_crs:int, max_prime_cnt:int):
    data_dir_now = os.path.join(DATA_DIR, f"com_link_gen_10-v{com_link_gen_10.get_version()}-com_link_gen-{total_crs}-{max_prime_cnt}")
    os.makedirs(data_dir_now, exist_ok=True)

    # 用于输出的数据
    data_list = com_link_gen_10.com_link_gen(total_crs, max_prime_cnt)

    for idx in tqdm(range(len(data_list))):
        filepath = os.path.join(data_dir_now, f"{idx+1:07d}.txt")
        item = data_list[idx]

        # 计算 pd_code
        try:
            pd_code_now = link_rep_to_pd_code.link_rep_to_pd_code(item)
        except Exception as e:
            print(f"Exception when caculate: \n{item}")
            raise e

        with open(filepath, "w") as fp:
            fp.write(
                ("// PD_CODE: " + str(pd_code_now) + "\n") +
                item)

def process_one_file(filepath:str):
    if not os.path.isfile(filepath):
        raise AssertionError()
    
    with open(filepath, "r") as fp:
        old_content = fp.read()

    # 如果这个文件中已经计算了 khovanov 同调，不需要重复计算
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

def process_khovanov(dir_to_process:str, mod:int, res:int):
    if not os.path.isdir(dir_to_process):
        raise FileNotFoundError()
    
    filelist = []
    for filename in os.listdir(dir_to_process):
        filepath = os.path.join(dir_to_process, filename)

        file_index = int(filename.replace(".txt", ""))
        if file_index % mod == res:
            filelist.append(filepath)

    for idx in tqdm(range(len(filelist))):
        filepath = filelist[idx]
        process_one_file(filepath)
        
if __name__ == "__main__":
    data_dir_now = os.path.join(DATA_DIR, f"com_link_gen_10-v0.0.4-com_link_gen-{10}-{3}")
    mod, res = input("mod res>>>").split()
    mod = int(mod)
    res = int(res)
    process_khovanov(data_dir_now, mod, res)
