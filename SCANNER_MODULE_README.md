# UniversalScanner Module Documentation

## Overview
The `UniversalScanner` module provides a unified, reusable solution for QR code and ISBN barcode scanning across the Library Management System. It automatically detects both QR codes and ISBN barcodes from camera input or uploaded images.

## Features
- **Automatic Detection**: Simultaneously scans for both QR codes and ISBN barcodes
- **Camera Integration**: Real-time scanning using device camera
- **File Upload**: Scan codes from uploaded images
- **Modular Design**: Easy to integrate into any page
- **Customizable Callbacks**: Handle results and errors with custom functions
- **Visual Feedback**: Scanning overlay with animations and status indicators

## Usage

### Basic Setup

1. **Include Required Files**:
```html
<link href="{{ url_for('static', filename='css/scanner.css') }}" rel="stylesheet">
<script src="{{ url_for('static', filename='js/scanner-module.js') }}"></script>
```

2. **HTML Structure**:
```html
<div class="camera-preview" id="cameraPreview">
    <!-- Scanner preview will appear here -->
</div>
<button class="btn btn-primary" id="toggleBtn">Start Scanner</button>
<input type="file" id="fileInput" accept="image/*" style="display: none;">
<div id="statusDiv" style="display: none;">Scanning...</div>
<div id="resultsDiv"></div>
```

3. **JavaScript Initialization**:
```javascript
const scanner = new UniversalScanner({
    scanInterval: 3000,  // Scan every 3 seconds
    autoStop: true,      // Stop after detection
    onResults: handleResults,
    onError: handleError
});

scanner.init({
    preview: '#cameraPreview',
    toggleBtn: '#toggleBtn',
    uploadInput: '#fileInput',
    statusDiv: '#statusDiv',
    resultsDiv: '#resultsDiv'
});
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `scanInterval` | number | 3000 | Milliseconds between automatic scans |
| `autoStop` | boolean | true | Stop scanning after code detection |
| `showStatus` | boolean | true | Show scanning status indicator |
| `apiBaseUrl` | string | '/api' | Base URL for scanning API endpoints |
| `onResults` | function | default handler | Callback for scan results |
| `onError` | function | default handler | Callback for errors |
| `onScanStart` | function | empty | Callback when scanning starts |
| `onScanStop` | function | empty | Callback when scanning stops |

### Custom Result Handling

```javascript
function handleResults(results, isAutomatic) {
    results.forEach(result => {
        console.log(`Found ${result.type}:`, result.books);
        result.books.forEach(book => {
            // Process each book found
            console.log(book.title, book.author, book.isbn);
        });
    });
}

function handleError(message) {
    console.error('Scanning error:', message);
}
```

### API Responses

The scanner expects API endpoints that return:

**Success Response**:
```json
{
    "success": true,
    "books": [
        {
            "id": 123,
            "title": "Book Title",
            "author": "Author Name",
            "isbn": "978-1234567890",
            "publisher": "Publisher",
            "language": "English",
            "description": "Book description..."
        }
    ]
}
```

**Error Response**:
```json
{
    "success": false,
    "message": "Error message"
}
```

## Current Implementations

### 1. Scanner Page (`/scanner`)
- Full-page scanner implementation
- Direct result display
- Download and share functionality

### 2. Books Page (`/books`) 
- Modal-based scanner for adding books
- Integrates with book form
- Auto-fills form fields from scan results

## Methods

| Method | Description |
|--------|-------------|
| `init(elements)` | Initialize with DOM elements |
| `start()` | Start camera scanner |
| `stop()` | Stop scanner and cleanup |
| `toggle()` | Toggle scanner on/off |
| `scanImage(file, isAutomatic)` | Scan uploaded image |
| `restartScanning()` | Restart after code detection |
| `cleanup()` | Full cleanup for page unload |

## Styling

The module includes CSS classes for styling:
- `.scanning-overlay` - Overlay container
- `.scan-frame` - Scanning frame
- `.scan-line` - Animated scan line
- `.scan-text` - Status text
- `.scanner-controls` - Control buttons
- `.camera-preview` - Camera preview container

## Future Extensions

The module is designed to be easily extended:

1. **New Code Types**: Add support for other barcode formats
2. **Multiple Pages**: Integrate into any page that needs scanning
3. **Custom APIs**: Configure different API endpoints
4. **Enhanced UI**: Add more visual feedback and controls
5. **Analytics**: Track scanning success rates and usage

## Troubleshooting

### Common Issues:
1. **Camera Access**: Ensure HTTPS or localhost for camera permissions
2. **API Endpoints**: Verify `/api/scan/qr` and `/api/scan/isbn` are available
3. **CSS Loading**: Include scanner.css for proper overlay display
4. **Module Loading**: Ensure scanner-module.js loads before page scripts

### Browser Compatibility:
- Modern browsers with getUserMedia support
- HTTPS required for camera access (except localhost)
- File API support for image uploads
