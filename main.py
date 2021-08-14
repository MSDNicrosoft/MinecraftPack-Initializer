# -*- coding: UTF-8 -*-
from __future__ import annotations
import os
import sys
import zipfile
from time import sleep
import gc as gc_function
import requests
from tqdm import tqdm
import multitasking
import signal
from retry import retry
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

def download_file(url, file_name):
    MB = 1024 ** 2  # 定义 1 MB 多少为 B

    def split(start: int, end: int, step: int) -> list[tuple[int, int]]:
        parts = [(start, min(start + step, end))  # 分多块
                 for start in range(0, end, step)]
        return parts

    def get_file_size(url: str) -> int:
        '''
        获取文件大小
        Parameters
        ----------
        url : 文件直链
        ------
        文件大小（B 为单位）
        '''
        global file_size_mb
        response = requests.head(url)
        file_size_b = response.headers.get('Content-Length')
        file_size_b_int = int(file_size_b)
        file_size_mb = file_size_b_int // 1048576
        return int(file_size_b_int)

    def download(url: str, file_name: str, retry_times: int = 3, each_size=16 * MB) -> None:

        '''
        根据文件直链和文件名下载文件
        Parameters
        ----------
        url : 文件直链
        file_name : 文件名
        retry_times: 可选的，每次连接失败重试次数
        Return
        ------
        :param each_size:
        '''

        f = open(file_name, 'wb')
        file_size_b_int = get_file_size(url)

        @retry(tries=retry_times)
        @multitasking.task
        def start_download(start: int, end: int) -> None:
            '''
            根据文件起止位置下载文件
            Parameters
            ----------
            start : 开始位置
            end : 结束位置
            '''
            response = session.get(url, stream=True)
            chunk_size = 128  # 每次读取的流式响应大小
            chunks = []  # 暂存已获取的响应，后续循环写入
            for chunk in response.iter_content(chunk_size=chunk_size):
                # 暂存获取的响应
                chunks.append(chunk)
                # 更新进度条
            f.seek(start)
            for chunk in chunks:
                f.write(chunk)
            # 释放已写入的资源
            del chunks

        session = requests.Session()  # 分块文件如果比文件大，就取文件大小为分块大小
        each_size = min(each_size, file_size_b_int)  # 分块
        parts = split(0, file_size_b_int, each_size)  # 创建进度条
        file_size_mb_str = str(file_size_mb)
        print("正在下载文件：" + file_name + "  大小：" + file_size_mb_str + " MB\n请稍等...")
        for part in parts:
            start, end = part
            start_download(start, end)
        # 等待全部线程结束
        multitasking.wait_for_tasks()
        f.close()

    if "__main__" == __name__:
        download(url, file_name)

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
        "HMCL", "HMCl", "HMcl", "HmCL", "HmCl", "Hmcl", "hmCL", "hmCl", "hmcl", "hMCL", "hMcl", "hMCl", "hMcL",
        "PCL2", "PCl2", "Pcl2", "PcL2", "pCL2", "pCl2", "pcL2", "pcl", "PCL", "PCl", "Pcl", "PcL", "pCL", "pCl", "pcL"]:
        if Launcher_Selection in ["HMCL", "HMCl", "HMcl", "HmCL", "HmCl", "Hmcl", "hmCL", "hmCl", "hmcl", "hMCL",
                                  "hMcl", "hMCl", "hMcL"]:
            Launcher_Selection = True
        else:
            Launcher_Selection = False


def java_confirm():
    global Java_Selection
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
        download_file(
            r'https://mirrors.tuna.tsinghua.edu.cn/AdoptOpenJDK/16/jre/x64/windows/OpenJDK16U-jre_x64_windows_hotspot_16.0.1_9.zip',
            f'OpenJDK16U-jre_x64_windows_hotspot_16.0.1_9.zip')
        sleep(0.4)
        extract_file(r'OpenJDK16U-jre_x64_windows_hotspot_16.0.1_9.zip', '.minecraft/')
        os.remove(r'OpenJDK16U-jre_x64_windows_hotspot_16.0.1_9.zip')
        os.rename(r'.minecraft/jdk-16.0.1+9-jre', r'runtime')
        os.remove(r'.minecraft/runtime/lib/src.zip')

def launcher_process():
    if Launcher_Selection:
        check_java()
        download_file(r'http://ci.huangyuhui.net/job/HMCL/lastSuccessfulBuild/artifact/HMCL/build/libs/HMCL-3.3.196.exe', f'HMCL.exe')
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

print("欢迎使用 " + Program_Name + "\n"
                               "程序作者：" + Author_Name + "\n"
                                                       "项目地址：" + Project_Url + "\n\n"
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

