import sys, platform, os, re, subprocess, codecs

if not sys.version_info >= (3, 6):
    sys.exit('Python 3.6 or higher is required!')

try:
    import eldf
except ImportError:
    sys.exit("Module eldf is not installed!\nPlease install it using this command:\n" + (sys.platform == 'win32')*(os.path.dirname(sys.executable) + '\\Scripts\\') + 'pip3 install eldf')

if len(sys.argv) < 2 or '-h' in sys.argv or '--help' in sys.argv:
    print('''Usage: 11l py-or-11l-source-file [options]

Options:
  --python-division               use Python 3 style division
  --python-remainder              use Python style remainder
  --floor-integer-division        use Python style integer division for negative numbers (i.e. floor division)
  --python-negative-indexing      support `a[k]` for k < 0 (`a[-...]` is supported anyway)
  --public-set-copy-constructor   unprivate Set copy constructor (if there are problems with default behaviour)
  --max-compat-with-python        sets all [5] options above
  --int64                         use 64-bit integers
  -d                              disable optimizations [makes compilation faster]
  -t                              transpile only
  -e                              expand includes
  -v                              print version''')
    sys.exit(1)

if '-v' in sys.argv:
    print(open(os.path.join(os.path.dirname(sys.argv[0]), 'version.txt')).read())
    sys.exit(0)

enopt = not '-d' in sys.argv

if not sys.argv[1].endswith(('.py', '.11l', '.911')):
    sys.exit("source file should have extension '.py' or '.11l' or '.911'")

def show_error(fname, fcontents, e, syntax_error):
    next_line_pos = fcontents.find("\n", e.pos)
    if next_line_pos == -1:
        next_line_pos = len(fcontents)
    prev_line_pos = fcontents.rfind("\n", 0, e.pos) + 1
    sys.exit(('Syntax' if syntax_error else 'Lexical') + ' error: ' + e.message + "\n in file '" + fname + "', line " + str(fcontents[:e.pos].count("\n") + 1) + "\n"
           + fcontents[prev_line_pos:next_line_pos] + "\n" + re.sub(r'[^\t]', ' ', fcontents[prev_line_pos:e.pos]) + '^'*max(1, e.end - e.pos))

import _11l_to_cpp.tokenizer, _11l_to_cpp.parse

if sys.argv[1].endswith('.py'):
    import python_to_11l.tokenizer, python_to_11l.parse
    py_source = open(sys.argv[1], encoding = 'utf-8-sig').read()
    try:
        _11l_code = python_to_11l.parse.parse_and_to_str(python_to_11l.tokenizer.tokenize(py_source), py_source, sys.argv[1])
    except (python_to_11l.parse.Error, python_to_11l.tokenizer.Error) as e:
        (fname, fcontents) = (sys.argv[1], py_source)
        if type(e) == python_to_11l.parse.Error and python_to_11l.parse.file_name != '':
            (fname, fcontents) = (python_to_11l.parse.file_name, python_to_11l.parse.source)
        show_error(fname, fcontents, e, type(e) == python_to_11l.parse.Error)
    _11l_fname = os.path.splitext(sys.argv[1])[0] + '.11l'
    open(_11l_fname, 'w', encoding = 'utf-8', newline = "\n").write(_11l_code)
else:
    _11l_fname = sys.argv[1]
    _11l_code = open(sys.argv[1], encoding = 'utf-8-sig').read()
    if _11l_fname.endswith('.911'):
        _11l_code = ": = 9:\n\n" + _11l_code
        _11l_fname += '.11l'
        open(_11l_fname, 'w', encoding = 'utf-8', newline = "\n").write(_11l_code)

cpp_code = ''
if '--int64' in sys.argv:
    cpp_code += "#define INT_IS_INT64\n"
    _11l_to_cpp.parse.int_is_int64 = True
if '--python-division' in sys.argv or '--max-compat-with-python' in sys.argv:
    _11l_to_cpp.parse.python_division = True
if '--python-remainder' in sys.argv or '--max-compat-with-python' in sys.argv:
    cpp_code += "#define PYTHON_REMAINDER\n"
if '--floor-integer-division' in sys.argv or '--max-compat-with-python' in sys.argv:
    cpp_code += "#define FLOOR_INTEGER_DIVISION\n"
if '--python-negative-indexing' in sys.argv or '--max-compat-with-python' in sys.argv:
    cpp_code += "#define PYTHON_NEGATIVE_INDEXING\n"
if '--public-set-copy-constructor' in sys.argv or '--max-compat-with-python' in sys.argv:
    cpp_code += "#define PUBLIC_SET_COPY_CONSTRUCTOR\n"
cpp_code_inc = '#include "' + os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '_11l_to_cpp', '11l.hpp')) + "\"\n\n" # replace("\\", "\\\\") is not necessary here (because MSVC for some reason treat backslashes in include path differently than in regular string literals)
used_builtin_modules = set()
try:
    tokens = _11l_to_cpp.tokenizer.tokenize(_11l_code)
    if _11l_to_cpp.tokenizer.needs_source_code_correction(tokens, _11l_code):
        if sys.argv[1].endswith('.py'):
            sys.exit('python_to_11l output needs source code correction!')
        has_bom = open(sys.argv[1], 'rb').read(3) == codecs.BOM_UTF8 # [https://stackoverflow.com/questions/13590749/reading-unicode-file-data-with-bom-chars-in-python <- google:‘python detect utf8 sig’]
        _11l_code = _11l_to_cpp.tokenizer.correct_source_code(tokens, _11l_code)
        open(_11l_fname, 'w', encoding = 'utf-8' + '-sig'*has_bom, newline = "\n").write(_11l_code)
        tokens = _11l_to_cpp.tokenizer.tokenize(_11l_code)
        assert not _11l_to_cpp.tokenizer.needs_source_code_correction(tokens, _11l_code)

    cpp_code_body = _11l_to_cpp.parse.parse_and_to_str(tokens, _11l_code, _11l_fname, append_main = True, used_builtin_modules = used_builtin_modules)

except (_11l_to_cpp.parse.Error, _11l_to_cpp.tokenizer.Error) as e:
    # open(_11l_fname, 'w', encoding = 'utf-8', newline = "\n").write(_11l_code)
    (fname, fcontents) = (_11l_fname, _11l_code)
    if type(e) == _11l_to_cpp.parse.Error and _11l_to_cpp.parse.file_name != '':
        (fname, fcontents) = (_11l_to_cpp.parse.file_name, _11l_to_cpp.parse.source)
    show_error(fname, fcontents, e, type(e) == _11l_to_cpp.parse.Error)

if len(used_builtin_modules):
    if 're' in used_builtin_modules: cpp_code += "#define INCLUDE_RE\n"
    if 'fs' in used_builtin_modules: cpp_code += "#define INCLUDE_FS\n"
    if 'csv' in used_builtin_modules: cpp_code += "#define INCLUDE_CSV\n"
    if 'eldf' in used_builtin_modules or 'json' in used_builtin_modules: cpp_code += "#define INCLUDE_LDF\n"
cpp_code += cpp_code_inc
cpp_code += cpp_code_body

if '-e' in sys.argv:
    included = set()

    def process_include_directives(src_code, dir = ''):
        exp_code = ''
        writepos = 0
        while True:
            i = src_code.find('#include "', writepos)
            if i == -1:
                break

            exp_code += src_code[writepos:i]
            if src_code[i-2:i] == '//': # skip commented includes
                exp_code += '#'
                writepos = i + 1
                continue

            fname_start = i + len('#include "')
            fname_end = src_code.find('"', fname_start)
            assert(src_code[fname_end + 1] == "\n") # [-TODO: Add support of comments after #include directives-]

            fname = src_code[fname_start:fname_end]
            if fname[1:3] == ':\\' or fname.startswith('/'): # this is an absolute pathname
                pass
            else: # this is a relative pathname
                assert(dir != '')
                fname = os.path.join(dir, fname)

            if fname not in included:
                included.add(fname)
                exp_code += process_include_directives(open(fname, encoding = 'utf-8-sig').read(), os.path.dirname(fname))

            writepos = fname_end + 1
        exp_code += src_code[writepos:]
        return exp_code

    cpp_code = process_include_directives(cpp_code)

cpp_fname = os.path.splitext(sys.argv[1])[0] + '.cpp'
open(cpp_fname, 'w', encoding = 'utf-8-sig', newline = "\n").write(cpp_code) # utf-8-sig is for MSVC

if '-t' in sys.argv or \
   '-e' in sys.argv:
    sys.exit()

if sys.platform == 'win32':
    was_break = False
    for version in ['2022', '2019', '2017']:
        for edition in ['BuildTools', 'Community', 'Enterprise', 'Professional']:
            vcvarsall = 'C:\\Program Files' + ' (x86)'*platform.machine().endswith('64') + '\\Microsoft Visual Studio\\' + version + '\\' + edition + R'\VC\Auxiliary\Build\vcvarsall.bat'
            if os.path.isfile(vcvarsall):
                was_break = True
                #print('Using ' + version + '\\' + edition)
                break # ^L.break
        if was_break:
            break
    if not was_break:
        sys.exit('''Unable to find vcvarsall.bat!
If you do not have Visual Studio 2017, 2019 or 2022 installed please install it or Build Tools for Visual Studio from here[https://visualstudio.microsoft.com/downloads/].''')

    sys.exit(os.system('"' + vcvarsall + '" ' + ('x64' if platform.machine().endswith('64') else 'x86') + ' > nul && cl.exe /std:c++17 /MT /EHsc /nologo /W3 /we4239 ' + '/O2 '*enopt + cpp_fname))

else:
    if int(subprocess.check_output(['g++', '-dumpversion'], encoding = 'utf-8').split('.')[0]) >= 9:
        gpp = 'g++'
    else:
        for n in range(9, 100):
            gpp = 'g++-' + str(n)
            if os.system(gpp + ' --version > /dev/null 2>&1') == 0:
                break
        else:
            sys.exit('At least GCC 9 is required!')

    sys.exit(os.system(gpp + ' -std=c++17 -Wfatal-errors -DNDEBUG ' + '-O3 '*enopt + '-march=native -o "' + os.path.splitext(sys.argv[1])[0] + '" "' + cpp_fname + '" -lstdc++fs'))
