from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

# Import routes from other files
from calculateReynoldsNumber import calculate_bp
from regimeDecide import regime_bp

# Register Blueprints
app.register_blueprint(calculate_bp)
app.register_blueprint(regime_bp)

if __name__ == '__main__':
    socketio.run(app, debug=True)
