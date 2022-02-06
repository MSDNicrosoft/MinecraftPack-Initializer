# -*- coding: UTF-8 -*-
from __future__ import annotations
import os
import re
import shutil
import sys
import urllib
import zipfile
from time import sleep
import gc as gc_function
from urllib.error import HTTPError, URLError
import urllib.request
from tqdm import tqdm
import multitasking
import signal
import asyncio
# from os.path import join
# from subprocess import CalledProcessError
# from shutil import which
# import subprocess
# import winreg

signal.signal(signal.SIGINT, multitasking.killall)

########################################################

Pack_Name = "Minecraft 1.17.1 Fabric"
Author_Name = "MSDNicrosoft"
Project_Url = "https://github.com/MSDNicroosft/MinecraftPack-Initializer"
Program_Name = f"{Pack_Name} 整合初始化工具"
Version = "1.0.0"

########################################################


def clean_screen():
    old_stdout = sys.stdout  # 保存默认的 Python 标准输出
    os.system('cls')
    sys.stdout = old_stdout  # 恢复 Python 默认的标准输出


def command(command):
    os.system(command)


def gc():
    gc_function.collect()


async def download_file(url, filename):
    try:
        print(f"下载 {filename} 中...")
        f = urllib.request.urlopen(url)
        with open(filename, 'wb+') as local_file:
            await local_file.write(f.read())
        del f
    except HTTPError:
        print("网络错误 !")
    except URLError:
        print("链接错误 !")


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



def extract_file(src_file, target_path):
    file = zipfile.ZipFile(src_file)
    try:
        file.extractall(path=target_path)
    except RuntimeError:
        print("解压失败 !")
        file.close()


def select_launcher():
    command(f"title {Program_Name} - 选择使用的启动器")
    Launcher_Selection = str.upper(
        input("你想使用哪个启动器来启动你的游戏 :\n" + "HMCL \ PCL2" + "\n")
        )
    if Launcher_Selection =="HMCL":
        return True
    elif Launcher_Selection == "PCL":
        return False
    else:
        clean_screen()
        print("输入错误,请重试 !")
        select_launcher()    


def java_confirm():
    clean_screen()
    command(f"title {Program_Name} Java 确认")
    Java_Selection = str.upper(
        input("你是否已安装 Java 17 ?(y/n)")
        )
    if Java_Selection == "Y":
        return True
    elif Java_Selection == "N":
        return False
    else:
        clean_screen()
        print("输入错误,请重试!")
        java_confirm()


async def java_process():
    if not Java_Selection:
        print("正在下载文件")
        asyncio.run(
            download_file(
            'https://mirrors.tuna.tsinghua.edu.cn/AdoptOpenJDK/16/jre/x64/windows/ibm-semeru-open-jre_x64_windows_16.0.2_7_openj9-0.27.0.zip',
            'ibm-semeru-open-jre_x64_windows_16.0.2_7_openj9-0.27.0.zip')
            )
        sleep(0.4)
        extract_file(r'ibm-semeru-open-jre_x64_windows_16.0.2_7_openj9-0.27.0.zip', None)
        try:
            os.remove(r'ibm-semeru-open-jre_x64_windows_16.0.2_7_openj9-0.27.0.zip')
            command('ren jdk-16.0.1+9-jre runtime')
            os.remove(r'runtime/lib/src.zip')
        except FileNotFoundError:
            pass
        await shutil.move("runtime", ".minecraft/runtime")
        try:
            os.remove("jdk-16.0.1+9-jre")
        except FileNotFoundError:
            pass



def launcher_process():
    if Launcher_Selection:
        asyncio.run(
            download_file(
            'http://ci.huangyuhui.net/job/HMCL/lastSuccessfulBuild/artifact/HMCL/build/libs/HMCL-3.3.196.exe',
            'HMCL.exe')
            )
    else:
        asyncio.run(
            download_file('https://download1325.mediafire.com/w26ivjyiawbg/4pttqgt3ogrp848/PCL.exe', 'PCL.exe')
        )



##############################################################
clean_screen()
command(f"title {Program_Name} - 加载程序")
print("程序加载中...")
for _ in tqdm(range(1, 101)):
    sleep(0.01)
del _
print("完成!")
sleep(0.6)
clean_screen()
command(f"title {Program_Name}")
print(f"欢迎使用 {Program_Name} \n程序作者: {Author_Name} \n 项目地址 : {Project_Url} \n 当前版本 {Version} \n\n")
input("按下回车键以开始初始化")
clean_screen()
Launcher_Selection = select_launcher()
Java_Selection = java_confirm()
command(f"title {Program_Name} 文件补全")
clean_screen()
java_process()
launcher_process()
command(f"title {Program_Name}")
clean_screen()
print(f"{Program_Name} 已初始化完成 !")
print("你可以删除此程序了 !")
input("\n\n按下回车退出此程序")
