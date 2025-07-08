/**
 * ID Pattern Validation Utilities
 * Provides validation for various ID patterns including ISBN and custom library IDs
 * Inspired by the open-library-system approach
 */

class IDPatternUtils {
    /**
     * Regular expression patterns for different ID types
     */
    static patterns = {
        // ISBN patterns (both ISBN-10 and ISBN-13)
        isbn: /^(978|979)[0-9X]{10,13}$/,
        // Custom library QR code IDs (starting with specific prefixes)
        qrCode: /^878[0-9]{10,13}$/,
        // Combined pattern for all valid book IDs
        bookId: /^(978|979|878)[0-9X]{10,13}$/,
        // UUID pattern (for QR code content)
        uuid: /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
    };

    /**
     * Check if an ID matches the book ID pattern
     * @param {string} id - ID to validate
     * @returns {boolean} - true if valid book ID format
     */
    static isValidBookId(id) {
        if (!id || typeof id !== 'string') return false;
        return this.patterns.bookId.test(id.replace(/[-\s]/g, ''));
    }

    /**
     * Check if an ID is an ISBN format
     * @param {string} id - ID to check
     * @returns {boolean} - true if ISBN format
     */
    static isIsbnFormat(id) {
        if (!id || typeof id !== 'string') return false;
        const cleaned = id.replace(/[-\s]/g, '');
        return this.patterns.isbn.test(cleaned);
    }

    /**
     * Check if an ID is a QR code format
     * @param {string} id - ID to check
     * @returns {boolean} - true if QR code format
     */
    static isQrCodeFormat(id) {
        if (!id || typeof id !== 'string') return false;
        const cleaned = id.replace(/[-\s]/g, '');
        return this.patterns.qrCode.test(cleaned);
    }

    /**
     * Check if a string is a valid UUID
     * @param {string} uuid - UUID to validate
     * @returns {boolean} - true if valid UUID format
     */
    static isValidUuid(uuid) {
        if (!uuid || typeof uuid !== 'string') return false;
        return this.patterns.uuid.test(uuid);
    }

    /**
     * Determine the type of ID
     * @param {string} id - ID to analyze
     * @returns {string} - 'isbn', 'qrcode', 'uuid', or 'unknown'
     */
    static getIdType(id) {
        if (!id || typeof id !== 'string') return 'unknown';
        
        const cleaned = id.replace(/[-\s]/g, '');
        
        if (this.isIsbnFormat(cleaned)) {
            return 'isbn';
        } else if (this.isQrCodeFormat(cleaned)) {
            return 'qrcode';
        } else if (this.isValidUuid(id)) {
            return 'uuid';
        }
        
        return 'unknown';
    }

    /**
     * Extract and validate ID from various sources
     * @param {string} input - Raw input string
     * @returns {object} - {type, id, isValid}
     */
    static parseId(input) {
        if (!input || typeof input !== 'string') {
            return { type: 'unknown', id: null, isValid: false };
        }

        const trimmed = input.trim();
        
        // Try to parse as JSON first (QR code content)
        try {
            const data = JSON.parse(trimmed);
            if (data.type === 'library_book' && data.uuid) {
                return {
                    type: 'qr_content',
                    id: data.uuid,
                    isValid: this.isValidUuid(data.uuid),
                    metadata: data
                };
            }
        } catch (e) {
            // Not JSON, continue with other parsing
        }

        // Check for ISBN with ISBNUtils if available
        if (window.ISBNUtils) {
            const isbn = window.ISBNUtils.extractIsbn(trimmed);
            if (isbn) {
                return {
                    type: 'isbn',
                    id: isbn,
                    isValid: true
                };
            }
        }

        // Check direct ID patterns
        const idType = this.getIdType(trimmed);
        if (idType !== 'unknown') {
            return {
                type: idType,
                id: trimmed.replace(/[-\s]/g, ''),
                isValid: true
            };
        }

        return { type: 'unknown', id: trimmed, isValid: false };
    }

    /**
     * Normalize ID format for storage/comparison
     * @param {string} id - ID to normalize
     * @returns {string|null} - Normalized ID or null if invalid
     */
    static normalizeId(id) {
        const parsed = this.parseId(id);
        
        if (!parsed.isValid) return null;
        
        switch (parsed.type) {
            case 'isbn':
                // Use ISBNUtils for normalization if available
                return window.ISBNUtils ? window.ISBNUtils.normalizeIsbn(id) : parsed.id;
            case 'qrcode':
            case 'uuid':
                return parsed.id;
            case 'qr_content':
                return parsed.metadata.uuid;
            default:
                return null;
        }
    }

    /**
     * Get display-friendly ID format
     * @param {string} id - ID to format
     * @returns {string} - Formatted ID for display
     */
    static formatForDisplay(id) {
        const parsed = this.parseId(id);
        
        if (!parsed.isValid) return id;
        
        switch (parsed.type) {
            case 'isbn':
                // Format ISBN with hyphens for readability
                const isbn = parsed.id;
                if (isbn.length === 13) {
                    return `${isbn.substring(0, 3)}-${isbn.substring(3, 4)}-${isbn.substring(4, 6)}-${isbn.substring(6, 12)}-${isbn.substring(12)}`;
                } else if (isbn.length === 10) {
                    return `${isbn.substring(0, 1)}-${isbn.substring(1, 4)}-${isbn.substring(4, 9)}-${isbn.substring(9)}`;
                }
                return isbn;
            case 'qrcode':
                // Format QR code ID with separators
                const qr = parsed.id;
                return `${qr.substring(0, 3)}-${qr.substring(3, 5)}-${qr.substring(5)}`;
            case 'uuid':
            case 'qr_content':
                return parsed.id;
            default:
                return id;
        }
    }

    /**
     * Validate ID strength/quality
     * @param {string} id - ID to validate
     * @returns {object} - {score, issues, suggestions}
     */
    static validateIdQuality(id) {
        const parsed = this.parseId(id);
        const result = {
            score: 0,
            issues: [],
            suggestions: []
        };
        
        if (!parsed.isValid) {
            result.issues.push('Invalid ID format');
            result.suggestions.push('Please check the ID format and try again');
            return result;
        }
        
        result.score = 85; // Base score for valid ID
        
        switch (parsed.type) {
            case 'isbn':
                result.score = 95; // High score for ISBN
                if (window.ISBNUtils) {
                    const details = window.ISBNUtils.getIsbnDetails(id);
                    if (details && details.prefix === '978') {
                        result.score = 100; // Perfect score for standard ISBN
                    }
                }
                break;
            case 'qrcode':
                result.score = 90; // Good score for QR code
                break;
            case 'uuid':
                result.score = 85; // Standard score for UUID
                break;
        }
        
        return result;
    }
}

// Export for use in other scripts
window.IDPatternUtils = IDPatternUtils;
