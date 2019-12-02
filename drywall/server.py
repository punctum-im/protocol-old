#!/usr/bin/python3
#
# drywall, the example implementation of the Euphony protocol
#
##################

import os

server_root="/usr/share/nginx/html"

print("drywall starting up...")

if not os.access(server_root, os.W_OK):
  print("ERROR: Cannot access server directory (" + server_root + ")")
  quit(1)

