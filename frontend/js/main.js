const API_BASE_URL = 'http://localhost:5000/api';

const imageInput = document.getElementById('imageInput');
const fileName = document.getElementById('fileName');
const confidenceSlider = document.getElementById('confidenceSlider');
const confidenceValue = document.getElementById('confidenceValue');
const uploadForm = document.getElementById('uploadForm');
const originalImage = document.getElementById('originalImage');
const resultImage = document.getElementById('resultImage');
const detectionDetails = document.getElementById('detectionDetails');
const historyList = document.getElementById('historyList');

const totalImagesEl = document.getElementById('totalImages');
const totalAnimalsEl = document.getElementById('totalAnimals');
const totalCatsEl = document.getElementById('totalCats');
const totalDogsEl = document.getElementById('totalDogs');

document.addEventListener('DOMContentLoaded', function() {
    updateStats();
    loadHistory();
    
    confidenceSlider.addEventListener('input', function() {
        confidenceValue.textContent = this.value;
    });
    
    imageInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            fileName.textContent = file.name;
            
            const reader = new FileReader();
            reader.onload = function(e) {
                originalImage.innerHTML = `<img src="${e.target.result}" alt="Uploaded Image">`;
            };
            reader.readAsDataURL(file);
        } else {
            fileName.textContent = 'No file chosen';
        }
    });
    
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        processImage();
    });
});

async function processImage() {
    const file = imageInput.files[0];
    const confidence = confidenceSlider.value;
    
    if (!file) {
        alert('Please select an image file');
        return;
    }
    
    const formData = new FormData();
    formData.append('image', file);
    formData.append('confidence', confidence);
    
    const processBtn = document.querySelector('.process-btn');
    const originalText = processBtn.innerHTML;
    processBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    processBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            resultImage.innerHTML = `<img src="${data.result_image}" alt="Detection Result">`;
            
            showDetectionInfo(data);
            
            updateStats();
            loadHistory();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Server error: ' + error.message);
    } finally {
        processBtn.innerHTML = originalText;
        processBtn.disabled = false;
    }
}

function showDetectionInfo(data) {
    let html = `
        <div class="info-grid">
            <div class="info-item">
                <label>File:</label>
                <span>${data.filename}</span>
            </div>
            <div class="info-item">
                <label>Processing Time:</label>
                <span>${data.processing_time} sec</span>
            </div>
            <div class="info-item">
                <label>Total Animals:</label>
                <span>${data.stats.total_animals}</span>
            </div>
            <div class="info-item">
                <label>Cats:</label>
                                <span>${data.stats.cats}</span>
            </div>
            <div class="info-item">
                <label>Dogs:</label>
                <span>${data.stats.dogs}</span>
            </div>
            <div class="info-item">
                <label>Confidence:</label>
                <span>${confidenceSlider.value}</span>
            </div>
        </div>
    `;
    
    if (data.detections.length > 0) {
        html += '<h4>Detected Objects:</h4><ul>';
        data.detections.forEach(detection => {
            html += `
                <li>
                    ${detection.class} (confidence: ${detection.confidence})
                </li>
            `;
        });
        html += '</ul>';
    }
    
    detectionDetails.innerHTML = html;
}

async function updateStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        const data = await response.json();
        
        totalImagesEl.textContent = data.total_images;
        totalAnimalsEl.textContent = data.total_animals;
        totalCatsEl.textContent = data.total_cats;
        totalDogsEl.textContent = data.total_dogs;
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/history`);
        const data = await response.json();
        
        let html = '';
        if (data.length === 0) {
            html = '<p>No history yet</p>';
        } else {
            data.forEach(item => {
                const date = new Date(item.upload_time);
                html += `
                    <div class="history-item">
                        <div class="history-info">
                            <h4>${item.filename}</h4>
                            <p>${date.toLocaleString()}</p>
                            <p>Animals: ${item.total_animals} (Cats: ${item.cats_count}, Dogs: ${item.dogs_count})</p>
                        </div>
                    </div>
                `;
            });
        }
        historyList.innerHTML = html;
    } catch (error) {
        console.error('Error fetching history:', error);
        historyList.innerHTML = '<p>Error loading history</p>';
    }
}

function exportExcel() {
    window.location.href = `${API_BASE_URL}/export/excel`;
}

async function clearHistory() {
    if (confirm('Are you sure you want to clear all history?')) {
        try {
            const response = await fetch(`${API_BASE_URL}/clear`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                loadHistory();
                updateStats();
                alert('History cleared successfully');
            } else {
                alert('Error: ' + data.error);
            }
        } catch (error) {
            alert('Server error: ' + error.message);
        }
    }
}