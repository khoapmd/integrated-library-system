/**
 * ISBN Utility Functions
 * Provides robust ISBN validation, normalization, and check digit verification
 * Inspired by the open-library-system approach
 */

class ISBNUtils {
    /**
     * Format an ISBN to a standard format (removes dashes, validates length)
     * @param {string} isbn - Raw ISBN string
     * @returns {string|null} - Formatted ISBN string or null if invalid
     */
    static formatIsbn(isbn) {
        // Remove any non-alphanumeric characters
        const cleanIsbn = isbn.replace(/[^0-9xX]/gi, '');
        
        // Check if it's a valid ISBN-10 or ISBN-13
        if (cleanIsbn.length === 10 || cleanIsbn.length === 13) {
            return cleanIsbn.toUpperCase(); // Ensure X is uppercase
        }
        
        return null;
    }

    /**
     * Validates an ISBN-13 check digit
     * @param {string} isbn - ISBN-13 string (without dashes)
     * @returns {boolean} - true if valid, false otherwise
     */
    static validateIsbn13(isbn) {
        if (isbn.length !== 13) return false;
        
        // Calculate check digit
        let sum = 0;
        for (let i = 0; i < 12; i++) {
            const digit = parseInt(isbn[i]);
            if (isNaN(digit)) return false;
            sum += digit * (i % 2 === 0 ? 1 : 3);
        }
        
        const checkDigit = (10 - (sum % 10)) % 10;
        const lastDigit = parseInt(isbn[12]);
        
        return !isNaN(lastDigit) && lastDigit === checkDigit;
    }

    /**
     * Validates an ISBN-10 check digit
     * @param {string} isbn - ISBN-10 string (without dashes)
     * @returns {boolean} - true if valid, false otherwise
     */
    static validateIsbn10(isbn) {
        if (isbn.length !== 10) return false;
        
        let sum = 0;
        for (let i = 0; i < 9; i++) {
            const digit = parseInt(isbn[i]);
            if (isNaN(digit)) return false;
            sum += digit * (10 - i);
        }
        
        const checkChar = isbn[9].toUpperCase();
        const checkDigit = checkChar === 'X' ? 10 : parseInt(checkChar);
        
        if (isNaN(checkDigit) && checkChar !== 'X') return false;
        
        return (sum + checkDigit) % 11 === 0;
    }

    /**
     * Validates an ISBN (either ISBN-10 or ISBN-13)
     * @param {string} isbn - ISBN string
     * @returns {boolean} - true if valid, false otherwise
     */
    static validateIsbn(isbn) {
        const formattedIsbn = this.formatIsbn(isbn);
        if (!formattedIsbn) return false;

        if (formattedIsbn.length === 13) {
            return this.validateIsbn13(formattedIsbn);
        } else if (formattedIsbn.length === 10) {
            return this.validateIsbn10(formattedIsbn);
        }

        return false;
    }

    /**
     * Normalize ISBN to ISBN-13 format if it's ISBN-10
     * @param {string} isbn - ISBN string
     * @returns {string|null} - Normalized ISBN-13 or original ISBN-13, null if invalid
     */
    static normalizeIsbn(isbn) {
        const formattedIsbn = this.formatIsbn(isbn);
        if (!formattedIsbn) return null;

        if (formattedIsbn.length === 13) {
            return this.validateIsbn13(formattedIsbn) ? formattedIsbn : null;
        } else if (formattedIsbn.length === 10) {
            if (!this.validateIsbn10(formattedIsbn)) return null;
            
            // Convert ISBN-10 to ISBN-13
            const isbn13Base = '978' + formattedIsbn.substring(0, 9);
            
            // Calculate new check digit
            let sum = 0;
            for (let i = 0; i < 12; i++) {
                sum += parseInt(isbn13Base[i]) * (i % 2 === 0 ? 1 : 3);
            }
            const checkDigit = (10 - (sum % 10)) % 10;
            
            return isbn13Base + checkDigit;
        }

        return null;
    }

    /**
     * Extract ISBN from various barcode formats and text
     * @param {string} text - Raw text from barcode/QR scan
     * @returns {string|null} - Extracted and validated ISBN or null
     */
    static extractIsbn(text) {
        // Common ISBN patterns
        const patterns = [
            // Standard ISBN with/without prefix
            /(?:ISBN[-\s]?(?:10|13)?[-\s]?)?(\d{10}|\d{13}|\d{9}[X])/i,
            // ISBN with hyphens
            /(?:ISBN[-\s]?)?(\d{1,5}[-\s]?\d{1,7}[-\s]?\d{1,7}[-\s]?[\dX])/i,
            // EAN barcode starting with 978 or 979 (ISBN-13)
            /^(978\d{10}|979\d{10})$/,
            // Just digits (10 or 13 length)
            /^(\d{10}|\d{13})$/
        ];

        for (const pattern of patterns) {
            const match = text.match(pattern);
            if (match) {
                const potentialIsbn = this.formatIsbn(match[1]);
                if (potentialIsbn && this.validateIsbn(potentialIsbn)) {
                    return this.normalizeIsbn(potentialIsbn);
                }
            }
        }

        return null;
    }

    /**
     * Check if a string looks like it could be an ISBN
     * @param {string} text - Text to check
     * @returns {boolean} - true if it looks like an ISBN
     */
    static looksLikeIsbn(text) {
        if (!text || typeof text !== 'string') return false;
        
        // Remove common ISBN prefixes and formatting
        const cleaned = text.replace(/^(?:ISBN[-\s]?(?:10|13)?[-\s]?)?/i, '').replace(/[-\s]/g, '');
        
        // Check if it's the right length and contains mostly digits
        if (cleaned.length === 10 || cleaned.length === 13) {
            // Allow one X at the end for ISBN-10
            const digitCount = (cleaned.match(/\d/g) || []).length;
            const hasValidX = cleaned.length === 10 && cleaned.endsWith('X');
            
            return digitCount === cleaned.length || (hasValidX && digitCount === 9);
        }
        
        return false;
    }

    /**
     * Get detailed ISBN information
     * @param {string} isbn - ISBN string
     * @returns {object|null} - ISBN details or null if invalid
     */
    static getIsbnDetails(isbn) {
        const normalized = this.normalizeIsbn(isbn);
        if (!normalized) return null;

        const details = {
            isbn13: normalized,
            isValid: true,
            prefix: normalized.substring(0, 3),
            registrationGroup: null,
            registrant: null,
            publication: null,
            checkDigit: normalized[12]
        };

        // For ISBN-13 starting with 978 or 979
        if (normalized.startsWith('978') || normalized.startsWith('979')) {
            // Basic parsing - full implementation would require ISBN agency data
            details.registrationGroup = normalized.substring(3, 4);
        }

        return details;
    }
}

// Export for use in other scripts
window.ISBNUtils = ISBNUtils;
