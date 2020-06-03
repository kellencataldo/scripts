""" This file should be .ycm_extra_conf.py at top of a c/c++ dir.
    It is based on  ~/.vim/bundle/YouCompleteMe/cpp/ycm/.ycm_extra_conf.py
    Basically just put compilation flags/include dirs in flags.
"""

import os
import ycm_core

# These are the compilation flags that will be used by YCM to check c files.
FLAGS = [
    # C Flags
    '-ggdb',
    '-Wall',
    '-Wextra',
    #'-Werror',
    '-Winline',
    '-pedantic',
    '-fexceptions',
    # C++ Flags
    #'-Weffc++',
    # Defines
    '-D_REENTRANT',
    # Important for clang, choose a standard below.
    # C++: c/gnu++98, c++03, c/gnu++11,
    # C: c/gnu90, c/gnu99, c/gnu11
    '-std=c99',
    # Need to tell clang language of headers.
    # For a C project set to 'c' instead of 'c++'.
    '-x',
    'c',
    # Includes.
    '-isystem',
    '/usr/include',
    '-isystem',
    '/usr/local/include',
    '-I',
    './libs/include',
    '-I',
    './src',
]


# Set this to the absolute path to the folder (NOT the file!) containing the
# compile_commands.json file to use that instead of 'flags'. See here for
# more details: http://clang.llvm.org/docs/JSONCompilationDatabase.html
#
# Most projects will NOT need to set this to anything; you can just change the
# 'flags' list of compilation flags. Notice that YCM itself uses that approach.
COMPILATION_DB_FOLDER = ''

if os.path.exists(COMPILATION_DB_FOLDER):
    DB = ycm_core.CompilationDB(COMPILATION_DB_FOLDER)
else:
    DB = None

# Extensions that will be looked for.
SOURCE_EXTENSIONS = ['.c', '.cpp', '.cxx', '.cc', '.m', '.mm']
HEADER_EXTENSIONS = ['.h', '.hpp', '.hxx', '.hh']


def MakeRelativePathsInFlagsAbsolute(flags, working_directory):
    """ Processes paths in FLAGS var and makes them absolute. """
    if not working_directory:
        return list(flags)
    new_flags = []
    make_next_absolute = False
    path_flags = ['-isystem', '-I', '-iquote', '--sysroot=']
    for flag in flags:
        new_flag = flag

        if make_next_absolute:
            make_next_absolute = False
            if not flag.startswith('/'):
                new_flag = os.path.join(working_directory, flag)

        for path_flag in path_flags:
            if flag == path_flag:
                make_next_absolute = True
                break

            if flag.startswith(path_flag):
                path = flag[len(path_flag):]
                new_flag = path_flag + os.path.join(working_directory, path)
                break

        if new_flag:
            new_flags.append(new_flag)
    return new_flags


def IsHeaderFile(filename):
    """ Return true only if filename ends in a header extension. """
    extension = os.path.splitext(filename)[1]
    return extension in HEADER_EXTENSIONS


def GetCompilationInfoForFile(filename):
    """ The compilation_commands.json file generated by CMake does not have
        entries for header files. So we do our best by asking the db for
        flags for a corresponding source file, if any. If one exists, the
        flags for that file should be good enough.
    """
    if IsHeaderFile(filename):
        basename = os.path.splitext(filename)[0]
        for extension in SOURCE_EXTENSIONS:
            replacement_file = basename + extension
            if os.path.exists(replacement_file):
                compilation_info = DB.GetCompilationInfoForFile(
                    replacement_file)
                if compilation_info.compiler_flags_:
                    return compilation_info
        return None
    return DB.GetCompilationInfoForFile(filename)


def FlagsForFile(filename, **kwargs):
    """ Given a filename, return the flags to compile it. """
    if DB:
        # Bear in mind that compilation_info.compiler_flags_ does NOT return a
        # python list, but a "list-like" StringVec object
        compilation_info = GetCompilationInfoForFile(filename)
        if not compilation_info:
            return None

        final_flags = MakeRelativePathsInFlagsAbsolute(
            compilation_info.compiler_flags_,
            compilation_info.compiler_working_dir_)

    else:
        relative_to = os.path.dirname(os.path.abspath(__file__))
        final_flags = MakeRelativePathsInFlagsAbsolute(FLAGS, relative_to)

    return {'flags': final_flags,
            'do_cache': True
            }
