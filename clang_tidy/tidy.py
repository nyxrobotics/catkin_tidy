from __future__ import print_function
import sys
import os
import pathlib

from catkin_tools.argument_parsing import add_context_args
from catkin_tools.metadata import find_enclosing_workspace
from catkin_tools.context import Context
from catkin_pkg.packages import find_packages
from subprocess import Popen
from subprocess import PIPE

def runClangTidy(clang_binary, pkg_root, package, headers, sources, cfg, compile_db, fix = False, export_file=None, dry_run = False):
    cmd = [clang_binary]
    cmd += ['-p={}'.format(compile_db)]
    cmd += ['-header-filter={}/.*'.format(pkg_root)]
    if fix:
        cmd += ['-enable-check-profile']
        cmd += ['-extra-arg=-std=c++11']
        cmd += ['-fix']
        cmd += ['-fix-errors']
        cmd += ['-format-style=file']
        cmd += ['-warnings-as-errors=*']
    if export_file:
        cmd += ['-export-fixes={}'.format(export_file)]
    cmd += sources
    cmd += headers
    if dry_run:
        print(" ".join(cmd))
    else:
        print("Command '{}'".format(cmd))
        print("Package path '{}'".format(pkg_root))
        s = Popen(cmd, cwd=pkg_root)
        s.wait()

def prepare_arguments(parser):
    add_context_args(parser)
    default_clang_tidy = "clang-tidy-" + getInstalledClangVersion()
    clang_binary = parser.add_argument
    clang_binary('-c', '--clang-tidy', nargs="?", default=default_clang_tidy , help="Name of clang-tidy binary, e.g. 'clang-tidy-9'")
    fix = parser.add_argument
    fix('-f', '--fix', action='store_true', default=False, help="Apply fixes")
    export = parser.add_argument
    export('-e', '--export', nargs=1, help="Export fixes to file (unsets -f)")
    pkg = parser.add_argument
    pkg('package', help="Package to run for")
    src = parser.add_argument
    src('src_file', nargs='*', help="Source files to run for")
    return parser

# List versions without minor numbers in order of newest to oldest
def getInstalledClangVersion():
    cmd = ['ls -vr /usr/lib/clang --ignore="*.*"']
    # print("Command:{}".format(cmd))
    s = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    s.wait()
    std_out, std_err = s.communicate()
    version_list = std_out.decode('utf-8').rstrip().split('\n')
    if len(version_list)==0:
        print("ERROR:No clang compiler found")
    return version_list[0]

def findSrcFiles(path):
    p = pathlib.Path(path)
    types = ('src/**/*.c', 'src/**/*.cpp')
    files_grabbed = []
    for files in types:
        files_grabbed.extend(p.glob(files))
    return map(lambda a : a.as_posix(), files_grabbed)

def findHeaderFiles(path):
    p = pathlib.Path(path)
    types = ('include/**/*.h', 'include/**/*.hpp')
    files_grabbed = []
    for files in types:
        files_grabbed.extend(p.glob(files))
    return map(lambda a : a.as_posix(), files_grabbed)

def findCodeFiles(path):
    p = pathlib.Path(path)
    types = ('src/**/*.c', 'src/**/*.cpp', 'include/**/*.h', 'include/**/*.hpp')
    files_grabbed = []
    for files in types:
        files_grabbed.extend(p.glob(files))
    return map(lambda a : a.as_posix(), files_grabbed)

def main(opts):
    opts = sys.argv[1:] if opts is None else opts
    # print(opts)

    workspace = os.getcwd() if opts.workspace is None else opts.workspace
    workspace = find_enclosing_workspace(workspace)

    if not workspace:
        print("No workspace found")
        sys.exit(1)

    ctx = Context.load(workspace, opts.profile, opts, load_env=False)
    packages = find_packages(ctx.source_space_abs)
    pkg_path = [pkg_path for pkg_path, p in packages.items() if p.name == opts.package]
    pkg_path = None if not pkg_path else pkg_path[0]
    if not pkg_path:
        print("Package '{}' not found!".format(opts.package))
        sys.exit(2)

    pkg_name = packages[pkg_path].name
    build_space = ctx.build_space_abs + os.path.sep + pkg_name
    compile_db = build_space + os.path.sep + "compile_commands.json"
    if not os.path.isfile(compile_db):
        print("No compile_commands.json in {}".format(build_space))
        sys.exit(3)

    pkg_root = ctx.source_space_abs + os.path.sep + pkg_path

    if not opts.src_file:
        opts.src_file = findSrcFiles(pkg_root)

    if not opts.src_file:
        print("No .cpp files found!")
        sys.exit(4)

    export_file = None if opts.export is None else opts.export[0]
    if export_file:
        opts.fix = False

    inc_file = findHeaderFiles(pkg_root)
    runClangTidy(clang_binary=opts.clang_tidy, pkg_root=pkg_root, package=opts.package, headers=inc_file, sources=opts.src_file, cfg=None, compile_db=build_space, fix=opts.fix, export_file=export_file, dry_run = False)
    return 0

description = dict(
        verb='clang_tidy',
        description='Runs clang-tidy on a file. Make sure you have enabled generation of compile_commands.json.',
        main=main,
        prepare_arguments=prepare_arguments,
        )
