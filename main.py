from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from database import init_db, save_sensor_data, get_recent_data
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Cambia esto por una clave segura
socketio = SocketIO(app, cors_allowed_origins="*")

# Inicializar la base de datos
init_db()

# Ruta para el dashboard
@app.route('/')
def index():
    return render_template('index.html')

# API para recibir datos de los sensores
@app.route('/api/sensors', methods=['POST'])
def receive_sensor_data():
    try:
        data = request.get_json()
        humidity1 = data.get('humidity1')
        humidity2 = data.get('humidity2')
        humidity3 = data.get('humidity3')
        humidity4 = data.get('humidity4')
        temperature = data.get('temperature')

        if None in (humidity1, humidity2, humidity3, humidity4, temperature):
            return jsonify({"error": "Missing sensor data"}), 400

        # Guardar datos en la base de datos
        save_sensor_data(humidity1, humidity2, humidity3, humidity4, temperature)

        # Emitir datos a los clientes conectados
        socketio.emit('sensor_update', {
            'humidity1': humidity1,
            'humidity2': humidity2,
            'humidity3': humidity3,
            'humidity4': humidity4,
            'temperature': temperature,
            'timestamp': datetime.datetime.now().isoformat()
        })

        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API para obtener datos recientes
@app.route('/api/recent-data', methods=['GET'])
def recent_data():
    data = get_recent_data()
    return jsonify(data)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)