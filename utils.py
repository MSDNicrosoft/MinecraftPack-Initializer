# -*- coding: UTF-8 -*-
import sys
import os
from retry import retry
from tqdm import tqdm
import requests
import zipfile


def check_platform():
    if not sys.platform.startswith('win'):
        print("本程序仅限 Windows 平台下运行")
        exit(-1)


def clean_screen():  # 如果直接调用会导致在清空后出现个 0
    old_stdout = sys.stdout  # 保存默认的 Python 标准输出
    os.system('cls')
    sys.stdout = old_stdout  # 恢复 Python 默认的标准输出


def simplify_str(string: str) -> str:
    """Remove unnecessary blanks and all capitalized."""
    return string.upper().strip()


def str2bool(v: str) -> bool:
    if isinstance(v, bool):
        return v
    elif simplify_str(v) == "Y":
        return True
    elif simplify_str(v) == "N":
        return False


def warp(string: list) -> str:
    return "\n".join(string)


def command(text: str):
    os.system(text)


@retry(tries=3)
def download_file(target_url, file_name=None) -> None:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.36 "
    }

    head = requests.head(target_url, headers=headers)  # 仅获取响应头部信息
    file_size = head.headers.get('Content-Length')  # 以 B 为单位的文件大小
    if file_size is not None:
        file_size = int(file_size)

    if file_name is None:  # 不提供文件名则默认使用地址中的文件名（不带参数）
        file_name = target_url.split("/")[-1].split("?")[0]

    response = requests.get(url=target_url, headers=headers, stream=True)
    chunk_size = 10240  # 一块文件的大小
    bar = tqdm(total=file_size, desc=f'下载文件 {file_name}', unit_scale=True, unit_divisor=1024, unit='B')
    with open(file_name, mode='wb') as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            f.write(chunk)
            bar.update(chunk_size)
    bar.close()  # 关闭进度条


def extract_file(src_file, target_path, remove_src_after_extracted=False) -> None:
    with zipfile.ZipFile(src_file) as f:
        try:
            f.extractall(path=target_path)
        except RuntimeError:
            print(f"解压失败！")
    if remove_src_after_extracted:
        try:
            os.remove(src_file)
        except FileNotFoundError:
            pass
