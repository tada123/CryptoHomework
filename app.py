from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:crypto123456@localhost:5432/crypto_wallet_db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/crypto_db'

with app.app_context():
    db = SQLAlchemy(app)

class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)

# Create new wallet
@app.route('/wallet', methods=['POST'])
def create_wallet():
    data = request.json
    symbol = data.get('symbol')

    # Verify crypto exists
    response = requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd')
    print("response: ", response)
    respobj = response.json()
    print("respobj: ", respobj)
    # if response.status_code != 200 or (symbol not in respobj):
    #     return (jsonify({'error': 'Invalid cryptocurrency symbol'}), 400)
    if response.status_code != 200:
        return (jsonify({'error': 'Invalid cryptocurrency symbol'}), 400)

    # Create the wallet
    wallet_entry = Wallet(symbol=symbol, amount=0)
    db.session.add(wallet_entry)
    db.session.commit()
    wid = wallet_entry.id
    print("wid: ", wid)
    singleUsdValue = respobj[symbol]['usd']
    return jsonify({'walletId': wid, 'message': 'Crypto added to wallet successfully', 'singleCoinUsdValue': singleUsdValue}), 201

@app.route('/wallet/<int:id>', methods=['GET'])
def get_wallet(id):
    wallet_entries = Wallet.query.get_or_404(id)
    return (jsonify([{ 'id': entry.id, 'symbol': entry.symbol, 'amount': entry.amount } for entry in wallet_entries]), 200)

@app.route('/wallet/<int:id>', methods=['PUT'])
def update_crypto(id):
    data = request.json
    amount = data.get('amount')
    wallet_entry = Wallet.query.get_or_404(id)
    wallet_entry.amount = amount
    symbol = wallet_entry.symbol
    db.session.commit()
    # Get current value in USD for response
    response = requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd')
    if response.status_code != 200:
        usdval = None
    else:
        respobj = response.json()
        usdval = respobj[symbol]['usd']
    return (jsonify({'message': 'Crypto amount updated successfully', 'walletUsdValue': (usdval * amount)}), 200)

@app.route('/wallet/<int:id>', methods=['DELETE'])
def delete_crypto(id):
    wallet_entry = Wallet.query.get_or_404(id)
    db.session.delete(wallet_entry)
    db.session.commit()
    return (jsonify({'message': 'Crypto deleted from wallet successfully'}), 200)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(host='0.0.0.0', port=8888)
else:
    raise NotImplementedError("This is not a library, please run from CLI instead")

