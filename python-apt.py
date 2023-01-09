#!/usr/bin/env python3
import apt
import json
import os
import re
import sys


def usage():
    print('Usage: %s [OPTION...]' % os.path.basename(sys.argv[0]))
    print()
    print('Prints all installed packages and their repositories (best guess).')
    print()
    print('This software will provide a JSON object. The property values are lists of')
    print('installed packages (all packages, unless filtered), and the property names')
    print('are the most likely origin candidates (formatted similar to sources.list)')
    print('of the respective package list. "Most likely" is the repository from which')
    print('the installed package in its installed version would be installed from.')
    print()
    print('OPTIONs:')
    print('  --help, -h                Show this help and quit.')
    print('  --list-repositories, -l   List only the repositories, do not list the')
    print('                            packages. Will return a JSON list.')
    print('  --list-packages, -L       List only the packages, do not list their')
    print('                            repositories. Will return a JSON list.')
    print('  --regex-repository, -r    Regular expression to filter the repository by')
    print('                            (matches mirror, component and/or archive).')
    print('  --regex-mirror, -m        Regular expression to filter the repositories')
    print('                            by their mirror.')
    print('  --regex-component, -c     Regular expression to filter the repositories')
    print('                            by their component.')
    print('  --regex-archive, -a       Regular expression to filter the repositories')
    print('                            by their archive.')
    print('  --regex-package, -p       Regular expression to filter packages by its')
    print('                            name.')
    print()
    print('Explanation:')
    print('  Assuming your sources.list has the following entry:')
    print('    deb http://de.archive.ubuntu.com/ubuntu/ jammy-backports main restricted universe')
    print('  Then the terms used can be explained thusly:')
    print('  - mirror: the FQDN of the mirror server, e.g. "de.archive.ubuntu.com"')
    print('  - archive: the repository, e.g. "jammy-backports"')
    print('  - component: the component, e.g. "main", "restricted" or "universe"')
    print()
    print('Additional information:')
    print('  https://help.ubuntu.com/community/Repositories')


regex_repository = []
regex_mirror = []
regex_component = []
regex_archive = []
regex_package = []
list_repositories_only = False

idx = 1
while idx < len(sys.argv):
    arg = sys.argv[idx]
    if arg in ['--help', '-h']:
        usage()
        sys.exit(0)
    elif arg in ['--list-repositories', '-l']:
        list_repositories_only = True
    elif arg in ['--regex-repository', '-r']:
        if len(sys.argv) < idx + 1:
            print('Lacking argument for option!')
            sys.exit(2)
        idx += 1
        regex_repository += [sys.argv[idx]]
    elif arg in ['--regex-mirror', '-m']:
        if len(sys.argv) < idx + 1:
            print('Lacking argument for option!')
            sys.exit(2)
        idx += 1
        regex_mirror += [sys.argv[idx]]
    elif arg in ['--regex-component', '-c']:
        if len(sys.argv) < idx + 1:
            print('Lacking argument for option!')
            sys.exit(2)
        idx += 1
        regex_component += [sys.argv[idx]]
    elif arg in ['--regex-archive', '-a']:
        if len(sys.argv) < idx + 1:
            print('Lacking argument for option!')
            sys.exit(2)
        idx += 1
        regex_archive += [sys.argv[idx]]
    elif arg in ['--regex-package', '-p']:
        if len(sys.argv) < idx + 1:
            print('Lacking argument for option!')
            sys.exit(2)
        idx += 1
        regex_package += [sys.argv[idx]]
    else:
        print('Bad argument: ' + arg)
        sys.exit(255)
    idx += 1

cache = apt.Cache()
pkg_list = {}

for package in cache:
    if len(regex_package) > 0:
        skip = True
        for regex in regex_package:
            if re.search(regex, package.name) is not None:
                skip = False
        if skip:
            continue

    if package.installed:
        origin_candidate = package.candidate.origins[0]
        origin_name = "%s %s %s" % (origin_candidate.site, origin_candidate.archive, origin_candidate.component)

        matched = False
        if not matched or len(regex_repository) > 0:
            for regex in regex_repository:
                if re.search(regex, origin_name) is not None:
                    matched = True
        if not matched or len(regex_mirror) > 0:
            for regex in regex_mirror:
                if re.search(regex, origin_candidate.site) is not None:
                    matched = True
        if not matched or len(regex_component) > 0:
            for regex in regex_component:
                if re.search(regex, origin_candidate.component) is not None:
                    matched = True
        if not matched or len(regex_archive) > 0:
            for regex in regex_archive:
                if re.search(regex, origin_candidate.archive) is not None:
                    matched = True
        if not matched and len(regex_repository) + len(regex_mirror) + len(regex_component) + len(regex_archive) > 0:
            continue

        if origin_name not in pkg_list:
            pkg_list[origin_name] = []
        pkg_list[origin_name] += [package.name]

if list_repositories_only:
    print(json.dumps(list(pkg_list.keys())))
else:
    print(json.dumps(pkg_list))
