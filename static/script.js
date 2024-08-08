// eslint-disable-next-line no-unused-vars
async function getWeather() {
    const location = document.getElementById('location').value;
    try {
        const response = await fetch(`/getWeather?location=${location}`);
        const data = await response.json();
        document.getElementById('weather-info').innerHTML = `
            <h3>Weather in ${location}</h3>
            <p>${data.weather}</p>
            <p>Rain Status: ${data.rain ? 'Yes' : 'No'}</p>
        `;
    } catch (error) {
        console.error('Error:', error);
    }
}

// eslint-disable-next-line no-unused-vars
async function getActivities() {
    const location = document.getElementById('location').value;
    try {
        const response = await fetch(`/suggestActivities?location=${location}`);
        const data = await response.json();
        const activitiesHtml = data.map(activity => `<li>${activity}</li>`).join('');
        document.getElementById('activities').innerHTML = `
            <h3>Suggested Activities</h3>
            <ul>${activitiesHtml}</ul>
        `;
    } catch (error) {
        console.error('Error:', error);
    }
}

// eslint-disable-next-line no-unused-vars
async function getTravelWeather() {
    const start = document.getElementById('start').value;
    const end = document.getElementById('end').value;
    try {
        const response = await fetch(`/getTravelWeather?start=${start}&end=${end}`);
        const data = await response.json();
        const weatherHtml = data.map(info => `
            <div class="weather-info">
                <h4>${info.location}</h4>
                <p>${info.weather}</p>
                <p>Rain Status: ${info.rain ? 'Yes' : 'No'}</p>
            </div>
        `).join('');
        const travelWeatherInfo = document.getElementById('travel-weather-info');
        travelWeatherInfo.innerHTML = weatherHtml;

        // Add vertical scrolling functionality
        travelWeatherInfo.style.maxHeight = '2500px';
        travelWeatherInfo.style.overflowY = 'auto';
        travelWeatherInfo.style.overflowX = 'hidden';
    } catch (error) {
        console.error('Error:', error);
    }
}