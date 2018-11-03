import sys, os, re

if not sys.version_info >= (3, 6):
    sys.exit('Python 3.6 or higher is required!')

try:
    import thindf
except ImportError:
    sys.exit("Module thindf is not installed!\nPlease install it using this command:\n" + (sys.platform == 'win32')*(os.path.dirname(sys.executable) + '\\Scripts\\') + 'pip3 install thindf')

if len(sys.argv) < 2 or '-h' in sys.argv or '--help' in sys.argv:
    print('''Usage: 11l py-or-11l-source-file [-d]

Options:
  -d                    disable optimizations [makes compilation faster]''')
    sys.exit(1)

enopt = not '-d' in sys.argv

if not (sys.argv[1].endswith('.py') or sys.argv[1].endswith('.11l')):
    sys.exit("source-file should have extension '.py' or '.11l'")

def show_error(fname, fcontents, e):
    next_line_pos = fcontents.find("\n", e.pos)
    if next_line_pos == -1:
        next_line_pos = len(fcontents)
    prev_line_pos = fcontents.rfind("\n", 0, e.pos) + 1
    sys.exit('Error: ' + e.message + "\n in file '" + fname + "', line " + str(fcontents[:e.pos].count("\n") + 1) + "\n"
           + fcontents[prev_line_pos:next_line_pos] + "\n" + re.sub(r'[^\t]', ' ', fcontents[prev_line_pos:e.pos]) + '^'*max(1, e.end - e.pos))

import _11l_to_cpp.tokenizer, _11l_to_cpp.parse

if sys.argv[1].endswith('.py'):
    import python_to_11l.tokenizer, python_to_11l.parse
    py_source = open(sys.argv[1], encoding = 'utf-8-sig').read()
    try:
        _11l_code = python_to_11l.parse.parse_and_to_str(python_to_11l.tokenizer.tokenize(py_source), py_source, sys.argv[1])
    except (python_to_11l.parse.Error, python_to_11l.tokenizer.Error) as e:
        show_error(sys.argv[1], py_source, e)
    _11l_fname = os.path.splitext(sys.argv[1])[0] + '.11l'
    open(_11l_fname, 'w', encoding = 'utf-8', newline = "\n").write(_11l_code)
else:
    _11l_fname = sys.argv[1]
    _11l_code = open(sys.argv[1], encoding = 'utf-8-sig').read()

cpp_code = '#include "' + os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '_11l_to_cpp', '11l.hpp')) + "\"\n\n" # replace("\\", "\\\\") is not necessary here (because MSVC for some reason treat backslashes in include path differently than in regular string literals)
try:
    cpp_code += _11l_to_cpp.parse.parse_and_to_str(_11l_to_cpp.tokenizer.tokenize(_11l_code), _11l_code, _11l_fname, append_main = True)
except (_11l_to_cpp.parse.Error, _11l_to_cpp.tokenizer.Error) as e:
    # open(_11l_fname, 'w', encoding = 'utf-8', newline = "\n").write(_11l_code)
    show_error(_11l_fname, _11l_code, e)

cpp_fname = os.path.splitext(sys.argv[1])[0] + '.cpp'
open(cpp_fname, 'w', encoding = 'utf-8-sig', newline = "\n").write(cpp_code) # utf-8-sig is for MSVC

if sys.platform == 'win32':
    was_break = False
    for edition in ['BuildTools', 'Community', 'Enterprise', 'Professional']:
        vcvarsall = R'C:\Program Files (x86)\Microsoft Visual Studio\2017'+'\\' + edition + R'\VC\Auxiliary\Build\vcvarsall.bat'
        if os.path.isfile(vcvarsall):
            was_break = True
            break
    if not was_break:
        sys.exit('''Unable to find vcvarsall.bat!
If you do not have Visual Studio 2017 installed please install it or Build Tools for Visual Studio 2017 from here[https://visualstudio.microsoft.com/downloads/].''')

    os.system('"' + vcvarsall + '" x64 > nul && cl.exe /std:c++17 /MT /EHsc /nologo ' + '/O2 '*enopt + cpp_fname)

else:
    if os.system('g++-8 --version > /dev/null') != 0:
        sys.exit('GCC 8 is not found!')
    os.system('g++-8 -std=c++17 -Wfatal-errors -DNDEBUG ' + '-O3 '*enopt + '-march=native -o "' + os.path.splitext(sys.argv[1])[0] + '" "' + cpp_fname + '" -lstdc++fs')
