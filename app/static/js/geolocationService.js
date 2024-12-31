export function geolocateUser(onSuccess, onError) {

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const { latitude, longitude } = position.coords;

                console.log('Sending latitude and longitude:', { latitude, longitude });

                // Fetch planetary hour data
                fetch('/api/geolocation_ephemeris', {

                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ latitude, longitude }),
                })
                    .then((response) => response.json())
                    .then((data) => {
                        console.log('Geolocation and planetary hour data:', data);
                        if (onSuccess) onSuccess(data, latitude, longitude);
                    })
                    .catch((error) => {
                        console.error('Error fetching planetary hour data:', error.message);
                        if (onError) onError(error);
                    });
            },
            (error) => {
                console.error('Geolocation error:', error.message);
                if (onError) onError(error);
            }
        );
    } else {
        console.error('Geolocation is not supported by this browser.');
        if (onError) onError(new Error('Geolocation not supported'));
    }
}
