#!/usr/bin/env python
# coding=utf-8

import click
import tempfile
import os
import os.path
import shutil
import subprocess

from termcolor import colored


@click.group()
def cli():
    """ Test salt states on local docker environment """
    pass


@cli.command(help="Retrieve the SSH public key used by the test Salt Master to access external formula through gitfs")
def publickey():
    subprocess.call("docker run -i -t julozi/wheezy-salt-base cat /etc/ssh/salt_rsa.pub", shell=True)


@cli.command(help="Test salt states on a local docker environment")
@click.option('--formula_dir',
              type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=False, readable=True, resolve_path=True),
              help='Path to the directory containing your salt formulas',
              prompt='Path to the directory containing your salt formula')
@click.option('--pillar_file',
              type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True, resolve_path=True),
              help='Path to a pillar sls file')
@click.option('--gitfs_formula',
              multiple=True,
              help='List of git repository to include on the test salt-master fileserver_backend configuration (separated by a semicolon)')
@click.option('--boot2docker', is_flag=True, help='Docker is running with boot2docker')
@click.argument('states', nargs=-1)
def test(formula_dir, pillar_file, gitfs_formula, boot2docker, states):
    salinity_path = os.path.dirname(os.path.abspath(__file__))

    # create temp dir
    # if using boot2docker only path located inside the user homedir can be mounted in a container
    # we also need to make sure to create the salinity temp_dir inside the user homedir
    # we need to check that the formulas_dir is also located inside the user homedir
    if boot2docker:
        user_home_dir = os.path.expanduser('~')

        if not formula_dir.startswith(user_home_dir):
            print(colored('When using boot2docker to run your docker containers, you need to locate the directory containing your salt formula repositories somewhere inside your home directory (%s)' % user_home_dir))
            exit(1)

        salinity_user_dir = os.path.join(user_home_dir, '.salinity')
        if not os.path.exists(salinity_user_dir):
            os.mkdir(salinity_user_dir)
        temp_dir_path = tempfile.mkdtemp(dir=salinity_user_dir)
    else:
        temp_dir_path = tempfile.mkdtemp(prefix='salinity')
    print(colored('Created temp dir for salinity data at %s' % temp_dir_path, 'green'))

    if pillar_file:
        shutil.copyfile(pillar_file, os.path.join(temp_dir_path, u'salinity.sls'))

    if gitfs_formula:
        salt_extra_config = open(os.path.join(temp_dir_path, u'extra_config'), 'w')
        salt_extra_config.write("fileserver_backend:\n  - roots\n  - git\n")
        salt_extra_config.write("gitfs_provider: pygit2\n")
        salt_extra_config.write("gitfs_remotes:\n")
        for formula in gitfs_formula:
            salt_extra_config.write("  - %s\n" % formula)
        salt_extra_config.write("gitfs_pubkey: /etc/ssh/salt_rsa.pub\n")
        salt_extra_config.write("gitfs_privkey: /etc/ssh/salt_rsa\n")
        salt_extra_config.close()

    # install container preparation script
    shutil.copyfile(os.path.join(salinity_path, 'prepare_tests.py'), os.path.join(temp_dir_path, u'prepare_tests.py'))

    # launch docker run
    print(colored('Launching tests of %s on docker' % u','.join(states), 'green'))
    command = "docker run -i -v %s:/salinity -v %s:/formula -t julozi/wheezy-salt-base sh -c 'python /salinity/prepare_tests.py %s && salt-call state.highstate && bash'" % (temp_dir_path, formula_dir, u' '.join(states))
    # command = "docker run -i -v %s:/salinity -v %s:/formula -t julozi/wheezy-salt-base sh -c 'bash'" % (temp_dir_path, formula_dir)
    print(colored('Command line : %s' % command, 'yellow'))
    subprocess.call(command, shell=True)

    shutil.rmtree(temp_dir_path)
    print(colored('Salinity temp dir deleted successfully', 'green'))


def main():
    cli()
