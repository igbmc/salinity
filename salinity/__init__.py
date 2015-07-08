#!/usr/bin/env python
# coding=utf-8

import click
import json
import os
import os.path
import shutil
import subprocess
import tempfile
import yaml

from termcolor import colored

be_verbose = False


@click.group()
@click.option('--verbose', is_flag=True, default=False, help='tell salinity to be more verbose')
def cli(verbose):
    """ Test salt states on local docker environment """
    be_verbose = verbose


@cli.command(help="Test salt states on a local docker environment")  # NOQA
@click.option('--formula_dir',
              type=click.Path(exists=True, file_okay=False, dir_okay=True,
                              writable=False, readable=True, resolve_path=True),
              help='Path to the directory containing your salt formulas',
              default='.')
@click.option('--pillar_file',
              type=click.Path(exists=True, file_okay=True, dir_okay=False,
                              writable=False, readable=True, resolve_path=True),
              help='Path to a pillar sls file')
@click.option('--gitfs_formula',
              multiple=True,
              help='List of git repository to include on the test salt-master \
                    fileserver_backend configuration (separated by a semicolon)')
@click.option('--pubkey',
              type=click.Path(exists=True, file_okay=True, dir_okay=False,
                              writable=False, readable=True, resolve_path=True),
              help='Path to the public key to use when accessing gitfs formulas')
@click.option('--privkey',
              type=click.Path(exists=True, file_okay=True, dir_okay=False,
                              writable=False, readable=True, resolve_path=True),
              help='Path to the private key to use when accessing gitfs formulas')
@click.option('--use_default_keys', is_flag=True, help='Use your default key pairs when accessing gitfs formulas')
@click.option('--boot2docker', is_flag=True, help='Docker is running with boot2docker')
@click.argument('states', nargs=-1)
def test(formula_dir, pillar_file, gitfs_formula, pubkey, privkey, use_default_keys, boot2docker, states):

    config = {}

    # salinity.json support will be removed in salinity 0.4
    if os.path.exists("salinity.json"):
        if be_verbose:
            print(colored("Found local config for salinity (salinity.json)", "yellow"))

        print(colored("DEPRECATION WARNING : salinity config file in JSON format will no longer be supported in the next salinity release.\nPlease convert your config file in the YAML format",
                      "orange"))

        try:
            config = json.loads(open("salinity.json").read())
        except:
            if be_verbose:
                print(colored("salinity failed loading local config", "red"))
            config = {}

    if os.path.exists("salinity.yml"):
        if be_verbose:
            print(colored("Found local config for salinity (salinity.yml)", "yellow"))

        try:
            config = yaml.load(open("salinity.yml").read())
        except:
            if be_verbose:
                print(colored("salinity failed loading local config", "red"))
            config = {}

    salinity_path = os.path.dirname(os.path.abspath(__file__))

    user_home_dir = os.path.expanduser('~')

    if boot2docker or config.get('boot2docker', False):

        # if using boot2docker only path located inside the user homedir can be mounted in a container
        if not formula_dir.startswith(user_home_dir):
            print(colored("Enable to configure the docker container properly", "red"))
            if be_verbose:
                print(colored('When using boot2docker to run your docker containers, you need to locate the directory containing your salt formula repositories somewhere inside your home directory (%s)' % user_home_dir, "orange"))
            exit(1)

    # create temp dir to share files with the docker container
    salinity_user_dir = os.path.join(user_home_dir, '.salinity')
    if not os.path.exists(salinity_user_dir):
        os.mkdir(salinity_user_dir)
    temp_dir_path = tempfile.mkdtemp(dir=salinity_user_dir)

    if be_verbose:
        print(colored('Created temp dir for salinity data at %s' % temp_dir_path, 'yellow'))

    if pillar_file or 'pillar_file' in config:
        if pillar_file:
            pillar_file_path = pillar_file
        else:
            pillar_file_path = config['pillar_file']
        shutil.copyfile(pillar_file_path, os.path.join(temp_dir_path, u'salinity.sls'))

    if gitfs_formula or 'gitfs_formula' in config:

        param_formulas = list(gitfs_formula) if gitfs_formula is not () else []
        formulas = set(param_formulas + config.get('gitfs_formula', []))

        use_rsa = False
        if use_default_keys and os.path.exists(os.path.expanduser('~/.ssh/id_rsa')) and os.path.exists(os.path.expanduser('~/.ssh/id_rsa.pub')):
            shutil.copyfile(os.path.expanduser('~/.ssh/id_rsa'), os.path.join(temp_dir_path, u'user_rsa'))
            shutil.copyfile(os.path.expanduser('~/.ssh/id_rsa.pub'), os.path.join(temp_dir_path, u'user_rsa.pub'))
            use_rsa = True
        elif pubkey and privkey:
            shutil.copyfile(privkey, os.path.join(temp_dir_path, u'user_rsa'))
            shutil.copyfile(pubkey, os.path.join(temp_dir_path, u'user_rsa.pub'))
            use_rsa = True

        salt_extra_config = open(os.path.join(temp_dir_path, u'extra_config'), 'w')
        salt_extra_config.write("fileserver_backend:\n  - roots\n  - git\n")
        salt_extra_config.write("gitfs_provider: pygit2\n")
        salt_extra_config.write("gitfs_remotes:\n")
        for formula in formulas:
            salt_extra_config.write("  - %s\n" % formula)

        if use_rsa:
            salt_extra_config.write("gitfs_privkey: /etc/ssh/user_rsa\n")
            salt_extra_config.write("gitfs_pubkey: /etc/ssh/user_rsa.pub\n")

        # if passphrase:
        #     salt_extra_config.write("gitfs_passphrase: %s\n" % passphrase)

        salt_extra_config.close()

    # install container preparation script
    shutil.copyfile(os.path.join(salinity_path, 'prepare_tests.py'), os.path.join(temp_dir_path, u'prepare_tests.py'))

    # launch docker container and run salt-call
    if be_verbose:
        print(colored('Launching tests of %s on docker' % u','.join(states), 'green'))

    command = "docker run -i -v %s:/salinity -v %s:/formula -t julozi/wheezy-salt-base sh -c 'python /salinity/prepare_tests.py %s && salt-call state.highstate && bash'" % (temp_dir_path, formula_dir, u' '.join(states))
    # command = "docker run -i -v %s:/salinity -v %s:/formula -t julozi/wheezy-salt-base sh -c 'bash'" % (temp_dir_path, formula_dir)
    if be_verbose:
        print(colored('Command line : %s' % command, 'yellow'))
    subprocess.call(command, shell=True)

    shutil.rmtree(temp_dir_path)
    if be_verbose:
        print(colored('Salinity temp dir deleted successfully', 'green'))


def main():
    cli()
