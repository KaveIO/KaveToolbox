#!/bin/bash
##############################################################################
#
# Copyright 2016 KPMG Advisory N.V. (unless otherwise stated)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
##############################################################################

mhelp='ProtectNotebooks.sh,\n\tappend to ipython_notebook_config.py,\n\tadd password protection to notebooks\n\tset default port number to a semi-unique hash of the username\n\n\tIf run as root or sudoer, will set the system wide ipython notebook config,\n\t\telse will set the user-specific one\n\n\tIn order to correctly protect, first you should create a valid ssl certificate for the server, for example\n\topenssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout mycert.pem -out mycert.pem #self-signed certificate\n\nusage ProtectNotebooks.sh /path/to/ssl/certificate [profilename] [--help]\n\tpositional args: /path/to/ssl/certificate, must be set to the path of a valid ssl certificate for this domain (localhost)\n\tprofilename=default (optional) if given will append to a different profile. Only applies when run as not a root user.\n\toptional args: --help: print this help and exit'

# Parse Arguements

for i in "$@" ; do
    if [[ ${i} == "--help" ]] ; then
        echo -e ${mhelp}
        exit 0
    fi
done

if [ -z "$1" ]; then
    echo -e ${help}
    echo "Error: Not enough arguements specified" 1>&2
    exit 1
fi

CERTFILE=${1}

if [ ! -e "$CERTFILE" ]; then
    echo -e ${help}
    echo "Error: Certificate directory/file does not exist" 1>&2
    exit 2
fi

PROFILE="default"

if [ ! -z "$2" ]; then
    PROFILE="$2"
fi

# Find directory to write to

MUID=`id -u $USER`
USERIDIR="${HOME}/.ipython/profile_${PROFILE}"
USERJDIR="${HOME}/.jupyter"
ETCDIR="/etc"
ROOTIDIR="${ETCDIR}/ipython"
ROOTJDIR="${ETCDIR}/jupyter"
DEPLOYIDIR=${USERIDIR}
DEPLOYJDIR=${USERJDIR}
URL=`hostname -f`


if [[ ${USER} == 'root' ]] || [[ ${MUID} == 0 ]] || [ -w  ${ETCDIR} ]; then
    DEPLOYIDIR=${ROOTIDIR}
    DEPLOYJDIR=${ROOTJDIR}
fi

#echo $DEPLOYDIR $CERTFILE
#exit 0

# Deploy

mkdir -p ${DEPLOYIDIR}

cat << EOF >> ${DEPLOYIDIR}/ipython_notebook_config.py
#
# Password protect ipython notebooks with user's login password
# each user forced to re-enter login credentials on starting a server
#
import getpass
import os,sys,socket
from IPython.lib import passwd
import pam, signal

c = get_config()
user=getpass.getuser()
uid=os.geteuid()

def forcequit():
    """IPython configuration captures all exceptions thrown.
I need to force kill the parent program in case the wrong password is entered too often
"""
    pid=os.getpid()
    gpid=os.getpgid(0)
    ppid=os.getppid()
    gppid=os.getpgid(ppid)
    for sig in [signal.SIGTERM, signal.SIGKILL, signal.SIGABRT]:
        os.kill(ppid, sig)
        os.killpg(gppid, sig)
        os.kill(pid, sig)
        os.killpg(gpid, sig)


def setpass(user):
    """Ask the user for a login password, match it against the unix login password
set this password to ipython notebooks, or quit after three failures
"""
    prompt='password:'
    for tries in range(3):
        cleartext= getpass.getpass(prompt)
        if pam.authenticate(user, cleartext, service='login'):
            from IPython.lib import passwd
            c.NotebookApp.password = passwd(cleartext)
            return True
        else:
            prompt='Password not verified, please check this is your login password and try again\npassword:'
    print >> sys.stderr, "ERROR: Too many password fails"
    return False

try:
    if not setpass(user):
        forcequit()
except Exception as e:
    err1, err2, err3 = sys.exc_info()
    print >> sys.stderr, str(e)
    print >> sys.stderr, err1
    print >> sys.stderr, str(err2)
    print >> sys.stderr, str(err3)
    forcequit()
#
# Set the notebook's certificate
#
c.NotebookApp.certfile = "${CERTFILE}"

#
# Use localhost's fqdn for certificate
#
c.NotebookApp.ip=socket.getfqdn()

#
# Add username into the URL for extra obvious URL
#
c.NotebookApp.base_url=user.lower()

#
# Set an intelligent semi-unique default port for all users
# based on a hash of the username
#
import string
user=user.lower()
c.NotebookApp.port =int(8288+5*((len(user)%8)+(8*string.ascii_lowercase.index(user[0]))+2*(26-string.ascii_lowercase.index(user[-2]))))
EOF

#now copy to the jupyter config location also.

mkdir -p ${DEPLOYJDIR}

cp ${DEPLOYIDIR}/ipython_notebook_config.py ${DEPLOYJDIR}/jupyter_notebook_config.py

# Chmod result in case user is root

if [ ${DEPLOYIDIR} == ${ROOTIDIR} ]; then
    chmod -R a+rx ${ROOTIDIR}
fi

if [ ${DEPLOYJDIR} == ${ROOTJDIR} ]; then
    chmod -R a+rx ${ROOTJDIR}
fi
