async function getWeather() {
    const location = document.getElementById('location').value;
    try {
        const response = await fetch(`/getWeather?location=${location}`);
        const data = await response.json();
        document.getElementById('weather-info').innerText = `Weather in ${location}: ${data.weather}`;
    } catch (error) {
        console.error('Error fetching weather:', error);
        document.getElementById('error').innerText = 'Failed to fetch weather data.';
    }
}

function getTravelWeather() {
    const start = document.getElementById('start').value;
    const end = document.getElementById('end').value;
    fetch(`/getTravelWeather?start=${start}&end=${end}`)
        .then(response => response.json())
        .then(data => {
            let travelInfo = 'Weather along the route:\n';
            for (const city in data) {
                travelInfo += `${city}: ${data[city]}\n`;
            }
            document.getElementById('travel-weather-info').innerText = travelInfo;
        })
        .catch(error => {
            console.error('Error fetching travel weather:', error);
            document.getElementById('error').innerText = 'Failed to fetch travel weather data.';
        });
}

async function getActivities() {
    const location = document.getElementById('location').value;
    try {
        const response = await fetch(`/suggestActivities?location=${location}`);
        const activities = await response.json();
        document.getElementById('activities').innerText = `Suggested activities in ${location}: ${activities.join(', ')}`;
    } catch (error) {
        console.error('Error fetching activities:', error);
        document.getElementById('error').innerText = 'Failed to fetch activities data.';
    }
}
