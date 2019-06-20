from flask import Flask, request, render_template, redirect
import db
import util
import json
from app.DGA import *

app = Flask(__name__)

@app.route('/')
def hello_world():
    ConctracList = db.getConctracList()
    return render_template('contractList.html', contractList = ConctracList), 200

@app.route('/createIndex')
def createIndex():
    return render_template('ContractIndex.html'), 200

@app.route('/getDGA', methods=['POST'])
def getDGA():
    contractId = request.form.get('contractId', default='id')
    print(contractId)
    fsm_struct = util.read_fsm(contractId)
    print(fsm_struct)
    res = {'fsm': fsm_struct}
    return json.dumps(res), 200

@app.route('/saveContract', methods=['POST'])
def saveContract():
    args = request.get_json() 
    contract_id = util.get_id(args['contract_name'])
    jsondata = json.dumps(args['content'])
    GenerateDGA(jsondata, contract_id)
    res = db.save_contract(args['contract_name'], contract_id, args['Obligor'],args['creditor'], jsondata)

    ConctracList = db.getConctracList()
    return render_template('contractList.html', contractList = ConctracList), 200

@app.route('/content/<contractId>')
def getContent(contractId):
    contract = db.getContent(contractId)
    content = []
    content.append(contract[0])
    content.append(contract[1])
    content.append(contract[2])
    content.append(contract[3])
    content.append(json.loads(contract[4]))
    return render_template('ContractIndex.html', id=contractId, contract=content), 200

@app.route('/ContractList')
def showlist():
    ConctracList = db.getConctracList()
    return render_template('contractList.html', contractList = ConctracList), 200

@app.route('/DGA/<contractId>')
def showDGA(contractId):
    return render_template('DGA.html', contractId = contractId), 200

if __name__ == '__main__':
    config = util.get_config()
    host = config["host"]
    port = int(config["port"])
    debug = config["debug"]
    if debug == "True":
        debug = True
    else:
        debug = False
    app.run(host=host, port=port, threaded=True, debug=debug)
