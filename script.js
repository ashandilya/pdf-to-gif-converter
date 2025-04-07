// Import config
import config from './config.js';

// Initialize PDF.js worker
console.log("Script loaded, initializing PDF.js...");
try {
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
    console.log("PDF.js worker initialized successfully");
} catch (error) {
    console.error("Error initializing PDF.js:", error);
}

// DOM Elements
console.log("Getting DOM elements...");
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const loading = document.getElementById('loading');
const convertBtn = document.getElementById('convertBtn');
const downloadBtn = document.getElementById('downloadBtn');
const pdfPreview = document.getElementById('pdfPreview');
const gifPreview = document.getElementById('gifPreview');
const frameRateInput = document.getElementById('frameRate');
const qualitySelect = document.getElementById('quality');

// Check if all elements were found
if (!dropZone || !fileInput || !convertBtn || !downloadBtn || !pdfPreview || !gifPreview || !frameRateInput || !qualitySelect || !loading) {
    console.error("Some DOM elements were not found:", {
        dropZone: !!dropZone,
        fileInput: !!fileInput,
        convertBtn: !!convertBtn,
        downloadBtn: !!downloadBtn,
        pdfPreview: !!pdfPreview,
        gifPreview: !!gifPreview,
        frameRateInput: !!frameRateInput,
        qualitySelect: !!qualitySelect,
        loading: !!loading
    });
}

// State variables
let currentPdfFile = null;
let currentGifBlob = null;

// Event Listeners
console.log("Setting up event listeners...");
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    console.log("File dropped:", file ? file.name : "No file");
    if (file && file.type === 'application/pdf') {
        handleFile(file);
    } else {
        alert('Please drop a PDF file.');
    }
});

fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    console.log("File selected:", file ? file.name : "No file");
    if (file && file.type === 'application/pdf') {
        handleFile(file);
    } else {
        alert('Please select a valid PDF file.');
    }
});

convertBtn.addEventListener('click', convertToGif);
downloadBtn.addEventListener('click', downloadGif);

// File handling
async function handleFile(file) {
    try {
        currentPdfFile = file;
        convertBtn.disabled = false;
        downloadBtn.disabled = true;
        currentGifBlob = null;
        gifPreview.innerHTML = '<p class="preview-placeholder">GIF Preview</p>';
        
        // Display PDF preview
        const arrayBuffer = await file.arrayBuffer();
        const pdf = await pdfjsLib.getDocument(arrayBuffer).promise;
        const page = await pdf.getPage(1);
        const viewport = page.getViewport({ scale: 1.0 });
        
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = viewport.width;
        canvas.height = viewport.height;
        
        await page.render({
            canvasContext: context,
            viewport: viewport
        }).promise;
        
        pdfPreview.innerHTML = '';
        pdfPreview.appendChild(canvas);
        
        console.log('PDF preview generated successfully');
    } catch (error) {
        console.error('Error handling PDF file:', error);
        alert('Error loading PDF file. Please try again.');
    }
}

// Convert PDF to GIF using backend
async function convertToGif() {
    if (!currentPdfFile) {
        alert('Please select a PDF file first.');
        return;
    }

    try {
        toggleLoading(true);
        convertBtn.disabled = true;
        
        // Convert PDF file to base64
        const reader = new FileReader();
        const pdfData = await new Promise((resolve, reject) => {
            reader.onload = () => resolve(reader.result);
            reader.onerror = () => reject(reader.error);
            reader.readAsDataURL(currentPdfFile);
        });

        // Send as JSON
        const response = await fetch(`${config.apiUrl}/convert`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                pdfData: pdfData,
                frameRate: parseInt(document.getElementById('frameRate').value),
                quality: document.getElementById('quality').value
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Server error: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || 'Unknown error occurred');
        }
        
        // Convert base64 to blob
        const gifData = atob(result.gif);
        const gifArray = new Uint8Array(gifData.length);
        for (let i = 0; i < gifData.length; i++) {
            gifArray[i] = gifData.charCodeAt(i);
        }
        currentGifBlob = new Blob([gifArray], { type: 'image/gif' });
        
        // Display GIF preview
        const gifUrl = URL.createObjectURL(currentGifBlob);
        const img = document.createElement('img');
        img.src = gifUrl;
        gifPreview.innerHTML = '';
        gifPreview.appendChild(img);
        
        downloadBtn.disabled = false;
        console.log('GIF conversion completed successfully');
    } catch (error) {
        console.error('Error converting to GIF:', error);
        alert('Error converting PDF to GIF: ' + error.message);
    } finally {
        toggleLoading(false);
        convertBtn.disabled = false;
    }
}

// Download the converted GIF
function downloadGif() {
    if (!currentGifBlob) {
        alert('Please convert a PDF to GIF first.');
        return;
    }
    
    const url = URL.createObjectURL(currentGifBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = currentPdfFile.name.replace('.pdf', '.gif');
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Toggle loading indicator
function toggleLoading(show) {
    loading.style.display = show ? 'flex' : 'none';
    dropZone.style.display = show ? 'none' : 'flex';
}

// Check if libraries are loaded
console.log("Checking if libraries are loaded...");
if (typeof pdfjsLib === 'undefined') {
    console.error("PDF.js library not loaded!");
} else {
    console.log("PDF.js library loaded successfully");
}

console.log("Script initialization complete"); 