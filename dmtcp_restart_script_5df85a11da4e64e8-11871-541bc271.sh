#!/bin/bash

set -m # turn on job control

#This script launches all the restarts in the background.
#Suggestions for editing:
#  1. For those processes executing on the localhost, remove
#     'ssh <hostname> from the start of the line. 
#  2. If using ssh, verify that ssh does not require passwords or other
#     prompts.
#  3. Verify that the dmtcp_restart command is in your path on all hosts,
#     otherwise set the remote_prefix appropriately.
#  4. Verify DMTCP_HOST and DMTCP_PORT match the location of the
#     dmtcp_coordinator. If necessary, add
#     'DMTCP_PORT=<dmtcp_coordinator port>' after 'DMTCP_HOST=<...>'.
#  5. Remove the '&' from a line if that process reads STDIN.
#     If multiple processes read STDIN then prefix the line with
#     'xterm -hold -e' and put '&' at the end of the line.
#  6. Processes on same host can be restarted with single dmtcp_restart
#     command.


usage_str='USAGE:
  dmtcp_restart_script.sh [OPTIONS]

OPTIONS:
  --host, -h, (environment variable DMTCP_HOST):
      Hostname where dmtcp_coordinator is running
  --port, -p, (environment variable DMTCP_PORT):
      Port where dmtcp_coordinator is running
  --hostfile <arg0> :
      Provide a hostfile (One host per line, "#" indicates comments)
  --restartdir, -d, (environment variable DMTCP_RESTART_DIR):
      Directory to read checkpoint images from
  --batch, -b:
      Enable batch mode for dmtcp_restart
  --disable-batch, -b:
      Disable batch mode for dmtcp_restart (if previously enabled)
  --interval, -i, (environment variable DMTCP_CHECKPOINT_INTERVAL):
      Time in seconds between automatic checkpoints
      (Default: Use pre-checkpoint value)
  --help:
      Print this message and exit.'


coord_host=$DMTCP_HOST
if test -z "$DMTCP_HOST"; then
  coord_host=iiitd-HP-Compaq-dx7400-Microtower
fi

coord_port=$DMTCP_PORT
if test -z "$DMTCP_PORT"; then
  coord_port=7779
fi

checkpoint_interval=$DMTCP_CHECKPOINT_INTERVAL
if test -z "$DMTCP_CHECKPOINT_INTERVAL"; then
  checkpoint_interval=0
fi

maybebatch=

if [ $# -gt 0 ]; then
  while [ $# -gt 0 ]
  do
    if [ $1 = "--help" ]; then
      echo "$usage_str"
      exit
    elif [ $1 = "--batch" -o $1 = "-b" ]; then
      maybebatch='--batch'
      shift
    elif [ $1 = "--disable-batch" ]; then
      maybebatch=
      shift
    elif [ $# -ge 2 ]; then
      case "$1" in 
        --host|-h)
          coord_host="$2";;
        --port|-p)
          coord_port="$2";;
        --hostfile)
          hostfile="$2"
          if [ ! -f "$hostfile" ]; then
            echo "ERROR: hostfile $hostfile not found"
            exit
          fi;;
        --restartdir|-d)
          DMTCP_RESTART_DIR=$2;;
        --interval|-i)
          checkpoint_interval=$2;;
        *)
          echo "$0: unrecognized option '$1'. See correct usage below"
          echo "$usage_str"
          exit;;
      esac
      shift
      shift
    elif [ $1 = "--help" ]; then
      echo "$usage_str"
      exit
    else
      echo "$0: Incorrect usage.  See correct usage below"
      echo
      echo "$usage_str"
      exit
    fi
  done
fi

dmt_rstr_cmd=dmtcp_restart
which dmtcp_restart > /dev/null \
 || dmt_rstr_cmd=/usr/bin/dmtcp_restart

local_prefix=
remote_prefix=
remote_dmt_rstr_cmd=dmtcp_restart
if ! test -z "$remote_prefix"; then
  remote_dmt_rstr_cmd="$remote_prefix/bin/dmtcp_restart"
fi

# Number of hosts in the computation = 1
# Number of processes in the computation = 1

given_ckpt_files=" /home/iiitd/code/microcast-desktop/ckpt_python2.7_5df85a11da4e64e8-11871-541bc271.dmtcp"

ckpt_files=""
if [ ! -z "$DMTCP_RESTART_DIR" ]; then
  for tmp in $given_ckpt_files; do
    ckpt_files="$DMTCP_RESTART_DIR/$(basename $tmp) $ckpt_files"
  done
else
  ckpt_files=$given_ckpt_files
fi

coordinator_info=
if [ -z "$maybebatch" ]; then
  coordinator_info="--host $coord_host --port $coord_port"
fi

exec $dmt_rstr_cmd $coordinator_info\
  $maybebatch $maybejoin --interval "$checkpoint_interval"\
  $ckpt_files
