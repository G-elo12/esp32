const socket = io();

const humidityData = {
    labels: [],
    datasets: [
        { label: 'Humidity 1', data: [], borderColor: 'blue', fill: false },
        { label: 'Humidity 2', data: [], borderColor: 'green', fill: false },
        { label: 'Humidity 3', data: [], borderColor: 'red', fill: false },
        { label: 'Humidity 4', data: [], borderColor: 'purple', fill: false }
    ]
};

const temperatureData = {
    labels: [],
    datasets: [{ label: 'Temperature', data: [], borderColor: 'orange', fill: false }]
};

const humidityChart = new Chart(document.getElementById('humidityChart').getContext('2d'), {
    type: 'line',
    data: humidityData,
    options: { responsive: true, scales: { y: { beginAtZero: true, max: 100 } } }
});

const temperatureChart = new Chart(document.getElementById('temperatureChart').getContext('2d'), {
    type: 'line',
    data: temperatureData,
    options: { responsive: true, scales: { y: { beginAtZero: true } } }
});

socket.on('sensor_update', (data) => {
    document.getElementById('humidity1').textContent = data.humidity1.toFixed(2);
    document.getElementById('humidity2').textContent = data.humidity2.toFixed(2);
    document.getElementById('humidity3').textContent = data.humidity3.toFixed(2);
    document.getElementById('humidity4').textContent = data.humidity4.toFixed(2);
    document.getElementById('temperature').textContent = data.temperature.toFixed(2);
    document.getElementById('timestamp').textContent = new Date(data.timestamp).toLocaleString();

    // Actualizar gráficos
    humidityData.labels.push(new Date(data.timestamp).toLocaleTimeString());
    humidityData.datasets[0].data.push(data.humidity1);
    humidityData.datasets[1].data.push(data.humidity2);
    humidityData.datasets[2].data.push(data.humidity3);
    humidityData.datasets[3].data.push(data.humidity4);
    temperatureData.labels.push(new Date(data.timestamp).toLocaleTimeString());
    temperatureData.datasets[0].data.push(data.temperature);

    // Limitar a 20 puntos en el gráfico
    if (humidityData.labels.length > 20) {
        humidityData.labels.shift();
        humidityData.datasets.forEach(dataset => dataset.data.shift());
        temperatureData.labels.shift();
        temperatureData.datasets[0].data.shift();
    }

    humidityChart.update();
    temperatureChart.update();
});

// Cargar datos recientes al iniciar
fetch('/api/recent-data')
    .then(response => response.json())
    .then(data => {
        data.forEach(item => {
            humidityData.labels.push(new Date(item.timestamp).toLocaleTimeString());
            humidityData.datasets[0].data.push(item.humidity1);
            humidityData.datasets[1].data.push(item.humidity2);
            humidityData.datasets[2].data.push(item.humidity3);
            humidityData.datasets[3].data.push(item.humidity4);
            temperatureData.labels.push(new Date(item.timestamp).toLocaleTimeString());
            temperatureData.datasets[0].data.push(item.temperature);
        });
        humidityChart.update();
        temperatureChart.update();
    });