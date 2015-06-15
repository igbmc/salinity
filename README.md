# Salinity

Test your Salt formula on a Docker container

## Requirements

- A running Docker system
- Python 2.7

## Limitations

Currently `salinity` only supports running your formula on a Debian 7 environment.

## Install

    $ sudo pip install salinity

## Usage

`salinity`provides two commands :

* `publickey` : Retrieve the public key used by salt to access your formulas through gitfs
* `test` : Test salt states on a local docker container

For more details use `salinity --help`

## Example

Test a salt state from a formula located in `/home/me/my_formula_repo`

    $ sality test --formula_dir=/home/me/my_formula_repo my_formula.my_state

Test a salt state with a test pillar file :

    $ salinity test --formula_dir=/home/me/my_formula_repo --pillar_file=test.pillar my_formula_my_state

Test a salt state with dependencies from a formula stored on a git server :

    $ salinity test --formula_dir=/home/me/my_formula_repo gitfs_formula=ssh://git@serv-gitlab.igbmc.u-strasbg.fr/saltstack-formulas/odbc-formula.git my_formula.my_state

The `gitfs_formula` option can be used multiple time in the same salinity test call.
