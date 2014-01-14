import sys
from cx_Freeze import setup, Executable
build_exe_options = { "includes": ["PyQt4.QtWebKit"]}
base = "Win32GUI"
setup(
    name = "CopyFiles",  
    version = "1",  
    description = "I wish programming was this easy",  
    executables = [Executable("NKULogin.pyw",base = base,compress = True)])
