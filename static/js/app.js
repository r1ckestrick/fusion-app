document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('uploadForm');
    const btn = document.getElementById('submitBtn');
    const resultContainer = document.getElementById('result-container');
    const resultImage = document.getElementById('result-image');
    const shareBtn = document.getElementById('share-btn');
    
    // Elementos para la pantalla de landing
    const startBtn = document.getElementById('startBtn');
    const landingScreen = document.getElementById('landingScreen');
    const formContainer = document.getElementById('formContainer');
    
    // Elementos para la cámara
    const video = document.getElementById('video');
    const takePhotoBtn = document.getElementById('takePhotoBtn');
    const preview = document.getElementById('preview');
    const previewImg = document.getElementById('previewImg');
    
    // Crear input file real
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*';
    fileInput.name = 'image';
    fileInput.style.display = 'none';
    form.appendChild(fileInput);

    // Funcionalidad del botón COMENZAR
    startBtn.addEventListener('click', function() {
        landingScreen.classList.add('hide');
        formContainer.classList.add('show');
        startCamera();
    });

    // Funcionalidad de la cámara
    function startCamera() {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(function(stream) {
                    video.srcObject = stream;
                    video.style.display = 'block';
                    preview.style.display = 'none';
                    resultContainer.style.display = 'none';
                    takePhotoBtn.style.display = 'block';
                })
                .catch(function(error) {
                    console.error('Error accediendo a la cámara:', error);
                    showFileInput();
                });
        } else {
            showFileInput();
        }
    }

    function showFileInput() {
        fileInput.click();
    }

    // Manejar selección de archivo
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                // Ocultar video y botón de foto, mostrar preview
                video.style.display = 'none';
                takePhotoBtn.style.display = 'none';
                previewImg.src = e.target.result;
                preview.style.display = 'block';
                btn.style.display = 'block';
                btn.disabled = false;
                resultContainer.style.display = 'none';
                shareBtn.style.display = 'none';
            };
            reader.readAsDataURL(file);
        }
    });

    // Funcionalidad de tomar foto
    takePhotoBtn.addEventListener('click', function() {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);
        
        canvas.toBlob(function(blob) {
            const file = new File([blob], 'photo.png', { type: 'image/png' });
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            fileInput.files = dataTransfer.files;
            
            // Ocultar video y botón de foto, mostrar preview
            const photoData = canvas.toDataURL('image/png');
            video.style.display = 'none';
            takePhotoBtn.style.display = 'none';
            previewImg.src = photoData;
            preview.style.display = 'block';
            btn.style.display = 'block';
            btn.disabled = false;
            resultContainer.style.display = 'none';
            shareBtn.style.display = 'none';
        }, 'image/png');
    });

    // Funcionalidad del formulario
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!fileInput.files || fileInput.files.length === 0) {
            alert('Por favor selecciona una imagen primero');
            return;
        }
        
        btn.textContent = 'Procesando...';
        btn.disabled = true;
        
        const formData = new FormData(this);
        try {
            const response = await fetch('/', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            if (result.success) {
                // Ocultar preview y botón de foto, mostrar resultado en el mismo marco
                preview.style.display = 'none';
                takePhotoBtn.style.display = 'none';
                resultImage.src = result.image_path;
                resultContainer.style.display = 'block';
                btn.textContent = 'Compartir';
                btn.disabled = false;
                btn.style.display = 'none';
                shareBtn.style.display = 'block';
                // Mostrar el botón de trailer
                document.getElementById('trailer-btn').style.display = 'block';
            } else {
                alert('Error: ' + (result.error || 'Error desconocido'));
                btn.textContent = 'DESCUBRIR MI AMOR ETERNO';
                btn.disabled = false;
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al procesar la imagen');
            btn.textContent = 'DESCUBRIR MI AMOR ETERNO';
            btn.disabled = false;
        }
    });

    // Compartir usando Web Share API si está disponible
    shareBtn.addEventListener('click', function() {
        if (navigator.canShare && resultImage.src) {
            fetch(resultImage.src)
                .then(res => res.blob())
                .then(blob => {
                    const file = new File([blob], 'fusion_generada.png', { type: blob.type });
                    if (navigator.canShare({ files: [file] })) {
                        navigator.share({
                            files: [file],
                            title: 'Mira nuestra fusión',
                            text: '¡Mira la imagen que generamos juntos!'
                        }).catch(() => {
                            fallbackDownload();
                        });
                    } else {
                        fallbackDownload();
                    }
                })
                .catch(() => {
                    fallbackDownload();
                });
        } else {
            fallbackDownload();
        }
    });

    function fallbackDownload() {
        const link = document.createElement('a');
        link.href = resultImage.src;
        link.download = 'fusion_generada.png';
        link.click();
    }

    // Abrir trailer al hacer click
    document.getElementById('trailer-btn').addEventListener('click', function() {
        window.open('https://www.youtube.com/watch?v=9AlO4Vl6v7U', '_blank');
    });
}); 