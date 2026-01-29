const API_BASE_URL = 'http://localhost:5000/api';

const imageInput = document.getElementById('imageInput');
const fileName = document.getElementById('fileName');
const confidenceSlider = document.getElementById('confidenceSlider');
const confidenceValue = document.getElementById('confidenceValue');
const modelSelect = document.getElementById('modelSelect');
const modelInfo = document.getElementById('modelInfo');
const uploadForm = document.getElementById('uploadForm');
const originalImage = document.getElementById('originalImage');
const detectionDetails = document.getElementById('detectionDetails');
const historyList = document.getElementById('historyList');

const totalImagesEl = document.getElementById('totalImages');
const totalAnimalsEl = document.getElementById('totalAnimals');
const totalCatsEl = document.getElementById('totalCats');
const totalDogsEl = document.getElementById('totalDogs');

let currentModal = null;

document.addEventListener('DOMContentLoaded', function() {
    testServerConnection();
    
    confidenceSlider.addEventListener('input', function() {
        confidenceValue.textContent = parseFloat(this.value).toFixed(2);
    });
    
    imageInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            fileName.textContent = file.name;
            
            if (file.size > 10 * 1024 * 1024) {
                alert('File size must be less than 10MB');
                resetFileInput();
                return;
            }
            
            const reader = new FileReader();
            reader.onload = function(e) {
                originalImage.innerHTML = `
                    <div class="image-wrapper">
                        <img src="${e.target.result}" alt="Uploaded Image">
                    </div>
                `;
            };
            reader.readAsDataURL(file);
        } else {
            fileName.textContent = 'No file chosen';
            originalImage.innerHTML = '<i class="fas fa-image"></i><p>Uploaded Image</p>';
        }
    });
    
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        processImage();
    });
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
    
    loadAvailableModels();
    updateStats();
    loadHistory();
});

function resetFileInput() {
    imageInput.value = '';
    fileName.textContent = 'No file chosen';
    originalImage.innerHTML = '<i class="fas fa-image"></i><p>Uploaded Image</p>';
}

async function loadAvailableModels() {
    try {
        const response = await fetch(`${API_BASE_URL}/models`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        
        if (data.success && data.models.length > 0) {
            modelSelect.innerHTML = '';
            
            data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                modelSelect.appendChild(option);
            });
            
            modelInfo.textContent = `Found ${data.models.length} model(s) available`;
            
            if (data.models.includes('best.pt')) {
                modelSelect.value = 'best.pt';
            }
        } else {
            modelSelect.innerHTML = '<option value="">No models found</option>';
            modelInfo.textContent = 'No model files found in models folder. Please add .pt files.';
        }
    } catch (error) {
        console.error('Error loading models:', error);
        modelSelect.innerHTML = '<option value="">Error loading models</option>';
        modelInfo.textContent = 'Error loading models. Check server connection.';
    }
}

async function testServerConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/test`);
        if (response.ok) {
            console.log('Server connection OK');
        }
    } catch (error) {
        console.error('Server connection error:', error);
    }
}

async function processImage() {
    const file = imageInput.files[0];
    const confidence = confidenceSlider.value;
    const model = modelSelect.value;
    
    if (!file) {
        alert('Please select an image file');
        return;
    }
    
    if (!model) {
        alert('Please select a model');
        return;
    }
    
    const processBtn = document.querySelector('.process-btn');
    const originalBtnText = processBtn.innerHTML;
    processBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    processBtn.disabled = true;
    
    try {
        const formData = new FormData();
        formData.append('image', file);
        formData.append('confidence', confidence);
        formData.append('model', model);
        
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            showDetectionInfo(data);
            await updateStats();
            await loadHistory();
            showNotification('Detection completed successfully!', 'success');
        } else {
            throw new Error(data.error || 'Unknown server error');
        }
        
    } catch (error) {
        console.error('Processing error:', error);
        detectionDetails.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle fa-3x"></i>
                <p>Error processing image</p>
                <p class="error-detail">${error.message}</p>
            </div>
        `;
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        processBtn.innerHTML = originalBtnText;
        processBtn.disabled = false;
    }
}

function showDetectionInfo(data) {
    let html = `
        <div class="info-grid">
            <div class="info-item">
                <label>Model Used:</label>
                <span>${data.model_name}</span>
            </div>
            <div class="info-item">
                <label>Processing Time:</label>
                <span>${data.processing_time} seconds</span>
            </div>
            <div class="info-item">
                <label>Confidence:</label>
                <span>${data.confidence}</span>
            </div>
            <div class="info-item highlight">
                <label>Total Animals:</label>
                <span>${data.stats.total_animals}</span>
            </div>
            <div class="info-item">
                <label>Cats:</label>
                <span class="cat-count">${data.stats.cats}</span>
            </div>
            <div class="info-item">
                <label>Dogs:</label>
                <span class="dog-count">${data.stats.dogs}</span>
            </div>
        </div>
    `;
    
    if (data.detections && data.detections.length > 0) {
        html += '<h4>Detections:</h4><div class="detections-list">';
        data.detections.forEach((detection, index) => {
            const confidencePercent = (detection.confidence * 100).toFixed(1);
            html += `
                <div class="detection-item">
                    <span class="detection-number">${index + 1}.</span>
                    <span class="detection-class ${detection.class}">${detection.class}</span>
                    <span class="detection-confidence">${confidencePercent}%</span>
                </div>
            `;
        });
        html += '</div>';
    } else {
        html += `
            <div class="no-detections">
                <i class="fas fa-search"></i>
                <p>No animals detected</p>
                <p class="hint">Try lowering the confidence threshold or using a different model</p>
            </div>
        `;
    }
    
    detectionDetails.innerHTML = html;
}

async function updateStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        
        totalImagesEl.textContent = data.total_images || 0;
        totalAnimalsEl.textContent = data.total_animals || 0;
        totalCatsEl.textContent = data.total_cats || 0;
        totalDogsEl.textContent = data.total_dogs || 0;
        
    } catch (error) {
        console.error('Error fetching stats:', error);
        totalImagesEl.textContent = '0';
        totalAnimalsEl.textContent = '0';
        totalCatsEl.textContent = '0';
        totalDogsEl.textContent = '0';
    }
}

async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/history`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        let html = '';
        
        if (!data || data.length === 0) {
            html = `
                <div class="empty-history">
                    <i class="fas fa-history fa-3x"></i>
                    <p>No detection history yet</p>
                    <p>Upload an image to get started!</p>
                </div>
            `;
        } else {
            data.forEach(item => {
                const date = new Date(item.upload_time);
                const formattedDate = date.toLocaleString();
                
                html += `
                    <div class="history-item" onclick="showHistoryDetails(${item.id})">
                        <div class="history-content">
                            <div class="history-thumbnail">
                                ${item.result_filename ? 
                                    `<img src="http://localhost:5000/results/${item.result_filename}" 
                                          alt="Detection Result" class="thumbnail-image">` :
                                    `<div class="thumbnail-placeholder">
                                        <i class="fas fa-image"></i>
                                    </div>`
                                }
                            </div>
                            <div class="history-info">
                                <h4>${item.filename}</h4>
                                <div class="model-badge">${item.model_name}</div>
                                <p><i class="far fa-calendar"></i> ${formattedDate}</p>
                                <div class="history-stats">
                                    <span class="stat-badge total">${item.total_animals} animals</span>
                                    <span class="stat-badge cats">${item.cats_count} cats</span>
                                    <span class="stat-badge dogs">${item.dogs_count} dogs</span>
                                </div>
                                <p><i class="far fa-clock"></i> Processing time: ${item.processing_time}s</p>
                                <p><i class="fas fa-filter"></i> Confidence: ${item.confidence}</p>
                                <button class="pdf-report-btn" onclick="event.stopPropagation(); exportSinglePDF(${item.id})">
                                    <i class="fas fa-file-pdf"></i> Get PDF Report
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            });
        }
        
        historyList.innerHTML = html;
        
    } catch (error) {
        console.error('Error loading history:', error);
        historyList.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle fa-2x"></i>
                <p>Failed to load history</p>
                <p class="error-detail">${error.message}</p>
                <button onclick="loadHistory()" class="retry-btn">
                    <i class="fas fa-redo"></i> Retry
                </button>
            </div>
        `;
    }
}

async function showHistoryDetails(historyId) {
    try {
        const response = await fetch(`${API_BASE_URL}/history/${historyId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const item = await response.json();
        const date = new Date(item.upload_time);
        const formattedDate = date.toLocaleString();
        
        let modalContent = `
            <div class="detection-details-content">
                <button class="close-modal" onclick="closeModal()">&times;</button>
                <h2><i class="fas fa-info-circle"></i> Detection Details</h2>
                
                ${item.result_filename ? `
                    <img src="http://localhost:5000/results/${item.result_filename}" 
                         alt="Detection Result" class="modal-image">
                ` : '<p class="no-detections">No result image available</p>'}
                
                <div class="modal-stats">
                    <div class="modal-stat-item">
                        <span class="modal-stat-label">File Name</span>
                        <span class="modal-stat-value">${item.filename}</span>
                    </div>
                    <div class="modal-stat-item">
                        <span class="modal-stat-label">Model Used</span>
                        <span class="modal-stat-value">${item.model_name}</span>
                    </div>
                    <div class="modal-stat-item">
                        <span class="modal-stat-label">Upload Time</span>
                        <span class="modal-stat-value">${formattedDate}</span>
                    </div>
                    <div class="modal-stat-item highlight">
                        <span class="modal-stat-label">Total Animals</span>
                        <span class="modal-stat-value">${item.total_animals}</span>
                    </div>
                    <div class="modal-stat-item">
                        <span class="modal-stat-label">Processing Time</span>
                        <span class="modal-stat-value">${item.processing_time}s</span>
                    </div>
                    <div class="modal-stat-item">
                        <span class="modal-stat-label">Cats Detected</span>
                        <span class="modal-stat-value cat-count">${item.cats_count}</span>
                    </div>
                    <div class="modal-stat-item">
                        <span class="modal-stat-label">Dogs Detected</span>
                        <span class="modal-stat-value dog-count">${item.dogs_count}</span>
                    </div>
                    <div class="modal-stat-item">
                        <span class="modal-stat-label">Confidence Threshold</span>
                        <span class="modal-stat-value">${item.confidence}</span>
                    </div>
                </div>
        `;
        
        if (item.detections && item.detections.length > 0) {
            modalContent += `
                <h3>Individual Detections (${item.detections.length})</h3>
                <div class="modal-detections-list">
            `;
            
            item.detections.forEach((detection, index) => {
                const confidencePercent = (detection.confidence * 100).toFixed(1);
                modalContent += `
                    <div class="modal-detection-item">
                        <span class="detection-number">${index + 1}.</span>
                        <span class="modal-detection-class ${detection.class}">${detection.class}</span>
                        <span class="modal-detection-confidence">${confidencePercent}% confidence</span>
                    </div>
                `;
            });
            
            modalContent += '</div>';
        } else {
            modalContent += `
                <div class="no-detections">
                    <i class="fas fa-search"></i>
                    <p>No animals were detected in this image</p>
                </div>
            `;
        }
        
        modalContent += `
            <div class="modal-actions">
                <button class="modal-pdf-btn" onclick="exportSinglePDF(${item.id})">
                    <i class="fas fa-file-pdf"></i> Download PDF Report
                </button>
            </div>
        `;
        
        modalContent += '</div>';
        
        let modal = document.getElementById('detectionDetailsModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'detectionDetailsModal';
            modal.className = 'detection-details-modal';
            document.body.appendChild(modal);
        }
        
        modal.innerHTML = modalContent;
        modal.style.display = 'flex';
        currentModal = modal;
        
    } catch (error) {
        console.error('Error loading history details:', error);
        alert(`Error loading details: ${error.message}`);
    }
}

function closeModal() {
    const modal = document.getElementById('detectionDetailsModal');
    if (modal) {
        modal.style.display = 'none';
        currentModal = null;
    }
}

function exportFullPDF() {
    window.open(`${API_BASE_URL}/export/pdf`, '_blank');
}

function exportSinglePDF(id) {
    window.open(`${API_BASE_URL}/export/pdf/${id}`, '_blank');
}

async function clearHistory() {
    if (!confirm('Are you sure you want to clear all history?\nThis will delete all records and uploaded images.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/clear`, {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        
        if (data.success) {
            detectionDetails.innerHTML = '<p>Upload an image to start detection</p>';
            await updateStats();
            await loadHistory();
            showNotification('History cleared successfully', 'success');
        } else {
            throw new Error(data.error || 'Clear failed');
        }
        
    } catch (error) {
        console.error('Error clearing history:', error);
        showNotification(`Error: ${error.message}`, 'error');
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

const notificationStyles = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        background: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        gap: 12px;
        z-index: 1000;
        animation: slideIn 0.3s ease;
        max-width: 400px;
    }
    
    .notification.success {
        border-left: 4px solid #38a169;
    }
    
    .notification.error {
        border-left: 4px solid #e53e3e;
    }
    
    .notification.info {
        border-left: 4px solid #4299e1;
    }
    
    .notification i {
        font-size: 1.2em;
    }
    
    .notification.success i {
        color: #38a169;
    }
    
    .notification.error i {
        color: #e53e3e;
    }
    
    .notification button {
        background: none;
        border: none;
        color: #718096;
        cursor: pointer;
        padding: 5px;
        margin-left: auto;
    }
    
    .notification button:hover {
        color: #4a5568;
    }
    
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;

const styleSheet = document.createElement("style");
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);