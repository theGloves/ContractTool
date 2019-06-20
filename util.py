import json
import datetime
import hashlib
from datetime import datetime

def get_config():
    with open('./config.json', 'r') as f:
        str_config = f.read()
    config = json.loads(str_config)
    return config

def get_id(contract_name):
    str_now = datetime.now().strftime("%Y%m%d%H%M%S")
    str_id = contract_name + str_now
    str_hash = hashlib.sha256(str_id.encode()).hexdigest()
    return str_hash[-8:]

def process_code(filename):
    st = ''
    with open('./code/' + filename, 'r') as fs:
        lines = fs.readlines()
        for line in lines:
            line = line.replace(' ', '&nbsp;&nbsp;')
            st = st + line.strip() + '<br>'
        return st
        
def read_fsm(filename):
    with open('./DGA/' + filename, 'r') as fs:
        fsm = json.load(fs)
    return fsm