# -*- coding: UTF-8 -*-
from __future__ import annotations

import os
import shutil
import sys
import urllib
import zipfile
from time import sleep
from urllib.error import HTTPError, URLError
import urllib.request
from tqdm import tqdm
import requests
import re

# import multitasking
# import signal

# from subprocess import CalledProcessError
# from shutil import which
# import subprocess
# import winreg

# signal.signal(signal.SIGINT, multitasking.killall)

########################################################

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


def simplify_str(string: str):
    """Remove unnecessary blanks and all capitalized."""
    return string.upper().strip()


def str2bool(v: str):
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
    def url2json(url: str):
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.36"
        }
        try:
            data = requests.get(url=url, headers=headers)
            return data.json()
        except (requests.HTTPError, requests.ConnectionError) as e:
            print("网络出现了错误")
            print(e)
        except requests.JSONDecodeError as e:
            print("解析错误")
            print(e)

    @staticmethod
    def launcher(name: str = None, dist_type: str = None, channel: str = None):
        if simplify_str(name) == "HMCL":
            if simplify_str(channel) in ["STABLE", "DEV"]:  # 版本核对
                SRC_URL = f"https://hmcl.huangyuhui.net/api/update_link?channel={channel.lower()}&download_link=true"
                if simplify_str(dist_type) in ["EXE", "JAR"]:  # 文件类型核对
                    target_url = download_url.url2json(SRC_URL)[dist_type.lower()]
                else:
                    print("HMCL 所选的文件格式有误")
                    return
            else:
                print("HMCL 所选的频道有误")
                return

        elif simplify_str(name) == "PCL":
            SRC_URL = "https://afdian.net/api/post/get-detail?post_id=0164034c016c11ebafcb52540025c377"
            unresolved_json = download_url.url2json(SRC_URL)
            html_data = unresolved_json["data"]["post"]["content"]  # 获取动态正文
            lanzou_URI = re.findall(  # 匹配下载链接（蓝奏云），但数据类型为 List
                '(?<=rel="noopener noreferrer" target="_blank">).*(?=</a>\n<strong>\u4e0b\u8f7d 2\uff1a)',
                html_data
            )
            target_url = "https://api.hanximeng.com/lanzou/?url=" + lanzou_URI[0]
        else:
            return

        return target_url

    @staticmethod
    def java(version: int, dist_type: str):
        SRC_URL = f"https://api.adoptium.net/v3/assets/latest/{version}/hotspot?os=windows"
        MIRROR_URL = f"https://mirrors.tuna.tsinghua.edu.cn/Adoptium/{version}/jdk/x64/windows/"
        ADOPTIUM_VERSION_LIST = [8, 11, 17, 18]
        if version not in ADOPTIUM_VERSION_LIST:  # Java 版本核对（仅可下载的）
            return
        unresolved_json = download_url.url2json(SRC_URL)
        if simplify_str(dist_type) == "ZIP":
            origin_url = str(unresolved_json[1]["binary"]["package"]["link"])
        elif simplify_str(dist_type) in ["EXE", "MSI"]:
            origin_url = unresolved_json[1]["binary"]["installer"]["link"]
        else:
            return
        file_name = origin_url.split("/")
        target_url = MIRROR_URL + file_name[-1]
        return target_url


def download_file(url, filename):
    try:
        print(f"下载 {filename} 中...")
        f = urllib.request.urlopen(url)
        with open(filename, 'wb+') as local_file:
            local_file.write(f.read())
        del f
    except HTTPError:
        print("网络错误 !")
    except URLError:
        print("链接错误 !")


def extract_file(src_file, target_path, remove_src_after_extracted):
    with zipfile.ZipFile(src_file) as f:
        try:
            f.extractall(path=target_path)
        except RuntimeError:
            print(f"解压失败 !")
    if remove_src_after_extracted:
        try:
            os.remove(src_file)
        except FileNotFoundError:
            pass


def check_java_version():  # TODO: 通过 MC 版本判断安装哪个版本的 Java
    ...


"""
def check_java():
    results = []
    if not results:
        for flag in [winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY]:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'Software\JavaSoft\Java Development Kit', 0,
                                     winreg.KEY_READ | flag)
                version, _ = winreg.QueryValueEx(key, 'CurrentVersion')
                key.Close()
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'Software\JavaSoft\Java Development Kit\%s' % version,
                                     0, winreg.KEY_READ | flag)
                path, _ = winreg.QueryValueEx(key, 'JavaHome')
                key.Close()
                path = join(str(path), 'bin')
                subprocess.run(['"%s"' % join(path, 'java'), ' -version'], stdout=open(os.devnull, 'w'),
                               stderr=subprocess.STDOUT, check=True)
                results.append(path)
            except (CalledProcessError, OSError):
                pass
    if not results:
        try:
            subprocess.run(['java', '-version'], stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT, check=True)
            results.append('')
        except (CalledProcessError, OSError):
            pass
    if not results and 'ProgramW6432' in os.environ:
        results.append(which('java.exe', path=os.environ['ProgramW6432']))
    if not results and 'ProgramFiles' in os.environ:
        results.append(which('java.exe', path=os.environ['ProgramFiles']))
    if not results and 'ProgramFiles(x86)' in os.environ:
        results.append(which('java.exe', path=os.environ['ProgramFiles(x86)']))
    results = [path for path in results if path is not None]
    if not results:
        return False
    else:
        return True
"""


def select_launcher():
    command(f"title {PROGRAM_NAME} - 选择使用的启动器")
    Launcher_Selection = str(
        input("你想使用哪个启动器来启动你的游戏(\"HMCL \ PCL\"):")
    )
    if not simplify_str(Launcher_Selection) in ["Y", "N"]:
        clean_screen()
        print("输入错误,请重试 !")
        select_launcher()
    else:
        return str2bool(Launcher_Selection)


def java_confirm():
    clean_screen()
    command(f"title {PROGRAM_NAME} Java 确认")
    Java_Selection = str(
        input("你是否已安装 Java 17 ?(y/n)")
    )
    if not simplify_str(Java_Selection) in ["Y", "N"]:
        clean_screen()
        print("输入错误,请重试 !")
    else:
        return str2bool(Java_Selection)


def java_process():
    if not java_confirm():
        print("正在下载文件")
        download_file(  # TODO: 等芒果搞完国内源解析和 ZIP 支持
            download_url.java(17, "zip"),
            "adoptium-jdk-17.zip")
        sleep(0.4)
        extract_file("adoptium-jdk-17.zip", "jdk-17", True)
        shutil.move("jdk-17", ".minecraft/runtime")


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
        extract_file("PCL.zip", None, True)


##############################################################
clean_screen()
check_platform()
command(f"title {PROGRAM_NAME}")
print(f"欢迎使用 {PROGRAM_NAME} \n程序作者: {AUTHOR_NAME} \n项目地址 : {PROJECT_URL} \n当前版本 {VERSION} \n\n")
input("按下回车键以开始初始化")
clean_screen()
command(f"title {PROGRAM_NAME} 文件补全")
clean_screen()
java_process()
launcher_process()
command(f"title {PROGRAM_NAME}")
clean_screen()
print(f"{PROGRAM_NAME} 已初始化完成 !")
print("你可以删除此程序了 !")
input("\n\n按下回车退出此程序")
