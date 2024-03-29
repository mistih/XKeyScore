# Kitlesel Takip Sistemi
# Author: Mistih
# Date: 2024-02-24
# Version: 1.0.0
# Type: Client

# This program is not work in the one machine, this program will be work in the 20 VPS machines.
# From main machine, the socket will be open the 20 VPS machines and the 20 VPS machines will be scan the whole network systems in the world and will notificate the main machine.

# Program: Main
# Description:  This program will be scan the whole network systems in the world and will be collect the data from 'OPEN SOURCE' the systems.
#               The data will examine by the Algorithm and data will be tagged by the Algorithm.
#               Data will be huge and the because of that the data will be stored in the 'Big Data' systems.
#               The data will be used for the 'Security' purposes.

# Importing the Libraries
import os
import time
import random
import urllib3
import socket
import json
import string
import re
import threading
import uuid

# Importing the Modules
from datetime import datetime
from App.Client.Socket import ClientSocket

def AuthKey():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=128))

def Port():
    return random.randint(64000, 64099)


s = ClientSocket("127.0.0.1", 8000, Port(), AuthKey())