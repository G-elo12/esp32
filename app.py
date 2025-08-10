from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, send
import json
from datetime import datetime
import os

# Configuración de la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tu_clave_secreta_aqui')

# Configurar SocketIO con CORS habilitado para conexiones externas
socketio = SocketIO(app, cors_allowed_origins="*", 
                   async_mode='threading',
                   ping_timeout=60,
                   ping_interval=25)

# Almacenar datos de sensores y estado de actuadores
sensor_data = {
    'temperature': 0,
    'humidity': 0,
    'last_update': None
}

actuator_states = {
    'led': False,
    'relay': False,
    'servo_angle': 0
}

# Lista de ESP32s conectados
connected_esp32s = []

@app.route('/')
def index():
    """Página principal para monitoreo web"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API REST para obtener estado actual"""
    return json.dumps({
        'sensors': sensor_data,
        'actuators': actuator_states,
        'connected_devices': len(connected_esp32s)
    })

# Eventos WebSocket para ESP32
@socketio.on('esp32_connect')
def handle_esp32_connection(data):
    """Maneja la conexión de un ESP32"""
    device_id = data.get('device_id', 'unknown')
    if device_id not in connected_esp32s:
        connected_esp32s.append(device_id)
    
    print(f"ESP32 conectado: {device_id}")
    emit('connection_ack', {'status': 'connected', 'device_id': device_id})
    
    # Notificar a clientes web sobre nueva conexión
    socketio.emit('device_status', {
        'type': 'esp32_connected',
        'device_id': device_id,
        'total_devices': len(connected_esp32s)
    }, room='web_clients')

@socketio.on('sensor_data')
def handle_sensor_data(data):
    """Recibe datos de sensores del ESP32"""
    global sensor_data
    
    # Actualizar datos de sensores
    sensor_data.update({
        'temperature': data.get('temperature', 0),
        'humidity': data.get('humidity', 0),
        'light': data.get('light', 0),
        'last_update': datetime.now().isoformat()
    })
    
    print(f"Datos recibidos: {data}")
    
    # Enviar datos actualizados a clientes web
    socketio.emit('sensor_update', sensor_data, room='web_clients')
    
    # Confirmar recepción al ESP32
    emit('data_received', {'status': 'ok'})

@socketio.on('actuator_status')
def handle_actuator_status(data):
    """Recibe estado actual de actuadores del ESP32"""
    global actuator_states
    actuator_states.update(data)
    
    # Notificar a clientes web
    socketio.emit('actuator_update', actuator_states, room='web_clients')

# Eventos WebSocket para clientes web
@socketio.on('web_connect')
def handle_web_connection():
    """Maneja conexión de cliente web"""
    # Unir a sala de clientes web
    from flask_socketio import join_room
    join_room('web_clients')
    
    # Enviar estado actual
    emit('initial_data', {
        'sensors': sensor_data,
        'actuators': actuator_states,
        'connected_devices': len(connected_esp32s)
    })

@socketio.on('control_actuator')
def handle_actuator_control(data):
    """Controla actuadores desde cliente web"""
    actuator_type = data.get('type')
    value = data.get('value')
    
    # Actualizar estado local
    if actuator_type in actuator_states:
        actuator_states[actuator_type] = value
    
    # Enviar comando a todos los ESP32 conectados
    socketio.emit('actuator_command', {
        'type': actuator_type,
        'value': value
    }, room='esp32_devices')
    
    print(f"Comando enviado: {actuator_type} = {value}")

@socketio.on('esp32_join')
def handle_esp32_join():
    """ESP32 se une a su sala específica"""
    from flask_socketio import join_room
    join_room('esp32_devices')

@socketio.on('disconnect')
def handle_disconnect():
    """Maneja desconexiones"""
    # Aquí podrías implementar lógica para remover ESP32s de la lista
    print("Cliente desconectado")

# Funciones auxiliares para comandos específicos
def send_command_to_esp32(command, value):
    """Envía un comando específico a todos los ESP32"""
    socketio.emit('command', {
        'action': command,
        'value': value,
        'timestamp': datetime.now().isoformat()
    }, room='esp32_devices')

# Endpoints para comandos directos (opcional)
@app.route('/api/control/<actuator>/<value>')
def control_actuator_api(actuator, value):
    """Control de actuadores vía API REST"""
    try:
        # Convertir valor según el tipo
        if actuator in ['led', 'relay']:
            value = value.lower() == 'true'
        elif actuator == 'servo_angle':
            value = int(value)
        
        actuator_states[actuator] = value
        send_command_to_esp32(actuator, value)
        
        return json.dumps({'status': 'success', 'actuator': actuator, 'value': value})
    except Exception as e:
        return json.dumps({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)