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


def clean_screen():  # 如果直接调用会导致在清空后出现个 0
    old_stdout = sys.stdout  # 保存默认的 Python 标准输出
    if sys.platform.startswith('linux'):
        os.system('clear')
    elif sys.platform.startswith('win'):
        os.system('cls')
    elif sys.platform.startswith('darwin'):
        os.system('clear')
    sys.stdout = old_stdout  # 恢复 Python 默认的标准输出


def str2bool(v: str):
    if isinstance(v, bool):
        return v
    elif v.upper().strip() == "Y":
        return True
    elif v.upper().strip() == "N":
        return False


def command(text):
    os.system(text)


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
    if not Launcher_Selection.upper().strip() in ["Y", "N"]:
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
    if not Java_Selection.upper().strip() in ["Y", "N"]:
        clean_screen()
        print("输入错误,请重试 !")
    else:
        return str2bool(Java_Selection)


def java_process():
    if not java_confirm():
        print("正在下载文件")
        download_file(
            '',  # TODO: 等芒果搞完国内源解析和 ZIP 支持
            'adoptium-jdk-17.zip')
        sleep(0.4)
        extract_file('adoptium-jdk-17.zip', 'jdk-17', True)
        shutil.move("jdk-17", ".minecraft/runtime")


def launcher_process():
    if select_launcher():
        download_file(
            'https://assets.bluemangoo.net/api/rdl?name=hmcl',
            'HMCL.exe')
    else:
        download_file('https://assets.bluemangoo.net/api/rdl?name=pcl', 'PCL.zip')
        extract_file('PCL.zip', None, True)


##############################################################
clean_screen()
command(f"title {PROGRAM_NAME} - 加载程序")
print("程序加载中...")
for _ in tqdm(range(1, 51)):
    sleep(0.01)
del _
print("完成!")
sleep(0.5)
clean_screen()
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
