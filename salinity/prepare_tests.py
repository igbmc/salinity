#!/usr/bin/env python
# coding=utf-8

import os
import shutil
import stat
import sys
import subprocess


def main():
    top_file = file('/srv/salt/top.sls', 'w')
    top_file.write("base:\n  'minion':\n")
    for state in sys.argv[1:]:
        top_file.write("    - %s\n" % state)
    top_file.close()

    for formula in os.listdir('/formula'):
        formula_path = os.path.join('/formula', formula)
        if os.path.isdir(formula_path) and os.path.exists(os.path.join(formula_path, 'init.sls')):
            os.symlink(formula_path, os.path.join('/srv/salt', formula))

    if os.path.exists('/salinity/salinity.sls'):
        print "Creating pillar file"
        # create top.sls pillar file
        top_file = file(u'/srv/pillar/top.sls', 'w')
        top_file.write("base:\n  'minion':\n    - salinity\n")
        top_file.close()
        # copy pillar file to pillar data dir under default name salinity.sls
        shutil.copyfile('/salinity/salinity.sls', u'/srv/pillar/salinity.sls')

    if os.path.exists('/salinity/user_rsa'):
        shutil.copyfile('/salinity/user_rsa', u'/etc/ssh/user_rsa')
        os.chmod('/etc/ssh/user_rsa', stat.S_IREAD | stat.S_IWRITE)

    if os.path.exists('/salinity/user_rsa.pub'):
        shutil.copyfile('/salinity/user_rsa.pub', u'/etc/ssh/user_rsa.pub')

    if os.path.exists('/salinity/extra_config'):
        shutil.copyfile('/salinity/extra_config', u'/etc/salt/extra_config')

    print "Starting salt-master"
    subprocess.call(" service salt-master start", shell=True)

    print "Starting salt-minion"
    subprocess.call("service salt-minion start", shell=True)


if __name__ == '__main__':
    main()
