document.addEventListener('DOMContentLoaded', function() {
    const tipoDocumentoSelect = document.getElementById('id_tipo_documento');
    const trimestreSelect = document.getElementById('id_trimestre');
    
    if (tipoDocumentoSelect && trimestreSelect) {
        // Función para actualizar el estado del campo trimestre
        function actualizarTrimestre() {
            const selectedOption = tipoDocumentoSelect.options[tipoDocumentoSelect.selectedIndex];
            
            if (selectedOption.value) {
                // Hacer una consulta AJAX para obtener la periodicidad
                fetch(`/admin-panel/api/tipo-documento/${selectedOption.value}/`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.periodicidad === 'ANUAL') {
                            trimestreSelect.disabled = true;
                            trimestreSelect.value = '';
                            trimestreSelect.removeAttribute('required');
                        } else {
                            trimestreSelect.disabled = false;
                            trimestreSelect.setAttribute('required', 'required');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
            } else {
                trimestreSelect.disabled = false;
                trimestreSelect.removeAttribute('required');
            }
        }
        
        // Ejecutar al cargar la página
        actualizarTrimestre();
        
        // Ejecutar cuando cambie la selección
        tipoDocumentoSelect.addEventListener('change', actualizarTrimestre);
    }
});