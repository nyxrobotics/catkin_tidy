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

def prepare_arguments(parser):
    add_context_args(parser)
    pkg = parser.add_argument
    pkg('package', help="Package to run for")
    return parser

def runClangBuild(pkg_name, clang_version):
    # 'catkin build <packagename> -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DCMAKE_C_COMPILER=/usr/bin/clang-13 -DCMAKE_CXX_COMPILER=/usr/bin/clang++-13'
    cmd = ['catkin build {}'.format(pkg_name)]
    cmd += ['-DCMAKE_EXPORT_COMPILE_COMMANDS=ON']
    cmd += ['-DCMAKE_C_COMPILER=/usr/bin/clang-{}'.format(clang_version)]
    cmd += ['-DCMAKE_CXX_COMPILER=/usr/bin/clang++-{}'.format(clang_version)]
    print("Command '{}'".format(" ".join(cmd)))
    s = Popen(" ".join(cmd), shell=True)
    s.wait()

def getInstalledClangVersion():
    # List versions without minor numbers in order of newest to oldest
    cmd = ['ls -vr /usr/lib/clang --ignore="*.*"']
    print("Command:{}".format(" ".join(cmd)))
    s = Popen(" ".join(cmd), shell=True, stdout=PIPE, stderr=PIPE)
    s.wait()
    std_out, std_err = s.communicate()
    version_list = std_out.decode('utf-8').rstrip().split('\n')
    if len(version_list)==0:
        print("ERROR:No clang compiler found")
    return version_list[0]

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
    pkg_root = ctx.source_space_abs + os.path.sep + pkg_path
    print("PKG_ROOT:'{}'".format(pkg_root))
    runClangBuild(pkg_name=pkg_name,clang_version=getInstalledClangVersion())
    return 0

description = dict(
        verb='clang_build',
        description='Build ROS package with clang compiler',
        main=main,
        prepare_arguments=prepare_arguments,
        )
