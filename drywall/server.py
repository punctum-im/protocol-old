#!/usr/bin/python3
#
# drywall, the example implementation of the Euphony protocol
#
##################

import os
from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask.ext.jsonpify import jsonify

server_root="/usr/share/nginx/html"

print("drywall starting up...")

if not os.access(server_root, os.W_OK):
  print("ERROR: Cannot access server directory (" + server_root + ")")
  quit(1)

