from flask import Flask, jsonify
from flask_socketio import SocketIO
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)
socketio = SocketIO(app)

# Import routes from other files
from calculateReynoldsNumber import calculate_bp
from regimeDecide import regime_bp
from batchProcess import batch_bp, MAX_BATCH_UPLOAD_BYTES

app.config["MAX_CONTENT_LENGTH"] = MAX_BATCH_UPLOAD_BYTES

# Register Blueprints
app.register_blueprint(calculate_bp)
app.register_blueprint(regime_bp)
app.register_blueprint(batch_bp)


@app.errorhandler(RequestEntityTooLarge)
def handle_request_entity_too_large(_error):
    max_size_mb = MAX_BATCH_UPLOAD_BYTES / (1024 * 1024)
    return jsonify(
        {"error": f"File is too large. Maximum upload size is {max_size_mb:.0f} MB."}
    ), 413

if __name__ == '__main__':
    socketio.run(app, debug=True)
