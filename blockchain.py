import hashlib
from time import time
from uuid import uuid4
from flask import Flask, abort, jsonify, request, redirect
from flask_cors import CORS

class Blockchain:
    def __init__(self):
        self.ch = [] #chain
        self.first_block()

    def first_block(self):
        index = len(self.ch) + 1
        d = '' #data
        nonee = 0
        final_block = blockchain.ch[-1] if len(self.ch) else None
        before_hash = final_block['hash'] if final_block else '0'

        block = {
            'index': index,
            'timestamp': time(),
            'd': d,
            'nonee': nonee,
            'before_hash': before_hash
        }

        self.ch.append(block)
        self.hash_calculate(index)
        self.block_validation(index)
    
    def mining(self, index):
        block = self.ch[index - 1]
        nonee = 0

        while not self.hash_validation(index, nonee=nonee):
            nonee += 1
        
        block['nonee'] = nonee
        self.block_calculation_and_validation(index)

    def hash_validation(self, index, nonee=None):
        block = self.ch[index - 1]
        d = block['d']
        previous_hash = block['before_hash']
        if nonee is None:
            nonee = block['nonee']
        return Blockchain.hash(index, d, previous_hash, nonee)[:4] == '0000'
    
    def data_change(self, index, d):
        block = self.ch[index - 1]
        block['d'] = str(d)
        self.block_calculation_and_validation(index)
    
    def nonee_change(self, index, nonee):
        block = self.ch[index - 1]
        block['nonee'] = str(nonee)
        self.block_calculation_and_validation(index)
    
    def hash_calculate(self, index):
        block = self.ch[index - 1]
        d = block['d']
        nonee = block['nonee']

        before_block = self.ch[index - 2] if (len(self.ch) > 1 and index > 1) else None
        before_hash = before_block['hash'] if before_block else '0'

        new_hash_block = Blockchain.hash(index, d, before_hash, nonee)
        block['hash'] = new_hash_block

    def block_validation(self, index):
        block = self.ch[index - 1]

        previous_block = self.ch[index - 2] if (len(self.ch) > 1 and index > 1) else None
        block['previous_hash'] = previous_block['hash'] if previous_block else '0'

        block['validated'] = self.hash_validation(index)

    def block_calculation_and_validation(self, index):
        for i in range(index, len(self.ch) + 1):
            self.hash_calculate(i)
            self.block_validation(i)

    @staticmethod
    def hash(index, data, previous_hash, nonee):
        return hashlib.sha1((str(index) + data + previous_hash + str(nonee)).encode()).hexdigest()


app = Flask(__name__)
CORS(app)

blockchain = Blockchain()

@app.route('/chain', methods=['GET'])
def complete_chain():
    response = {
        'chain': blockchain.ch,
        'length': len(blockchain.ch),
    }
    return jsonify(response), 200

@app.route('/newblock', methods=['GET'])
def new_block():
    blockchain.first_block()
    return redirect('/chain')

@app.route('/mine/<int:index>', methods=['GET'])
def mining(index):
    blockchain.mining(index=index)
    return redirect('/chain')

@app.route('/changedata/<int:index>', methods=['GET'])
def data_change(index):
    values = request.args
    print(values)
    required = ['d']
    for x in required:
        if x not in values:
            return abort(400)

    d = values['d']
    blockchain.data_change(index, d)

    return redirect('/chain')

@app.route('/changenonce/<int:index>', methods=['GET'])
def nonee_change(index):
    values = request.args
    print(values)
    required = ['nonee']
    for x in required:
        if x not in values:
            return abort(400)

    nonce = values['nonce']
    blockchain.nonee_change(index, nonce)

    return redirect('/chain')

@app.route('/clear', methods=['GET'])
def blockchain_clear():
    blockchain.__init__()
    return redirect('/chain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
