from ctypes.wintypes import HKEY
import time
from winreg import HKEY_LOCAL_MACHINE, ConnectRegistry
import win32api
import win32process
import win32pdh
import sys
import os
from winreg import *
from datetime import datetime
from ctypes import *
import ctypes


class Evasion:
    def __init__(self):
        return None
        
    def check_all_DLL_names(self):
        SandboxEvidence = []
        sandboxDLLs = ["sbiedll.dll","dbghelp.dll","api_log.dll","dir_watch.dll","pstorec.dll","vmcheck.dll","wpespy.dll"]
        allPids = win32process.EnumeProcesses()
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
            return True
        else:
            return False
    def check_all_processes_names(self):
        EvidenceOfSandbox =[]
        sandboxProcesses = "vmsrvc", "tcpview", "wireshark", "visual basic", "fiddler", "vmware", "vbox", "process explorer", "autoit", "vboxtray", "vmtools", "vmrawdsk", "vmusbmouse", "vmvss", "vmscsi", "vmxnet", "vmx_svga", "vmmemctl", "df5serv", "vboxservice", "vmhgfs"
        _, runningProcesses = win32pdh.EnumObjectItems(None,None,'process', win32pdh.PERF_DETAIL_WIZARD)

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

    def debugging_detection(self):
        isDebuggerPresent = windll.kernel32.IsDebuggerPresent

        if (isDebuggerPresent):
            return False
        else:
            return True

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

    def usb(self):
        MinimumUSBHistory = 2

        if len(sys.argv) == 2:
            MinimumUSBHistory = int(sys.argv[1])

        HKLM = ConnectRegistry(None,HKEY_LOCAL_MACHINE)
        Opened_HKLM_Key = OpenKey(HKLM, r'SYSTEM\ControlSet001\Enum\USBSTOR')

        if QueryInfoKey(Opened_HKLM_Key)[0] >= MinimumUSBHistory:
            return True
        else:
            return False
    
    def main(self):  
        if self.usb():
            return False
        elif self.disk_size():
            return False
        elif self.debugging_detection():
            return False
        elif self.check_all_processes_names():
            return False
        elif self.check_all_DLL_names():
            return False
        else:
            return True

def test():
    evasion = Evasion()
    if evasion.main() == False:
        print("no sandbox")
        return True
    elif evasion.main() == True:
        return False
    else:
        return False