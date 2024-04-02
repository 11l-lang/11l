import os, sys, datetime

for envvar in ['ProgramFiles', 'ProgramFiles(x86)', 'ProgramW6432']:
    os.environ["PATH"] += os.pathsep + os.getenv(envvar, '') + r'\7-Zip'

with open('version.txt', 'w') as f:
    today = datetime.date.today()
    f.write(str(today.year) + '.' + str(today.month))

for root, dirs, files in os.walk('_11l_to_cpp/tests'):
    dirs[:] = [d for d in dirs if d[0] != '.'] # exclude hidden folders (e.g. `.git`)
    for name in files:
        if not '.' in name and not 'testdata' in root:
            os.remove(os.path.join(root, name))
            print("Removed '" + os.path.join(root, name) + "'")

os.system(r'copy ..\eldf\eldf.py .')
os.system(r'copy ..\eldf\eldf.py python_to_11l')
os.system(r'copy ..\eldf\eldf.py _11l_to_cpp')

if os.system('7z a -mx9 -xr!__pycache__ -xr!.mypy_cache -xr!.vs -xr!.git -xr!build -xr!*.exe -xr!*.obj -xr!*.out -xr!*.html -xr!*.pyd -xr!*.pyx -xr!*.pyproj -xr!*.sln -- 11l.tar 11l 11l.cmd 11l.py eldf.py LICENSE.txt version.txt python_to_11l/*.py python_to_11l/tests/* _11l_to_cpp/*.py _11l_to_cpp/tests/* _11l_to_cpp/11l.hpp _11l_to_cpp/11l_hpp/*') != 0:
    sys.exit('7z failed')

if os.system('7z a -sdel -mx9 -- 11l.tar.xz 11l.tar') != 0:
    sys.exit('7z failed')
