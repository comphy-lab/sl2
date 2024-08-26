from flask import Blueprint, request, jsonify

regime_bp = Blueprint('regime', __name__)

# Define the regime classification function
def classify_regime(row):
    oh, we = row['Oh'], row['We']
    if oh <= 1 / we ** 2:
        return 'I'
    elif 1 / we ** 2 < oh <= 1 / we ** (3 / 4):
        return 'II'
    elif 1 / we ** (3 / 4) < oh <= we ** 0.5:
        return 'III'
    elif we ** 0.5 < oh:
        return 'IV'
    else:
        return 'Undefined'

@regime_bp.route('/regime', methods=['POST'])
def decide_regime():
    data = request.json
    weber_number = data.get('weberNumber')
    ohnesorge_number = data.get('ohnesorgeNumber')
    if weber_number is None or ohnesorge_number is None:
        return jsonify({'error': 'Missing parameters'}), 400
    try:
        weber_number = float(weber_number)
        ohnesorge_number = float(ohnesorge_number)
        row = {'We': weber_number, 'Oh': ohnesorge_number}
        regime = classify_regime(row)
        return jsonify({'regime': regime})
    except ValueError:
        return jsonify({'error': 'Invalid input'}), 400
