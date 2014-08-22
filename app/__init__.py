from flask import Flask

app = Flask(__name__)

from app import routes

import time
print "\n\t-- Starting on " + time.strftime("%c") + " --\n"