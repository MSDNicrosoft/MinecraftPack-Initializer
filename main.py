# -*- coding: UTF-8 -*-
from __future__ import annotations
import os
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
from os.path import join
from subprocess import CalledProcessError
from shutil import which
import subprocess
import winreg

signal.signal(signal.SIGINT, multitasking.killall)

########################################################

Pack_Name = "Minecraft 1.17.1 Fabric"
Author_Name = "MSDNicrosoft"
Project_Url = "https://github.com/MSDNicroosft"
Program_Name = Pack_Name + " 整合初始化工具"
Version = "1.0.0"

########################################################

Java_Selection = None
Launcher_Selection = None
file_size_mb = None
Java_Exist = None


############################################################


def clean_screen():
    old_stdout = sys.stdout
    os.system('cls')
    sys.stdout = old_stdout


def console_command(command):
    os.system(command)


def gc():
    gc_function.collect()


def download_file(url, filename):
    try:
        print(f'下载 {filename} 中...')
        f = urllib.request.urlopen(url)
        with open(filename, 'wb+') as local_file:
            local_file.write(f.read())
    except HTTPError:
        print("网络错误！")
    except URLError:
        print("链接错误！")


def check_java():
    global Java_Exist
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
        Java_Exist = False
    else:
        Java_Exist = True


def extract_file(src_file, target_path):
    file = zipfile.ZipFile(src_file)
    try:
        file.extractall(path=target_path)
    except RuntimeError:
        print("解压失败！")
        file.close()


def select_launcher():
    global Launcher_Selection
    console_command('title ' + Program_Name + " - 选择使用的启动器")
    Launcher_Selection = input("你想使用哪个启动器来启动你的游戏：\n" + "HMCL \ PCL2" + "\n")
    if Launcher_Selection not in [
        "HMCL", "HMCl", "HMcl", "HmCL", "HmCl", "Hmcl", "hmCL", "hmCl", "hmcl", "hMCL", "hMcl", "hMCl", "hMcL",
        "PCL2", "PCl2", "Pcl2", "PcL2", "pCL2", "pCl2", "pcL2", "pcl", "PCL", "PCl", "Pcl", "PcL", "pCL", "pCl", "pcL"]:
        clean_screen()
        print("输入错误，请重试！")
        select_launcher()
    elif Launcher_Selection in [
        "HMCL", "HMCl", "HMcl", "HmCL", "HmCl", "Hmcl", "hmCL", "hmCl", "hmcl", "hMCL", "hMcl", "hMCl", "hMcL", "HmcL"
                                                                                                                "PCL2",
        "PCl2", "Pcl2", "PcL2", "pCL2", "pCl2", "pcL2", "pcl", "PCL", "PCl", "Pcl", "PcL", "pCL", "pCl", "pcL"]:
        if Launcher_Selection in ["HMCL", "HMCl", "HMcl", "HmCL", "HmCl", "Hmcl", "hmCL", "hmCl", "hmcl", "hMCL", "HmcL"
                                                                                                                  "hMcl",
                                  "hMCl", "hMcL"]:
            Launcher_Selection = True
        else:
            Launcher_Selection = False


def java_confirm():
    global Java_Selection
    clean_screen()
    console_command('title ' + Program_Name + " - Java 确认")
    Java_Selection = input("你是否已安装 Java 16？（y/n）")
    if Java_Selection not in ["y", "Y", "n", "N"]:
        clean_screen()
        print("输入错误，请重试！")
        java_confirm()
    elif Java_Selection in ["y", "Y", "n", "N"]:
        if Java_Selection in ["y", "Y"]:
            Java_Selection = True
        else:
            Java_Selection = False


def java_process():
    if not Java_Selection:
        print("正在下载文件")
        download_file(
            r'https://mirrors.tuna.tsinghua.edu.cn/AdoptOpenJDK/16/jre/x64/windows/OpenJDK16U-jre_x64_windows_hotspot_16.0.1_9.zip',
            f'OpenJDK16U-jre_x64_windows_hotspot_16.0.1_9.zip')
        sleep(0.4)
        extract_file(r'OpenJDK16U-jre_x64_windows_hotspot_16.0.1_9.zip', None)
        try:
            os.remove(r'OpenJDK16U-jre_x64_windows_hotspot_16.0.1_9.zip')
            console_command('ren jdk-16.0.1+9-jre runtime')
            os.remove(r'runtime/lib/src.zip')
        except FileNotFoundError:
            pass
        shutil.move("runtime", ".minecraft/runtime")
        sleep(2)
        try:
            os.remove("jdk-16.0.1+9-jre")
        except FileNotFoundError:
            pass


def launcher_process():
    if Launcher_Selection:
        check_java()
        download_file(
            r'http://ci.huangyuhui.net/job/HMCL/lastSuccessfulBuild/artifact/HMCL/build/libs/HMCL-3.3.196.exe',
            f'HMCL.exe')
    else:
        download_file(r'https://download1325.mediafire.com/w26ivjyiawbg/4pttqgt3ogrp848/PCL.exe', f'PCL.exe')


##############################################################
clean_screen()
console_command("title " + Program_Name + " - 加载程序")
print("程序加载中...")
for _ in tqdm(range(1, 101)):
    sleep(0.01)
print("完成！")
sleep(0.7)
clean_screen()
console_command("title " + Program_Name)
print("欢迎使用 " + Program_Name + "\n"
                               "程序作者：" + Author_Name + "\n"
                                                       "项目地址：" + Project_Url + "\n"
                                                                               "当前版本" + Version + "\n\n"
      )
input("按下回车键以开始初始化")
clean_screen()
select_launcher()
java_confirm()
console_command('title ' + Program_Name + ' - 文件补全')
clean_screen()
java_process()
launcher_process()
console_command('title ' + Program_Name + ' - 完成')
clean_screen()
print(Program_Name + "已初始化完成！")
print("你可以删除此程序了！")
input("\n\n按下回车退出此程序")
