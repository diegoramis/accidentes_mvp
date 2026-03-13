function getLocation() {
  if (!navigator.geolocation) {
    alert('La geolocalización no está disponible en este dispositivo.');
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      document.getElementById('latitude').value = position.coords.latitude;
      document.getElementById('longitude').value = position.coords.longitude;
    },
    () => {
      alert('No se pudo obtener la ubicación. Verifica permisos del navegador.');
    }
  );
}
