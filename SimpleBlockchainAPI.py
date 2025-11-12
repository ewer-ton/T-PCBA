import datetime
import json
import hashlib
from flask import Flask, jsonify, request

# --- Blockchain Class Definition ---

class Blockchain:
    """
    Implements a basic cryptographic blockchain structure.
    """
    def __init__(self):
        # The main list to hold the chain of blocks
        self.chain = []
        # Create the genesis block
        self.create_blockchain(proof=1, previous_hash='0')

    def create_blockchain(self, proof, previous_hash):
        """
        Creates a new block and adds it to the chain.
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash
        }
        self.chain.append(block)
        return block

    def get_previous_block(self):
        """
        Returns the last block in the chain.
        """
        last_block = self.chain[-1]
        return last_block

    def proof_of_work(self, previous_proof):
        """
        Proof of Work algorithm: Finds a number 'new_proof' such that
        hash(new_proof**2 - previous_proof**2) starts with '0000'.
        """
        new_proof = 1
        check_proof = False
        while check_proof is False:
            # The hashing problem/algorithm
            hash_operation = hashlib.sha256(str(new_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            
            # Check for the required difficulty (4 leading zeros)
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        """
        Generates a SHA-256 hash of an entire block.
        :param block: A block (dictionary)
        :return: The cryptographic hash string
        """
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        """
        Checks if the entire chain is valid by verifying links and PoW for every block.
        """
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            
            # 1. Check if the previous_hash links correctly
            if block["previous_hash"] != self.hash(previous_block):
                return False

            # 2. Check if the Proof of Work is valid
            previous_proof = previous_block['proof']
            current_proof = block['proof']
            hash_operation = hashlib.sha256(str(current_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            
            # Check for the required difficulty
            if hash_operation[:4] != '0000':
                return False
                
            # Move to the next block
            previous_block = block
            block_index += 1
        return True

# --- Flask Web Application Setup ---

# Create the Flask app instance
app = Flask(__name__)

# Create a Blockchain instance
blockchain = Blockchain()


# --- API Endpoints ---

@app.route('/', methods=['GET'])
def home():
    """
    Provides instructions and available endpoints.
    """
    response = {
        'message': 'Welcome to the Python Blockchain API!',
        'instructions': 'Use the following endpoints to interact with the chain:',
        'endpoints': {
            'Mine Block': '/mine_block',
            'Get Full Chain': '/get_chain',
            'Check Validity': '/is_valid'
        }
    }
    return jsonify(response), 200


@app.route('/mine_block', methods=['GET'])
def mine_block():
    """
    Mines a new block by solving the Proof of Work and adding it to the chain.
    """
    # Get necessary data from the last block
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    
    # Solve Proof of Work
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)

    # Create the new block
    block = blockchain.create_blockchain(proof, previous_hash)
    
    # Create the response
    response = {
        'message': 'Congratulations, you just mined a block!',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }
    return jsonify(response), 200


@app.route('/get_chain', methods=['GET'])
def get_chain():
    """
    Returns the full blockchain.
    """
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/is_valid', methods=['GET'])
def is_valid():
    """
    Checks if the current blockchain is valid.
    """
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'The Blockchain is valid. Integrity verified.'}
    else:
        response = {'message': 'The Blockchain is NOT valid! Tampering detected.'}
    return jsonify(response), 200


# --- Run the App ---

if __name__ == '__main__':
    # Running on port 5000 is common for these types of tutorials
    app.run(host='0.0.0.0', port=5000)