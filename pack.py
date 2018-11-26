import os, sys

for envvar in ['ProgramFiles', 'ProgramFiles(x86)', 'ProgramW6432']:
    os.environ["PATH"] += os.pathsep + os.getenv(envvar, '') + r'\7-Zip'

if os.system('7z a -mx9 -- 11l.tar 11l 11l.cmd 11l.py LICENSE.txt python_to_11l/*.py python_to_11l/tests/* _11l_to_cpp/*.py _11l_to_cpp/tests/* _11l_to_cpp/11l.hpp _11l_to_cpp/11l_hpp/*') != 0:
    sys.exit('7z failed')

if os.system('7z a -sdel -mx9 -- 11l.tar.xz 11l.tar') != 0:
    sys.exit('7z failed')
