from __future__ import print_function
import sys
import os
import pathlib

from catkin_tools.argument_parsing import add_context_args
from catkin_tools.metadata import find_enclosing_workspace
from catkin_tools.context import Context
from catkin_pkg.packages import find_packages
from subprocess import Popen

def runClangTidy(clang_binary, pkg_root, package, filenames, cfg, compile_db, fix = False, export_file=None, dry_run = False):
    cmd = [clang_binary]
    # Matches headers in current package but excludes autogenerated StuffConfig.h
    # cmd += ['-header-filter={}/.*(?<!Config).h'.format(package)]
    cmd += ['-header-filter={}/include'.format(package)]
    cmd += ['-p={}'.format(compile_db)]
    #cmd += ['-config={}'.format(cfg)]
    if fix:
        cmd += ['--fix']
        cmd += ['--fix-errors']
        cmd += ['-extra-arg=-std=c++11']
        cmd += ['-warnings-as-errors=*']
        cmd += ['-enable-check-profile']
        cmd += ['-format-style=file']
    if export_file:
        cmd += ['--export-fixes={}'.format(export_file)]
    cmd += filenames
    if dry_run:
        print(" ".join(cmd))
    else:
        print("Command '{}'".format(cmd))
        print("Package path '{}'".format(pkg_root))
        s = Popen(cmd, cwd=pkg_root)
        s.wait()

def prepare_arguments(parser):
    add_context_args(parser)
    clang_binary = parser.add_argument
    clang_binary('-c', '--clang-tidy', nargs="?", default="clang-tidy-13", help="Name of clang-tidy binary, e.g. 'clang-tidy-9'")
    fix = parser.add_argument
    fix('-f', '--fix', action='store_true', default=True, help="Apply fixes")
    export = parser.add_argument
    export('-e', '--export', nargs=1, help="Export fixes to file (unsets -f)")
    pkg = parser.add_argument
    pkg('package', help="Package to run for")
    src = parser.add_argument
    src('src_file', nargs='*', help="Source files to run for")
    return parser

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
    #print(opts)

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
        opts.src_file = findCodeFiles(pkg_root)

    if not opts.src_file:
        print("No .cpp files found!")
        sys.exit(4)

    export_file = None if opts.export is None else opts.export[0]
    if export_file:
        opts.fix = False

    runClangTidy(clang_binary=opts.clang_tidy, pkg_root=pkg_root, package=opts.package, filenames=opts.src_file, cfg=None, compile_db=build_space, fix=opts.fix, export_file=export_file, dry_run = False)
    return 0

description = dict(
        verb='tidy',
        description='Runs clang-tidy on a file. Make sure you have enabled generation of compile_commands.json.',
        main=main,
        prepare_arguments=prepare_arguments,
        )
