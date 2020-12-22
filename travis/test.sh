#!/bin/sh
trap catch ERR

# travis test script for django app
#
# PRECONDITIONS:
#      * necessary test tooling already installed
#      * inherited env vars from application's .travis.yml MUST include:
#        DJANGO_APP: django application directory name

# start virtualenv
source bin/activate

# install test tooling
pip install pycodestyle coverage

function run_test {
    echo "##########################"
    echo "TEST: $1"
    eval $1
}

function catch {
    echo "Test failure occurred on line $LINENO"
    exit 1
}

run_test "pycodestyle ${DJANGO_APP}/ --exclude=migrations,static"

run_test "coverage run --source=${DJANGO_APP} '--omit=*/migrations/*' manage.py test ${DJANGO_APP}"

# put generaged coverage result where it will get processed
cp .coverage* /coverage

exit 0