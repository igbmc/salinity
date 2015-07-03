# Salinity

Test your Salt formula on a Docker container

## Requirements

- A docker host
- Python 2.7

## Limitations

Currently Salinity only supports running your formula on a Debian 7 environment.

## Install

    $ sudo pip install salinity

## Getting started

Salinity let you run a salt formula located on your local computer in a virtual salt environment.

This quick example will show you how to use Salinity to test the official mysql formula.

**Clone the official mysql formula**

    $ git clone https://github.com/saltstack-formulas/mysql-formula.git

**Create a pillar test file for salinity**

    $ cd mysql-formula
    $ vim test.sls

Enter the following pillar data :

    mysql:
        server:
            root_user: 'admin'
            root_password: 'somepass'
            user: mysql

    lookup:
        server: mysql-server
        service: mysql

**Test the `mysql.server` state with salinity**

    $ salinity test --pillar_file=test.sls mysql.server
    [...]
    ----------
          ID: mysqld
    Function: service.running
        Name: mysql
      Result: True
     Comment: Service mysql is already enabled, and is running
     Started: 19:54:41.498938
    Duration: 3372.095 ms
     Changes:
              ----------
              mysql:
                  True

    Summary
    ------------
    Succeeded: 6 (changed=4)
    Failed:    0
    ------------
    Total states run:     6
    root@d7764b152842:/#

Salinity will start a docker container runningvsalt master and salt minion to test the `mysql.server` state.
Once the state has been applied on the container, Salinity stay in the container waiting for instruction.

You can either quit the container (Ctrl + D) or relaunch your state if you would like to check some modification in your formula :

    # salt-call state.highstate

**Clean up**

    # exit

If you leave the container, Salinity will delete any temporary files and return to your host shell

## Usage

The Salinity utility is handling commands in the form

    $ salinity [OPTIONS] COMMAND [ARGS]

Currently, the only command available is the `test` command.

### `test` command

The `test` command let you test one or more states of your formula on a virtual salt environment.

    $ salinity test [ARGS] [STATES]

**--formula_dir**

Path to the directory containing your salt formula. If not specified, Salinity will use current directory.

**--pillar_file**

Pillar file to use when applying the state

**--gitfs_formula**

Git repositories URL that should be made available on the salt master running your formula. Theses formulas are generally dependencies of the formula your are testing.

The option can be used several times.

Each URL should have one of the following form :
* https://github.com/saltstack-formulas/salt-formula.git
* git@github.com:user/repo.git
* ssh://user@domain.tld/path/to/repo.git

**--pubkey**

Path to the public key to use when accessing gitfs formulas through ssh.

**--privkey**

Path to the private key to use when accessing gitfs formulas through ssh.

Currently RSA keys protected by a passphrase are not supported.

**--use_default_keys**

Tell Salinity to use your default RSA keys (~/.ssh/id_rsa.pub and ~/.ssh/id_rsa).

Currently RSA keys protected by a passphrase are not supported.

**--boot2docker**

Tell Salinity that your docker host is based on the boot2docker image (for Mac OS and Windows environment).

## Using Salinity configuration file

Salinity can read options from a standard configuration file called `salinity.yml`. This file should be located in the directory from which Salinity is called.

Options passed to the command line have priority on the options read from the configuration file.

Here is a example of a `salinity.yml` file

    pillar_file: pillar.test.sls
    gitfs_formula:
        - https://github.com/saltstack-formulas/mysql-formula.git
        - https://github.com/saltstack-formulas/nginx-formula.git
    pubkey: ~/.ssh/salinity_rsa.pub
    privkey: ~/.ssh/salinity_rsa
