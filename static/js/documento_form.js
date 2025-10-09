document.addEventListener('DOMContentLoaded', function() {
    const tipoDocumentoSelect = document.getElementById('id_tipo_documento');
    const trimestreSelect = document.getElementById('id_trimestre');
    const archivoInput = document.getElementById('id_archivo');
    
    // Datos de periodicidad por tipo de documento (esto debería venir del backend)
    const periodicidadData = {};
    
    // Función para obtener periodicidad del tipo de documento
    function updateTrimestre() {
        const selectedValue = tipoDocumentoSelect.value;
        
        if (!selectedValue) {
            trimestreSelect.disabled = true;
            trimestreSelect.value = '';
            return;
        }
        
        // Hacer petición AJAX para obtener la periodicidad
        fetch(`/admin-panel/api/tipo-documento/${selectedValue}/periodicidad/`)
            .then(response => response.json())
            .then(data => {
                periodicidadData[selectedValue] = data.periodicidad;
                
                if (data.periodicidad === 'ANUAL') {
                    trimestreSelect.disabled = true;
                    trimestreSelect.value = '';
                    trimestreSelect.parentElement.querySelector('.form-text').textContent = 'No aplica para documentos anuales';
                } else {
                    trimestreSelect.disabled = false;
                    trimestreSelect.parentElement.querySelector('.form-text').textContent = 'Requerido para documentos trimestrales';
                }
            })
            .catch(error => {
                console.log('Error al obtener periodicidad:', error);
                // Fallback: habilitar trimestre por defecto
                trimestreSelect.disabled = false;
            });
    }
    
    // Validación de archivo PDF
    function validateFile() {
        const file = archivoInput.files[0];
        const maxSize = 50 * 1024 * 1024; // 50MB
        
        if (file) {
            // Validar extensión
            if (!file.name.toLowerCase().endsWith('.pdf')) {
                alert('Solo se permiten archivos PDF');
                archivoInput.value = '';
                return false;
            }
            
            // Validar tamaño
            if (file.size > maxSize) {
                alert('El archivo es demasiado grande. Máximo 50MB permitido.');
                archivoInput.value = '';
                return false;
            }
            
            // Mostrar información del archivo
            const fileInfo = document.createElement('div');
            fileInfo.className = 'mt-2 text-muted';
            fileInfo.innerHTML = `
                <small>
                    <i class="fas fa-file-pdf me-1"></i>
                    ${file.name} (${formatFileSize(file.size)})
                </small>
            `;
            
            // Remover info anterior si existe
            const existingInfo = archivoInput.parentElement.querySelector('.file-info');
            if (existingInfo) {
                existingInfo.remove();
            }
            
            fileInfo.classList.add('file-info');
            archivoInput.parentElement.appendChild(fileInfo);
        }
        
        return true;
    }
    
    // Formatear tamaño de archivo
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Event listeners
    if (tipoDocumentoSelect) {
        tipoDocumentoSelect.addEventListener('change', updateTrimestre);
        
        // Ejecutar al cargar si hay valor seleccionado
        if (tipoDocumentoSelect.value) {
            updateTrimestre();
        }
    }
    
    if (archivoInput) {
        archivoInput.addEventListener('change', validateFile);
    }
    
    // Validación del formulario antes de enviar
    const form = document.getElementById('documentoForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            const tipoDocumento = tipoDocumentoSelect.value;
            const trimestre = trimestreSelect.value;
            
            // Validar que si es trimestral, se haya seleccionado trimestre
            if (tipoDocumento && periodicidadData[tipoDocumento] === 'TRIMESTRAL' && !trimestre) {
                e.preventDefault();
                alert('Debe seleccionar un trimestre para documentos trimestrales');
                trimestreSelect.focus();
                return false;
            }
            
            // Validar que si es anual, no haya trimestre
            if (tipoDocumento && periodicidadData[tipoDocumento] === 'ANUAL' && trimestre) {
                e.preventDefault();
                alert('Los documentos anuales no requieren trimestre');
                return false;
            }
            
            return true;
        });
    }
});