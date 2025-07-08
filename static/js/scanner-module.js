/**
 * Universal Scanner Module - LOCAL SCANNING ONLY
 * Handles QR Code and ISBN barcode scanning functionality
 * Can be used across multiple pages in the library management system
 * 
 * ⚠️ IMPORTANT: This module performs LOCAL-ONLY scanning.
 * NO server API calls are made for code detection.
 * All scanning is done in the browser using:
 * - BarcodeDetector API (for QR codes)
 * - QuaggaJS library (for ISBN barcodes)
 * 
 * VERSION: 2.0.3-FULL-API (Updated: 2025-07-07)
 * CACHE BUSTER: 20250707-104500
 */

// Immediately log that this is the correct FULL-API version
console.log('🚀 [MODULE LOADED] UniversalScanner v2.0.3-FULL-API loaded');
console.log('✅ [API ENABLED] This module makes API calls for book lookup');
console.log('📅 [CACHE CHECK] Cache buster: 20250707-104500');

class UniversalScanner {
    constructor(options = {}) {
        console.log('🔧 [API SCANNER] Initializing scanner module with API support');
        console.log('✅ [API ENABLED] This scanner makes API calls for book lookup');
        
        // Configuration options
        this.options = {
            scanInterval: options.scanInterval || 3000, // 3 seconds default
            autoStop: options.autoStop !== false, // Auto stop after detection (default: true)
            showStatus: options.showStatus !== false, // Show scanning status (default: true)
            apiBaseUrl: options.apiBaseUrl || '/api', // Not used for scanning, only for legacy compatibility
            ...options
        };

        // State management
        this.currentStream = null;
        this.scanningInterval = null;
        this.isScanning = false;
        this.isScannerActive = false;
        this.callbacks = {
            onResults: options.onResults || this.defaultResultHandler.bind(this),
            onError: options.onError || this.defaultErrorHandler.bind(this),
            onScanStart: options.onScanStart || (() => {}),
            onScanStop: options.onScanStop || (() => {})
        };

        // DOM elements (will be set when initializing)
        this.elements = {};
    }

    /**
     * Initialize the scanner with DOM elements
     * @param {Object} elements - Object containing DOM element selectors or elements
     */
    init(elements) {
        this.elements = {
            preview: this.getElement(elements.preview),
            toggleBtn: this.getElement(elements.toggleBtn),
            uploadInput: this.getElement(elements.uploadInput),
            statusDiv: this.getElement(elements.statusDiv),
            resultsDiv: this.getElement(elements.resultsDiv)
        };

        // Bind events
        this.bindEvents();
    }

    /**
     * Helper to get DOM element
     */
    getElement(selector) {
        if (typeof selector === 'string') {
            // Add # prefix if it looks like an ID selector without it
            if (!selector.startsWith('#') && !selector.startsWith('.') && !selector.includes(' ')) {
                selector = '#' + selector;
            }
            return document.querySelector(selector);
        }
        return selector; // Already an element
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        if (this.elements.toggleBtn) {
            this.elements.toggleBtn.addEventListener('click', () => this.toggle());
        }

        if (this.elements.uploadInput) {
            this.elements.uploadInput.addEventListener('change', (e) => {
                if (e.target.files[0]) {
                    this.scanImage(e.target.files[0], false);
                }
            });
        }
    }

    /**
     * Toggle scanner on/off
     */
    toggle() {
        if (this.isScannerActive) {
            this.stop();
        } else {
            this.start();
        }
    }

    /**
     * Start the camera scanner
     */
    async start() {
        try {
            // Stop existing stream
            if (this.currentStream) {
                this.currentStream.getTracks().forEach(track => track.stop());
            }

            // Get user media
            this.currentStream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: 'environment',
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            });

            // Create video element
            const video = document.createElement('video');
            video.srcObject = this.currentStream;
            video.autoplay = true;
            video.playsInline = true;
            video.muted = true; // Prevent audio feedback
            video.style.width = '100%';
            video.style.height = '100%';
            video.style.objectFit = 'cover';

            // Update preview
            if (this.elements.preview) {
                this.elements.preview.innerHTML = '';
                this.elements.preview.appendChild(video);
                this.addScanningOverlay();
            }

            // Update button state
            this.updateToggleButton(true);
            this.isScannerActive = true;

            // Start automatic scanning
            this.startAutomaticScanning(video);

            // Callback
            this.callbacks.onScanStart();

        } catch (error) {
            console.error('Error accessing camera:', error);
            this.callbacks.onError('Unable to access camera. Please ensure camera permissions are granted.');
        }
    }

    /**
     * Stop the camera scanner
     */
    stop() {
        if (this.currentStream) {
            this.currentStream.getTracks().forEach(track => track.stop());
            this.currentStream = null;
        }

        this.stopAutomaticScanning();
        this.isScanning = false;
        this.isScannerActive = false;

        // Reset preview
        if (this.elements.preview) {
            this.resetPreview();
        }

        // Update button state
        this.updateToggleButton(false);

        // Clear results
        if (this.elements.resultsDiv) {
            this.elements.resultsDiv.innerHTML = '';
        }

        // Callback
        this.callbacks.onScanStop();
    }

    /**
     * Add scanning overlay to video
     */
    addScanningOverlay() {
        const overlay = document.createElement('div');
        overlay.className = 'scanning-overlay';
        overlay.innerHTML = `
            <div class="scan-frame">
                <div class="scan-line"></div>
            </div>
            <div class="scan-controls">
                <p class="scan-text">Position code within the frame</p>
            </div>
        `;
        this.elements.preview.appendChild(overlay);
    }

    /**
     * Reset preview to initial state
     */
    resetPreview() {
        this.elements.preview.innerHTML = `
            <div class="text-center text-muted">
                <i class="fas fa-camera fa-3x"></i>
                <p class="mt-2">Scanner will appear here</p>
                <small>The scanner will automatically detect QR codes and ISBN barcodes</small>
            </div>
        `;
    }

    /**
     * Update toggle button appearance
     */
    updateToggleButton(isActive) {
        if (!this.elements.toggleBtn) return;

        if (isActive) {
            this.elements.toggleBtn.innerHTML = '<i class="fas fa-stop me-2"></i>Stop Scanner';
            this.elements.toggleBtn.className = this.elements.toggleBtn.className.replace('btn-primary', 'btn-danger');
        } else {
            this.elements.toggleBtn.innerHTML = '<i class="fas fa-camera me-2"></i>Start Scanner';
            this.elements.toggleBtn.className = this.elements.toggleBtn.className.replace('btn-danger', 'btn-primary');
        }
    }

    /**
     * Start automatic scanning
     */
    startAutomaticScanning(video) {
        const startScanning = () => {
            this.scanningInterval = setInterval(() => {
                if (!this.isScanning) {
                    this.captureAndScan(video);
                }
            }, this.options.scanInterval);
        };

        // Check if video metadata is already loaded
        if (video.readyState >= video.HAVE_METADATA) {
            // Metadata already loaded, start scanning immediately
            startScanning();
        } else {
            // Wait for metadata to load
            video.addEventListener('loadedmetadata', startScanning, { once: true });
        }
    }

    /**
     * Stop automatic scanning
     */
    stopAutomaticScanning() {
        if (this.scanningInterval) {
            clearInterval(this.scanningInterval);
            this.scanningInterval = null;
        }
    }

    /**
     * Capture image from video and scan locally
     */
    async captureAndScan(video) {
        if (this.isScanning) return;

        this.isScanning = true;
        
        console.log('🔍 [LOCAL SCANNER] Starting local-only scan - NO SERVER CALLS');

        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);

        console.log('🔍 [LOCAL SCANNER] Captured frame for scanning:', canvas.width, 'x', canvas.height);

        // Scan directly from canvas - no need to convert to blob/file
        try {
            // Scan locally for both QR and barcodes - NO SERVER CALLS
            console.log('🔍 [LOCAL SCANNER] Scanning for QR and ISBN locally...');
            const [qrResults, barcodeResults] = await Promise.allSettled([
                this.scanImageForQRLocal(canvas),
                this.scanImageForBarcodeLocal(canvas)
            ]);

            let foundResults = false;
            let results = [];

            // Process QR results
            if (qrResults.status === 'fulfilled' && qrResults.value.success) {
                console.log('✅ [LOCAL QR] QR detection successful');
                // Check for books first
                if (qrResults.value.books && qrResults.value.books.length > 0) {
                    results.push({
                        type: 'QR Code',
                        books: qrResults.value.books
                    });
                    foundResults = true;
                } 
                // Check for members
                else if (qrResults.value.members && qrResults.value.members.length > 0) {
                    results.push({
                        type: 'QR Code',
                        members: qrResults.value.members
                    });
                    foundResults = true;
                } 
                else if (qrResults.value.rawData) {
                    // QR detected but no book/member info - only show if it's meaningful data
                    console.log('📱 [LOCAL QR] QR Code detected but no book/member info:', qrResults.value.rawData);
                }
            } else {
                console.log('❌ [LOCAL QR] QR detection failed or no QR found');
            }

            // Process barcode results (ISBN)
            if (barcodeResults.status === 'fulfilled' && barcodeResults.value.success) {
                console.log('✅ [LOCAL ISBN] ISBN detection successful');
                if (barcodeResults.value.books && barcodeResults.value.books.length > 0) {
                    results.push({
                        type: 'ISBN Barcode',
                        books: barcodeResults.value.books
                    });
                    foundResults = true;
                } else if (barcodeResults.value.isbn) {
                    // Just detected ISBN, fetch book info (LOCAL ONLY)
                    console.log('📚 [LOCAL ISBN] ISBN detected, creating local book info:', barcodeResults.value.isbn);
                    const bookInfo = await this.fetchBookInfoByISBN(barcodeResults.value.isbn);
                    if (bookInfo) {
                        results.push({
                            type: 'ISBN Barcode',
                            books: [bookInfo]
                        });
                        foundResults = true;
                    }
                }
            } else {
                console.log('❌ [LOCAL ISBN] ISBN detection failed or no ISBN found');
            }

            // Handle results
            if (foundResults) {
                console.log('🎉 [LOCAL RESULTS] Found results, triggering callback (NO SERVER CALLS):', results);
                this.callbacks.onResults(results, true);
                
                if (this.options.autoStop) {
                    this.stopAutomaticScanning();
                    this.showCodeFoundMessage();
                }
            } else {
                console.log('🔍 [LOCAL SCANNER] No meaningful results found in this scan');
                // Only show "no results" message every 10th scan to avoid spam
                if (!this.scanCount) this.scanCount = 0;
                this.scanCount++;
                
                if (this.scanCount % 10 === 0) {
                    // Show helpful message after several failed scans
                    if (this.elements.resultsDiv) {
                        this.elements.resultsDiv.innerHTML = `
                            <div class="alert alert-info">
                                <i class="fas fa-search me-2"></i>
                                <strong>Still scanning...</strong> 
                                ${this.scanCount} attempts so far.
                                <div class="mt-2 small">
                                    <strong>💡 Tips:</strong>
                                    <ul class="mb-0">
                                        <li>Hold the ISBN barcode steady in good lighting</li>
                                        <li>Try uploading a clear photo instead</li>
                                        <li>Use "Manual ISBN Entry" if scanning fails</li>
                                    </ul>
                                </div>
                            </div>
                        `;
                    }
                }
            }

        } catch (error) {
            console.error('Error scanning live video:', error);
        } finally {
            this.isScanning = false;
        }
    }

    /**
     * Scan image for QR codes and ISBN barcodes locally
     */
    async scanImage(file, isAutomatic = false) {
        if (!isAutomatic && this.options.showStatus && this.elements.statusDiv) {
            this.elements.statusDiv.style.display = 'block';
        }

        try {
            // Create image element for local scanning
            const img = new Image();
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            const imageUrl = URL.createObjectURL(file);
            
            return new Promise((resolve) => {
                img.onload = async () => {
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);
                    
                    // Scan locally for both QR and barcodes
                    const [qrResults, barcodeResults] = await Promise.allSettled([
                        this.scanImageForQRLocal(canvas),
                        this.scanImageForBarcodeLocal(canvas)
                    ]);

                    let foundResults = false;
                    let results = [];

                    // Process QR results
                    if (qrResults.status === 'fulfilled' && qrResults.value.success) {
                        results.push({
                            type: 'QR Code',
                            books: qrResults.value.books
                        });
                        foundResults = true;
                    }

                    // Process barcode results (ISBN)
                    if (barcodeResults.status === 'fulfilled' && barcodeResults.value.success) {
                        if (barcodeResults.value.books && barcodeResults.value.books.length > 0) {
                            results.push({
                                type: 'ISBN Barcode',
                                books: barcodeResults.value.books
                            });
                            foundResults = true;
                        } else if (barcodeResults.value.isbn) {
                            // Just detected ISBN, need to fetch book info
                            const bookInfo = await this.fetchBookInfoByISBN(barcodeResults.value.isbn);
                            if (bookInfo) {
                                results.push({
                                    type: 'ISBN Barcode',
                                    books: [bookInfo]
                                });
                                foundResults = true;
                            }
                        }
                    }

                    URL.revokeObjectURL(imageUrl);

                    // Handle results
                    if (foundResults) {
                        this.callbacks.onResults(results, isAutomatic);
                        
                        if (this.options.autoStop && isAutomatic) {
                            this.stopAutomaticScanning();
                            this.showCodeFoundMessage();
                        }
                    } else if (!isAutomatic) {
                        this.callbacks.onResults([], isAutomatic);
                    }

                    resolve({ success: foundResults, results });
                };

                img.onerror = () => {
                    URL.revokeObjectURL(imageUrl);
                    if (!isAutomatic) {
                        this.callbacks.onError('Failed to load image');
                    }
                    resolve({ success: false, results: [] });
                };

                img.src = imageUrl;
            });

        } catch (error) {
            console.error('Error scanning image:', error);
            if (!isAutomatic) {
                this.callbacks.onError('Error scanning image for codes');
            }
        } finally {
            if (!isAutomatic && this.options.showStatus && this.elements.statusDiv) {
                this.elements.statusDiv.style.display = 'none';
            }
            this.isScanning = false;
        }
    }

    /**
     * Scan canvas for QR codes locally using built-in methods first, fallback to server
     */
    async scanImageForQRLocal(canvas) {
        try {
            // First try to detect QR using built-in BarcodeDetector API if available
            if ('BarcodeDetector' in window) {
                try {
                    const barcodeDetector = new BarcodeDetector({ formats: ['qr_code'] });
                    const barcodes = await barcodeDetector.detect(canvas);
                    
                    if (barcodes.length > 0) {
                        const qrData = barcodes[0].rawValue;
                        console.log('QR Code detected locally:', qrData);
                        
                        // Parse QR code data to extract book information
                        try {
                            const data = JSON.parse(qrData);
                            
                            if (data.type === 'library_book' && data.uuid) {
                                // Look up book by UUID
                                const bookInfo = await this.fetchBookByUUID(data.uuid);
                                if (bookInfo) {
                                    return {
                                        success: true,
                                        books: [bookInfo]
                                    };
                                }
                            }
                        } catch (e) {
                            // If not JSON, treat as plain text
                            console.log('QR Code contains non-JSON text:', qrData);
                        }
                        
                        return {
                            success: true,
                            books: [],
                            rawData: qrData
                        };
                    } else {
                        // No QR codes detected
                        return { success: false };
                    }
                } catch (detectorError) {
                    console.log('ℹ️ [QR] BarcodeDetector failed (trying ZXing fallback):', detectorError);
                    return { success: false };
                }
            } else {
                console.log('ℹ️ [QR] BarcodeDetector not available (normal), using ZXing fallback...');
                
                // Try ZXing-js as fallback for QR codes
                if (typeof ZXing !== 'undefined' && ZXing.BrowserMultiFormatReader) {
                    try {
                        console.log('🔍 [ZXING-QR] Attempting ZXing QR detection...');
                        const codeReader = new ZXing.BrowserMultiFormatReader();
                        
                        // Convert canvas to image for ZXing
                        const imageData = canvas.toDataURL();
                        const img = new Image();
                        
                        const zxingResult = await new Promise((resolve, reject) => {
                            img.onload = async () => {
                                try {
                                    const result = await codeReader.decodeFromImageElement(img);
                                    resolve(result);
                                } catch (error) {
                                    reject(error);
                                }
                            };
                            img.onerror = reject;
                            img.src = imageData;
                        });
                        
                        if (zxingResult && zxingResult.text) {
                            const qrData = zxingResult.text;
                            console.log('✅ [ZXING-QR] QR Code detected:', qrData);
                            
                            // Parse QR code data to extract book or member information
                            try {
                                const data = JSON.parse(qrData);
                                
                                if (data.type === 'library_book' && data.uuid) {
                                    // Look up book by UUID
                                    const bookInfo = await this.fetchBookByUUID(data.uuid);
                                    if (bookInfo) {
                                        return {
                                            success: true,
                                            books: [bookInfo]
                                        };
                                    }
                                } else if (data.type === 'library_member' && data.employee_code) {
                                    // Look up member by employee code
                                    const memberInfo = await this.fetchMemberByEmployeeCode(data.employee_code);
                                    if (memberInfo) {
                                        return {
                                            success: true,
                                            members: [memberInfo]
                                        };
                                    }
                                }
                            } catch (e) {
                                // If not JSON, treat as plain text and try member lookup
                                console.log('QR Code contains non-JSON text, trying member lookup:', qrData);
                                
                                // Try to find member by employee code or member ID
                                const memberInfo = await this.fetchMemberByCode(qrData);
                                if (memberInfo) {
                                    return {
                                        success: true,
                                        members: [memberInfo]
                                    };
                                }
                            }
                            
                            return {
                                success: true,
                                books: [],
                                rawData: qrData
                            };
                        } else {
                            console.log('❌ [ZXING-QR] No QR codes detected with ZXing');
                            return { success: false };
                        }
                        
                    } catch (zxingError) {
                        console.log('❌ [ZXING-QR] ZXing QR detection failed:', zxingError.message);
                        return { success: false };
                    }
                } else {
                    console.log('⚠️ [ZXING-QR] ZXing library not available for QR fallback');
                    return { success: false };
                }
            }
            
        } catch (error) {
            console.error('Error scanning QR code locally:', error);
            return { success: false };
        }
    }

    /**
     * Scan canvas for barcodes locally using built-in methods first, fallback to server
     */
    /**
     * Scan canvas for barcodes locally using native BarcodeDetector API
     */
    async scanImageForBarcodeLocal(canvas) {
        try {
            // Use native BarcodeDetector API (Chrome/Edge) - prioritize this as it's more reliable
            if ('BarcodeDetector' in window) {
                console.log('🔍 [DETECTOR] Using native BarcodeDetector for ISBN detection...');
                try {
                    const barcodeDetector = new BarcodeDetector({ 
                        formats: ['ean_13', 'ean_8', 'code_128', 'code_39', 'code_93'] 
                    });
                    
                    console.log('🔍 [DETECTOR] Scanning canvas:', canvas.width, 'x', canvas.height);
                    const barcodes = await barcodeDetector.detect(canvas);
                    
                    console.log('🔍 [DETECTOR] Detected', barcodes.length, 'barcode(s)');
                    
                    if (barcodes.length > 0) {
                        for (const barcode of barcodes) {
                            const rawValue = barcode.rawValue;
                            const format = barcode.format;
                            
                            console.log('✅ [DETECTOR] Barcode found:', {
                                value: rawValue,
                                format: format,
                                boundingBox: barcode.boundingBox
                            });
                            
                            // Use ISBNUtils for better validation
                            if (window.ISBNUtils && window.ISBNUtils.looksLikeIsbn(rawValue)) {
                                const isbn = window.ISBNUtils.extractIsbn(rawValue);
                                if (isbn) {
                                    console.log('✅ [DETECTOR] Valid ISBN detected:', isbn);
                                    return {
                                        success: true,
                                        isbn: isbn,
                                        books: []
                                    };
                                }
                            }
                            
                            // Fallback pattern validation
                            const cleanCode = rawValue.replace(/[^0-9X]/gi, '');
                            if (this.isValidISBNPattern(cleanCode)) {
                                console.log('✅ [DETECTOR] ISBN pattern validated:', cleanCode);
                                return {
                                    success: true,
                                    isbn: cleanCode,
                                    books: []
                                };
                            }
                            
                            console.log('⚠️ [DETECTOR] Code detected but not valid ISBN:', rawValue);
                        }
                        
                        console.log('⚠️ [DETECTOR] Found barcodes but none were valid ISBNs');
                    } else {
                        console.log('❌ [DETECTOR] No barcodes detected in image');
                    }
                } catch (detectorError) {
                    console.log('❌ [DETECTOR] BarcodeDetector failed:', detectorError.message);
                }
            } else {
                console.log('ℹ️ [DETECTOR] BarcodeDetector not available (this is normal in Chrome)');
                console.log('💡 [DETECTOR] Using ZXing fallback for excellent scanning support');
            }

            // Try ZXing-js as fallback if available
            if (typeof ZXing !== 'undefined' && ZXing.BrowserMultiFormatReader) {
                console.log('🔍 [ZXING] Trying ZXing-js fallback for ISBN detection...');
                
                try {
                    const codeReader = new ZXing.BrowserMultiFormatReader();
                    
                    // Convert canvas to image for ZXing
                    const img = new Image();
                    const dataUrl = canvas.toDataURL();
                    
                    const result = await new Promise((resolve, reject) => {
                        img.onload = async () => {
                            try {
                                const zxingResult = await codeReader.decodeFromImageElement(img);
                                resolve(zxingResult);
                            } catch (error) {
                                reject(error);
                            }
                        };
                        img.onerror = reject;
                        img.src = dataUrl;
                    });
                    
                    if (result && result.getText()) {
                        const detectedCode = result.getText();
                        console.log('✅ [ZXING] ZXing detected code:', detectedCode);
                        
                        // Validate as ISBN
                        const validatedISBN = this.validateDetectedISBN(detectedCode);
                        if (validatedISBN) {
                            console.log('✅ [ZXING] Valid ISBN confirmed:', validatedISBN);
                            return {
                                success: true,
                                isbn: validatedISBN,
                                books: []
                            };
                        }
                    }
                } catch (zxingError) {
                    console.log('❌ [ZXING] ZXing-js failed:', zxingError.message);
                }
            } else {
                console.log('⚠️ [ZXING] ZXing-js library not available');
            }

            // No local detection succeeded
            console.log('❌ [LOCAL] No local barcode detection succeeded');
            return { success: false };
            
        } catch (error) {
            console.error('❌ [ERROR] Error in local barcode scanning:', error);
            return { success: false };
        }
    }

    /**
     * Simple ZXing-js detection (fallback only)
     */
    async detectISBNWithZXingSimple(canvas) {
        try {
            console.log('🔍 [ZXING-SIMPLE] Attempting simple ZXing-js detection...');
            
            // Use the simplest possible ZXing API
            const codeReader = new ZXing.BrowserMultiFormatReader();
            
            // Try the most basic decode method
            const result = await codeReader.decodeOnce(canvas);
            
            if (result && result.getText()) {
                const detectedCode = result.getText();
                console.log('✅ [ZXING-SIMPLE] Detected:', detectedCode);
                
                return this.validateDetectedISBN(detectedCode);
            }
            
            console.log('❌ [ZXING-SIMPLE] No code detected');
            return null;
            
        } catch (error) {
            console.log('❌ [ZXING-SIMPLE] Error:', error.message);
            return null;
        }
    }
    
    /**
     * Validate detected code as ISBN
     */
    validateDetectedISBN(detectedCode) {
        // Use ISBNUtils for validation if available
        if (window.ISBNUtils && window.ISBNUtils.looksLikeIsbn(detectedCode)) {
            const isbn = window.ISBNUtils.extractIsbn(detectedCode);
            if (isbn) {
                console.log('✅ [ZXING] Valid ISBN confirmed:', isbn);
                return isbn;
            }
        }
        
        // Fallback validation
        const cleanCode = detectedCode.replace(/[^0-9X]/gi, '');
        if (this.isValidISBNPattern(cleanCode)) {
            console.log('✅ [ZXING] ISBN pattern validated:', cleanCode);
            return cleanCode;
        }
        
        console.log('⚠️ [ZXING] Code detected but not valid ISBN:', detectedCode);
        return null;
    }
    
    /**
     * Simple ISBN pattern validation
     */
    isValidISBNPattern(code) {
        const patterns = [
            /^978\d{10}$/,     // ISBN-13 starting with 978
            /^979\d{10}$/,     // ISBN-13 starting with 979
            /^\d{9}[0-9X]$/i,  // ISBN-10
            /^\d{12}[0-9X]$/i  // EAN-13 (potential ISBN)
        ];
        
        return patterns.some(pattern => pattern.test(code));
    }

    /**
     * Preprocess image for better barcode detection
     */
    preprocessImageForBarcode(originalCanvas) {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Set canvas size (optimize for barcode scanning)
        canvas.width = originalCanvas.width;
        canvas.height = originalCanvas.height;
        
        // Draw original image
        ctx.drawImage(originalCanvas, 0, 0);
        
        // Get image data for processing
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;
        
        // Apply contrast enhancement and noise reduction
        for (let i = 0; i < data.length; i += 4) {
            // Convert to grayscale
            const gray = Math.round(0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2]);
            
            // Apply contrast enhancement
            const contrast = 1.2; // Increase contrast
            const enhanced = Math.max(0, Math.min(255, (gray - 128) * contrast + 128));
            
            // Apply threshold for better black/white separation
            const threshold = enhanced > 128 ? 255 : 0;
            
            data[i] = threshold;     // Red
            data[i + 1] = threshold; // Green
            data[i + 2] = threshold; // Blue
            // Alpha channel stays the same
        }
        
        // Put processed data back
        ctx.putImageData(imageData, 0, 0);
        
        console.log('Image preprocessed for barcode detection');
        return canvas;
    }

    /**
     * Fetch book information by ISBN from backend API
     */
    async fetchBookInfoByISBN(isbn) {
        console.log('📚 [API] Fetching book info for ISBN:', isbn);
        
        try {
            // First try to find in local database
            const localResponse = await fetch(`/api/books/isbn/${isbn}`);
            if (localResponse.ok) {
                const localData = await localResponse.json();
                if (localData.success) {
                    console.log('✅ [API] Found book in local database');
                    return localData.book;
                }
            }
            
            // If not found locally, try external lookup
            console.log('🔍 [API] Book not found locally, trying external lookup...');
            const externalResponse = await fetch(`/api/isbn/lookup/${isbn}`);
            if (externalResponse.ok) {
                const externalData = await externalResponse.json();
                if (externalData.success) {
                    console.log('✅ [API] Found book info from external source');
                    return externalData.book_info;
                }
            }
            
            // If still not found, create placeholder
            console.log('⚠️ [API] No book info found, creating placeholder');
            return {
                isbn: isbn,
                title: `Book ${isbn}`,
                author: 'Unknown Author',
                description: `Book detected with ISBN: ${isbn}. Please add details manually.`,
                publisher: 'Unknown Publisher',
                status: 'detected',
                source: 'scan_detection'
            };
            
        } catch (error) {
            console.error('❌ [API] Error fetching book info:', error);
            // Return placeholder on error
            return {
                isbn: isbn,
                title: `Book ${isbn}`,
                author: 'Unknown Author',
                description: `Book detected with ISBN: ${isbn}. Connection error - please add details manually.`,
                publisher: 'Unknown Publisher',
                status: 'detected',
                source: 'scan_detection'
            };
        }
    }

    /**
     * Fetch book information by UUID from backend API
     */
    async fetchBookByUUID(uuid) {
        console.log('📱 [API] Fetching book info for UUID:', uuid);
        
        try {
            const response = await fetch(`/api/books/uuid/${uuid}`);
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    console.log('✅ [API] Found book by UUID');
                    return data.book;
                }
            }
            
            // If not found, create placeholder
            console.log('⚠️ [API] Book not found by UUID, creating placeholder');
            return {
                uuid: uuid,
                title: `QR Book ${uuid.substring(0, 8)}`,
                author: 'Unknown Author',
                description: `Book detected with UUID: ${uuid}. Please add details manually.`,
                publisher: 'Unknown Publisher',
                status: 'detected',
                source: 'qr_scan'
            };
            
        } catch (error) {
            console.error('❌ [API] Error fetching book by UUID:', error);
            // Return placeholder on error
            return {
                uuid: uuid,
                title: `QR Book ${uuid.substring(0, 8)}`,
                author: 'Unknown Author',
                description: `Book detected with UUID: ${uuid}. Connection error - please add details manually.`,
                publisher: 'Unknown Publisher',
                status: 'detected',
                source: 'qr_scan'
            };
        }
    }

    /**
     * Fetch member information by employee code from backend API
     */
    async fetchMemberByEmployeeCode(employeeCode) {
        console.log('👤 [API] Fetching member info for employee code:', employeeCode);
        
        try {
            const response = await fetch(`/api/members/employee/${employeeCode}`);
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    console.log('✅ [API] Found member by employee code');
                    return data.member;
                }
            }
            
            console.log('⚠️ [API] Member not found by employee code');
            return null;
            
        } catch (error) {
            console.error('❌ [API] Error fetching member by employee code:', error);
            return null;
        }
    }

    /**
     * Fetch member information by any code (employee code or member ID)
     */
    async fetchMemberByCode(code) {
        console.log('👤 [API] Fetching member info for code:', code);
        
        try {
            const response = await fetch('/api/scan/member-qr', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    qr_data: code
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    console.log('✅ [API] Found member by code');
                    return data.member;
                }
            }
            
            console.log('⚠️ [API] Member not found by code');
            return null;
            
        } catch (error) {
            console.error('❌ [API] Error fetching member by code:', error);
            return null;
        }
    }

    /**
     * Show code found message
     */
    showCodeFoundMessage() {
        const scanControls = document.querySelector('.scan-controls');
        if (scanControls) {
            scanControls.innerHTML = `
                <p class="scan-text" style="color: #28a745;">
                    <i class="fas fa-check-circle text-success me-2"></i>Code detected! Scanning stopped.
                </p>
                <button class="btn btn-success btn-sm" onclick="universalScanner.restartScanning()">
                    <i class="fas fa-redo me-1"></i> Scan Another
                </button>
            `;
        }

        // Stop scan line animation
        const scanLine = document.querySelector('.scan-line');
        if (scanLine) {
            scanLine.style.animationPlayState = 'paused';
        }
    }

    /**
     * Restart scanning after code found
     */
    restartScanning() {
        if (this.currentStream && !this.scanningInterval) {
            const video = document.querySelector(`#${this.elements.preview.id} video`);
            if (video) {
                // Reset scan controls to original scanning interface
                const scanControls = document.querySelector('.scan-controls');
                if (scanControls) {
                    scanControls.innerHTML = `
                        <p class="scan-text">Position code within the frame</p>
                    `;
                }

                // Reset scan text
                const scanText = document.querySelector('.scan-text');
                if (scanText) {
                    scanText.innerHTML = 'Position code within the frame';
                    scanText.style.color = 'white';
                }

                // Restart scan line animation
                const scanLine = document.querySelector('.scan-line');
                if (scanLine) {
                    scanLine.style.animationPlayState = 'running';
                }

                // Clear previous results
                if (this.elements.resultsDiv) {
                    this.elements.resultsDiv.innerHTML = '';
                }

                // Restart automatic scanning
                this.startAutomaticScanning(video);
                
                console.log('📱 [SCANNER] Scanning restarted successfully');
            }
        }
    }

    /**
     * Toggle description display between truncated and full text
     */
    toggleDescription(button, fullDescription) {
        const descContainer = button.parentElement;
        const isExpanded = button.textContent.trim() === 'Show Less';
        
        if (isExpanded) {
            // Collapse description
            descContainer.innerHTML = `${fullDescription.substring(0, 200)}...
                <button class="btn btn-link btn-sm p-0 ms-1" onclick="universalScanner.toggleDescription(this, \`${fullDescription.replace(/`/g, '\\`').replace(/\$/g, '\\$')}\`)">
                    <small>Show More</small>
                </button>`;
        } else {
            // Expand description
            descContainer.innerHTML = `${fullDescription}
                <button class="btn btn-link btn-sm p-0 ms-1" onclick="universalScanner.toggleDescription(this, \`${fullDescription.replace(/`/g, '\\`').replace(/\$/g, '\\$')}\`)">
                    <small>Show Less</small>
                </button>`;
        }
    }

    /**
     * Default result handler
     */
    defaultResultHandler(results, isAutomatic) {
        if (!this.elements.resultsDiv) return;

        if (results.length === 0) {
            this.elements.resultsDiv.innerHTML = '<div class="alert alert-warning"><i class="fas fa-search me-2"></i>No codes detected in the image. Try adjusting the position or lighting.</div>';
            return;
        }

        let html = '';
        results.forEach(result => {
            const typeIcon = result.type === 'QR Code' ? 'fas fa-qrcode' : 'fas fa-barcode';
            const typeClass = result.type === 'QR Code' ? 'success' : 'info';

            html += `
                <div class="alert alert-success">
                    <i class="${typeIcon} me-2"></i>Successfully detected ${result.type}!
                </div>
            `;

            result.books.forEach(book => {
                html += `
                    <div class="book-result-card">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h5 class="mb-0">${book.title}</h5>
                            <span class="badge bg-${typeClass}">
                                <i class="${typeIcon} me-1"></i>${result.type}
                            </span>
                        </div>
                        <p class="mb-2"><strong>Author:</strong> ${book.author}</p>
                        <p class="mb-2"><strong>ISBN:</strong> ${book.isbn || 'Not available'}</p>
                        ${book.publisher ? `<p class="mb-2"><strong>Publisher:</strong> ${book.publisher}</p>` : ''}
                        ${book.language ? `<p class="mb-2"><strong>Language:</strong> ${book.language}</p>` : ''}
                        ${book.status ? `
                            <p class="mb-2"><strong>Status:</strong> 
                                <span class="badge bg-${book.status === 'available' ? 'success' : 'warning'}">
                                    ${book.status}
                                </span>
                            </p>
                            <p class="mb-2"><strong>Available:</strong> ${book.copies_available}/${book.copies_total}</p>
                        ` : ''}
                        ${book.description ? `
                            <div class="book-description mb-2">
                                <strong>Description:</strong>
                                <span class="description-text" id="desc-${book.isbn || Math.random()}">
                                    ${book.description.length > 200 ? 
                                        `${book.description.substring(0, 200)}...
                                         <button class="btn btn-link btn-sm p-0 ms-1" onclick="universalScanner.toggleDescription(this, \`${book.description.replace(/`/g, '\\`').replace(/\$/g, '\\$')}\`)">
                                            <small>Show More</small>
                                         </button>` : 
                                        book.description
                                    }
                                </span>
                            </div>
                        ` : ''}
                        <div class="d-flex gap-2">
                            ${book.id ? 
                                `<button class="btn btn-primary btn-sm" onclick="universalScanner.viewBookDetails(${book.id})">
                                    <i class="fas fa-eye me-1"></i>View Details
                                </button>` :
                                `<button class="btn btn-primary btn-sm" onclick="universalScanner.showBookDetails(${JSON.stringify(book).replace(/"/g, '&quot;')})">
                                    <i class="fas fa-plus me-1"></i>Add to Library
                                </button>`
                            }
                        </div>
                    </div>
                `;
            });
        });

        this.elements.resultsDiv.innerHTML = html;
    }

    /**
     * Default error handler
     */
    defaultErrorHandler(message) {
        if (this.elements.resultsDiv) {
            let helpText = '';
            if (message.includes('BarcodeDetector not available')) {
                helpText = `
                    <div class="mt-2">
                        <strong>💡 Browser Compatibility Tips:</strong>
                        <ul class="small mt-1 mb-0">
                            <li>Use Chrome or Edge for best scanning performance</li>
                            <li>Try uploading a clear image of the barcode instead</li>
                            <li>Use the "Manual ISBN Entry" button as an alternative</li>
                        </ul>
                    </div>
                `;
            }
            
            this.elements.resultsDiv.innerHTML = 
                `<div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>${message}
                    ${helpText}
                </div>`;
        } else {
            // Use toast notification if available, otherwise fall back to console
            if (window.showError) {
                window.showError(message);
            } else {
                console.error(message);
            }
        }
    }

    /**
     * View book details (placeholder - should be overridden)
     */
    viewBookDetails(bookId) {
        console.log('viewBookDetails should be implemented by the page using this module');
    }

    /**
     * Show book details (placeholder - should be overridden)
     */
    showBookDetails(bookData) {
        console.log('showBookDetails should be implemented by the page using this module');
    }

    /**
     * Manual entry for ISBN with validation
     */
    async manualIsbnEntry() {
        const isbn = prompt("Enter ISBN number (with or without dashes):");
        if (!isbn) return null; // User canceled
        
        // Use ISBNUtils for validation if available
        if (window.ISBNUtils) {
            const extractedIsbn = window.ISBNUtils.extractIsbn(isbn);
            if (extractedIsbn) {
                console.log('Manual ISBN entry validated:', extractedIsbn);
                return extractedIsbn;
            } else {
                if (window.showWarning) {
                    window.showWarning('Invalid ISBN format. Please check the number and try again.');
                } else {
                    console.error('Invalid ISBN format. Please check the number and try again.');
                }
                return null;
            }
        } else {
            // Fallback validation
            const cleanIsbn = isbn.replace(/[^0-9xX]/gi, '');
            if (cleanIsbn.length === 10 || cleanIsbn.length === 13) {
                return cleanIsbn;
            } else {
                if (window.showWarning) {
                    window.showWarning('Invalid ISBN format. Please enter a valid ISBN-10 or ISBN-13.');
                } else {
                    console.error('Invalid ISBN format. Please enter a valid ISBN-10 or ISBN-13.');
                }
                return null;
            }
        }
    }

    /**
     * Manual entry for QR/UUID
     */
    async manualUuidEntry() {
        const uuid = prompt("Enter book UUID or QR code data:");
        if (!uuid) return null; // User canceled
        
        // Basic UUID validation (could be enhanced)
        if (uuid.length > 5 && uuid.trim()) {
            return uuid.trim();
        } else {
            if (window.showWarning) {
                window.showWarning('Invalid UUID format. Please enter a valid identifier.');
            } else {
                console.error('Invalid UUID format. Please enter a valid identifier.');
            }
            return null;
        }
    }

    /**
     * Enhanced manual entry with validation
     */
    async enhancedManualEntry() {
        const input = prompt("Enter ISBN, QR code content, or book UUID:");
        if (!input) return; // User canceled
        
        // Use IDPatternUtils for comprehensive validation if available
        if (window.IDPatternUtils) {
            const parsed = window.IDPatternUtils.parseId(input);
            
            if (!parsed.isValid) {
                if (window.showWarning) {
                    window.showWarning(`Invalid input format. Detected type: ${parsed.type}\nPlease enter a valid ISBN, QR code content, or UUID.`);
                } else {
                    console.error(`Invalid input format. Detected type: ${parsed.type}\nPlease enter a valid ISBN, QR code content, or UUID.`);
                }
                return;
            }
            
            console.log('Parsed ID:', parsed);
            
            // Handle based on detected type
            switch (parsed.type) {
                case 'isbn':
                    const bookInfo = await this.fetchBookInfoByISBN(parsed.id);
                    if (bookInfo) {
                        this.callbacks.onResults([{
                            type: 'ISBN Barcode (Manual)',
                            books: [bookInfo]
                        }], false);
                    } else {
                        this.callbacks.onResults([{
                            type: 'ISBN Barcode (Manual)',
                            books: [{
                                isbn: parsed.id,
                                title: 'Unknown Title',
                                author: 'Unknown Author',
                                description: `Book with ISBN ${parsed.id} - metadata not found`
                            }]
                        }], false);
                    }
                    break;
                    
                case 'uuid':
                case 'qr_content':
                    const uuid = parsed.type === 'qr_content' ? parsed.metadata.uuid : parsed.id;
                    const qrBookInfo = await this.fetchBookByUUID(uuid);
                    if (qrBookInfo) {
                        this.callbacks.onResults([{
                            type: 'QR Code (Manual)',
                            books: [qrBookInfo]
                        }], false);
                    } else {
                        this.callbacks.onError('Book not found with the provided UUID');
                    }
                    break;
                    
                case 'qrcode':
                    // This is a direct QR code ID, treat as UUID
                    const directQrBookInfo = await this.fetchBookByUUID(parsed.id);
                    if (directQrBookInfo) {
                        this.callbacks.onResults([{
                            type: 'QR Code (Manual)',
                            books: [directQrBookInfo]
                        }], false);
                    } else {
                        this.callbacks.onError('Book not found with the provided QR code ID');
                    }
                    break;
                    
                default:
                    this.callbacks.onError('Unrecognized ID format');
            }
        } else {
            // Fallback to original manual entry logic
            await this.originalManualEntry(input);
        }
    }

    /**
     * Original manual entry logic (fallback)
     */
    async originalManualEntry(input) {
        const type = prompt("Enter 'ISBN' for ISBN barcode or 'UUID' for QR code/UUID entry:").toLowerCase();
        
        if (type === 'isbn') {
            const isbn = await this.manualIsbnEntry();
            if (isbn) {
                const bookInfo = await this.fetchBookInfoByISBN(isbn);
                if (bookInfo) {
                    this.callbacks.onResults([{
                        type: 'ISBN Barcode (Manual)',
                        books: [bookInfo]
                    }], false);
                } else {
                    this.callbacks.onResults([{
                        type: 'ISBN Barcode (Manual)',
                        books: [{
                            isbn: isbn,
                            title: 'Unknown Title',
                            author: 'Unknown Author',
                            description: `Book with ISBN ${isbn} - metadata not found`
                        }]
                    }], false);
                }
            }
        } else if (type === 'uuid') {
            const uuid = await this.manualUuidEntry();
            if (uuid) {
                const bookInfo = await this.fetchBookByUUID(uuid);
                if (bookInfo) {
                    this.callbacks.onResults([{
                        type: 'QR Code (Manual)',
                        books: [bookInfo]
                    }], false);
                } else {
                    this.callbacks.onError('Book not found with the provided UUID');
                }
            }
        } else {
            if (window.showWarning) {
                window.showWarning('Please enter either "ISBN" or "UUID"');
            } else {
                console.error('Please enter either "ISBN" or "UUID"');
            }
        }
    }

    /**
     * Cleanup - call when page unloads
     */
    cleanup() {
        this.stop();
        window.removeEventListener('beforeunload', this.cleanup.bind(this));
    }
}

// Export for use in other scripts
window.UniversalScanner = UniversalScanner;
