# -*- coding: UTF-8 -*-

import json
import os
import shutil
import subprocess
import sys
import zipfile
from time import sleep
from retry import retry
from tqdm import tqdm
import requests
import re

########################################################

MC_VERSION = "1.17.1"  # 需提供 Mojang 官方的版本名，最低支持 1.7.10
VERSION_FOLDER_NAME = "1.17.1 Fabric"  # `.minecraft/versions` 目录下的版本文件夹
PACK_NAME = "Minecraft 1.17.1 Fabric"
AUTHOR_NAME = "MSDNicrosoft"
PROJECT_URL = "https://github.com/MSDNicroosft/MinecraftPack-Initializer"
PROGRAM_NAME = f"{PACK_NAME} 整合初始化工具"
VERSION = "1.0.0"


########################################################


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


def command(text: str):
    os.system(text)


class download_url:

    @staticmethod
    def url2json(url: str) -> dict:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.36"
        }
        try:
            data = requests.get(url=url, headers=headers)
            return data.json()
        except (requests.HTTPError, requests.ConnectionError):
            print("网络错误")
        except requests.JSONDecodeError:
            print("解析错误")

    @staticmethod
    def launcher(name: str = None, dist_type: str = None, channel: str = None) -> str:
        if simplify_str(name) == "HMCL":
            if simplify_str(channel) in ["STABLE", "DEV"]:  # 版本核对
                SRC_URL = f"https://hmcl.huangyuhui.net/api/update_link?channel={channel.lower()}&download_link=true"
                if simplify_str(dist_type) in ["EXE", "JAR"]:  # 文件类型核对
                    target_url = download_url.url2json(SRC_URL)[dist_type.lower()]
                else:
                    raise "HMCL 所选的文件格式有误"
            else:
                raise "HMCL 所选的频道有误"

        elif simplify_str(name) == "PCL":
            SRC_URL = "https://afdian.net/api/post/get-detail?post_id=0164034c016c11ebafcb52540025c377"
            unresolved_json = download_url.url2json(SRC_URL)
            html_data = unresolved_json["data"]["post"]["content"]  # 获取动态正文
            lanzou_URI = re.findall(  # 匹配下载链接（蓝奏云），但数据类型为 List
                '(?<=rel="noopener noreferrer" target="_blank">).*(?=</a>\n<strong>\u4e0b\u8f7d 2\uff1a)',
                html_data
            )
            direct_link_json = download_url.url2json("https://api.hanximeng.com/lanzou/?url=" + lanzou_URI[0])
            if direct_link_json["code"] == 200:
                target_url = direct_link_json["downUrl"]
            else:
                raise "解析 API 出错"
        else:
            raise "无法解析您所选的启动器"
        return target_url

    @staticmethod
    def java(version: int, dist_type: str) -> str:
        ADOPTIUM_VERSION_LIST = [8, 11, 17, 18]
        if version not in ADOPTIUM_VERSION_LIST:  # Java 版本核对（仅可下载的）
            for exist_support_java in ADOPTIUM_VERSION_LIST:
                if exist_support_java >= version:
                    version = exist_support_java
                    break
        SRC_URL = f"https://api.adoptium.net/v3/assets/latest/{version}/hotspot?os=windows"
        MIRROR_URL = f"https://mirrors.tuna.tsinghua.edu.cn/Adoptium/{version}/jdk/x64/windows/"
        unresolved_json = download_url.url2json(SRC_URL)
        if simplify_str(dist_type) == "ZIP":
            origin_url = str(unresolved_json[1]["binary"]["package"]["link"])
        elif simplify_str(dist_type) in ["EXE", "MSI"]:
            origin_url = unresolved_json[1]["binary"]["installer"]["link"]
        else:
            raise "文件类型错误"
        file_name = origin_url.split("/")
        target_url = MIRROR_URL + file_name[-1]
        return target_url


@retry(tries=3)
def download_file(target_url, file_name=None) -> None:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.36"
    }

    head = requests.head(target_url, headers=headers)  # 仅获取响应头部信息
    file_size = head.headers.get('Content-Length')  # 以 B 为单位的文件大小
    if file_size is not None:
        file_size = int(file_size)

    if file_name is None:  # 不提供文件名则默认使用地址中的文件名（不带参数）
        file_name = target_url.split("/")[-1].split("?")[0]

    response = requests.get(url=target_url, headers=headers, stream=True)
    # 一块文件的大小
    chunk_size = 10240
    bar = tqdm(total=file_size, desc=f'下载文件 {file_name}', unit_scale=True, unit_divisor=1024, unit='B')
    with open(file_name, mode='wb') as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            f.write(chunk)
            bar.update(chunk_size)
    bar.close()  # 关闭进度条


def extract_file(src_file, target_path, remove_src_after_extracted) -> None:
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


def check_java_version() -> int:
    # 通过提供的 MC 版本名获取
    MANIFEST_URL = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
    global_manifest = download_url.url2json(MANIFEST_URL)
    for version in global_manifest["versions"]:
        # 如果存在 `id` 键，并且 `id` 键的值等于 `MC_VERSION`，并且存在 `url` 键
        if version["id"] and version["id"] == MC_VERSION and version["url"]:
            target_version = download_url.url2json(version["url"])
            required_java_version = int(target_version["javaVersion"]["majorVersion"])
            break
    else:
        # 读取包内的 json 获取
        try:
            with open(f"./.minecraft/versions/{VERSION_FOLDER_NAME}/{VERSION_FOLDER_NAME}.json", 'r',
                      encoding='UTF-8') as f:
                LOCAL_TARGET_VERSION = json.load(f)
        except FileNotFoundError:
            print("版本信息文件未找到!")
            required_java_version = 17  # 如果没有默认使用 Java 17
        else:
            required_java_version = int(LOCAL_TARGET_VERSION["javaVersion"]["majorVersion"])
    return required_java_version


def check_java() -> bool:
    RESULT = False

    def parse_java_version(full_version: str) -> int:
        if full_version.find("_") == -1:  # JDK
            return int(full_version.split(".")[0])
        else:  # JRE
            return int(full_version.split(".")[1])

    required_java_version = check_java_version()  # 获取此包最低所需的 Java 版本
    found_java_execute_result = []
    # 调用系统命令寻找 `java.exe`，以换行符分隔，转换为列表
    where_execute_result = subprocess.getoutput("where /f java.exe").split("\n")
    for java in where_execute_result:  # 执行 `java -version`，将执行的结果添加至列表
        found_java_execute_result.append(subprocess.getoutput(f"{java} -version"))
    found_java_version = []
    for version in found_java_execute_result:
        found_java_version.append(
            parse_java_version(re.findall('(?<=version ").*(?=")', version)[0])
        )
    found_java_version = list(set(found_java_version))  # 使用 Python 集合特性，删除重复的值
    for version in found_java_version:  # 将存在的 Java 的版本与所需的最低版本比较
        if version >= required_java_version:  # 只要有高于所需版本的 Java (1.7.2 除外)就返回 True（无需额外下载安装）
            RESULT = True
    return RESULT


def select_launcher() -> bool:
    command(f"title {PROGRAM_NAME} - 选择使用的启动器")
    Launcher_Selection = str(
        input("你想使用哪个启动器来启动你的游戏(HMCL \ PCL):")
    )
    if not simplify_str(Launcher_Selection) in ["HMCL", "PCL"]:
        clean_screen()
        print("输入错误,请重试 !")
        select_launcher()
    else:
        if simplify_str(Launcher_Selection) == "HMCL":
            return True
        else:
            return False


def java_process():
    if not check_java():
        print("正在下载文件")
        download_file(
            download_url.java(
                version=check_java_version(),
                dist_type="zip"),
            "adoptium-jdk.zip")
        sleep(0.4)
        extract_file("adoptium-jdk.zip", "jdk", remove_src_after_extracted=True)
        shutil.move("jdk", ".minecraft/runtime")


def launcher_process():
    if select_launcher():
        download_file(
            download_url.launcher("HMCL", "EXE", "STABLE"),
            "HMCL.exe")
    else:
        download_file(
            download_url.launcher("PCL"),
            "PCL.zip"
        )
        extract_file("PCL.zip", None, remove_src_after_extracted=True)


##############################################################
if __name__ == '__main__':
    clean_screen()
    check_platform()
    command(f"title {PROGRAM_NAME}")
    print(f"""
欢迎使用 {PROGRAM_NAME}
程序作者: {AUTHOR_NAME}
项目地址: {PROJECT_URL}
当前版本: {VERSION}


    """)
    input("按下回车键以开始初始化")
    clean_screen()
    command(f"title {PROGRAM_NAME} 文件补全")
    clean_screen()
    java_process()
    launcher_process()
    command(f"title {PROGRAM_NAME}")
    clean_screen()
    print(f"{PROGRAM_NAME} 已为您初始化完成 !")
    print("你可以删除此程序了 !")
    input("\n\n按下回车退出此程序")
