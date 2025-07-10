import qrcode
import cv2
import numpy as np
from pyzbar import pyzbar
from PIL import Image
import io
import base64
import requests
import isbnlib
from isbnlib import meta, cover
import json
import time
import ssl
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class QRCodeManager:
    def __init__(self):
        self.qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
    
    def generate_qr_code(self, book_uuid, format='base64'):
        """Generate QR code for a book using its UUID"""
        self.qr.clear()
        
        # Create QR code data with book information
        qr_data = {
            'type': 'library_book',
            'uuid': book_uuid,
            'timestamp': str(int(time.time()))
        }
        
        self.qr.add_data(json.dumps(qr_data))
        self.qr.make(fit=True)
        
        # Create QR code image
        img = self.qr.make_image(fill_color="black", back_color="white")
        
        if format == 'base64':
            # Convert to base64 for web display
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return f"data:image/png;base64,{img_str}"
        elif format == 'pil':
            return img
        else:
            return img
    
    def scan_qr_code(self, image_data):
        """Scan QR code from image data"""
        try:
            # Convert base64 to PIL Image if needed
            if isinstance(image_data, str) and image_data.startswith('data:image'):
                header, data = image_data.split(',', 1)
                image_data = base64.b64decode(data)
                image = Image.open(io.BytesIO(image_data))
            elif isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            else:
                image = image_data
            
            # Convert to numpy array for pyzbar
            img_array = np.array(image)
            
            # Decode QR codes
            decoded_objects = pyzbar.decode(img_array)
            
            results = []
            for obj in decoded_objects:
                try:
                    data = json.loads(obj.data.decode('utf-8'))
                    if data.get('type') == 'library_book':
                        results.append({
                            'uuid': data.get('uuid'),
                            'timestamp': data.get('timestamp'),
                            'rect': obj.rect
                        })
                    elif data.get('type') == 'library_member':
                        results.append({
                            'employee_code': data.get('employee_code'),
                            'member_id': data.get('member_id'),
                            'timestamp': data.get('timestamp'),
                            'rect': obj.rect
                        })
                except json.JSONDecodeError:
                    # Handle non-JSON QR codes (might be plain employee codes)
                    qr_text = obj.data.decode('utf-8')
                    results.append({
                        'data': qr_text,
                        'rect': obj.rect,
                        # Try to identify if it might be an employee code or member ID
                        'possible_employee_code': qr_text if len(qr_text) <= 20 else None
                    })
            
            return results
        except Exception as e:
            print(f"Error scanning QR code: {e}")
            return []

class ISBNScanner:
    def __init__(self):
        # Import config to get ISBN services
        try:
            from config import Config
            self.services = Config.ISBN_SERVICES
        except ImportError:
            # Fallback if config import fails
            self.services = ['goob', 'openl', 'worldcat']  # ISBN service providers
        
        print(f"ISBN Scanner initialized with services: {self.services}")
        
        # Configure requests session with SSL verification disabled for development
        self.session = requests.Session()
        
        # Disable SSL verification (for development only)
        self.session.verify = False
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Set up retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set timeout
        self.timeout = 10
    
    def scan_isbn_from_image(self, image_data):
        """Scan ISBN barcode from image"""
        try:
            # Convert image data to OpenCV format
            if isinstance(image_data, str) and image_data.startswith('data:image'):
                header, data = image_data.split(',', 1)
                image_data = base64.b64decode(data)
            
            # Convert to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert to grayscale for better barcode detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Decode barcodes
            barcodes = pyzbar.decode(gray)
            
            isbns = []
            for barcode in barcodes:
                barcode_data = barcode.data.decode('utf-8')
                
                # Validate if it's an ISBN
                if self.is_valid_isbn(barcode_data):
                    isbns.append({
                        'isbn': barcode_data,
                        'type': barcode.type,
                        'rect': barcode.rect
                    })
            
            return isbns
        except Exception as e:
            print(f"Error scanning ISBN: {e}")
            return []
    
    def is_valid_isbn(self, isbn_string):
        """Validate ISBN format"""
        try:
            # Clean the ISBN string
            isbn_clean = isbnlib.clean(isbn_string)
            return isbnlib.is_isbn10(isbn_clean) or isbnlib.is_isbn13(isbn_clean)
        except:
            return False
    
    def get_book_info_by_isbn(self, isbn):
        """Get book information from ISBN with fallback through multiple services"""
        try:
            # Clean the ISBN
            isbn_clean = isbnlib.clean(isbn)
            print(f"Looking up ISBN: {isbn_clean}")
            
            # Try each service in order until one succeeds
            book_info = None
            for service in self.services:
                try:
                    print(f"Trying ISBN service: {service}")
                    book_info = meta(isbn_clean, service=service)
                    if book_info:
                        print(f"✅ Successfully found metadata using service: {service}")
                        print(f"Book info: {book_info}")
                        break
                except Exception as e:
                    print(f"❌ Service '{service}' failed: {e}")
                    continue
            
            # If no service worked, try with default service as final attempt
            if not book_info:
                try:
                    print("Trying default service as final attempt...")
                    book_info = meta(isbn_clean, service='default')
                    if book_info:
                        print(f"✅ Successfully found metadata using default service")
                        print(f"Book info: {book_info}")
                except Exception as e:
                    print(f"❌ Default service also failed: {e}")
            
            if book_info:
                # Get cover image URL
                cover_url = None
                try:
                    covers = cover(isbn_clean)
                    if covers:
                        cover_url = covers.get('thumbnail') or covers.get('smallThumbnail')
                except Exception as e:
                    print(f"Error fetching cover: {e}")
                
                # Try to get description, page count, and categories from Google Books API
                google_data = self._get_description_from_google_books(isbn_clean)
                description = None
                page_count = None
                categories = None
                
                if google_data:
                    description = google_data.get('description')
                    page_count = google_data.get('pageCount')
                    categories = google_data.get('categories')
                
                # If no description from Google Books, try Open Library
                if not description:
                    description = self._get_description_from_open_library(isbn_clean)

                return {
                    'isbn': isbn_clean,
                    'title': book_info.get('Title', f'Book {isbn_clean}'),
                    'authors': book_info.get('Authors', []),
                    'author': ', '.join(book_info.get('Authors', ['Unknown Author'])),
                    'publisher': book_info.get('Publisher', 'Unknown Publisher'),
                    'publication_date': book_info.get('Year', ''),
                    'language': book_info.get('Language', 'English'),
                    'description': description or 'No description available',
                    'cover_url': cover_url,
                    'pages': page_count,
                    'pageCount': page_count,  # Include both fields for compatibility
                    'categories': categories,  # Add categories field
                    'source': 'api_lookup'
                }
            else:
                # If no metadata found from any isbnlib service, try Google Books directly
                print(f"❌ No metadata found from any isbnlib service, trying Google Books API directly...")
                try:
                    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn_clean}"
                    response = self.session.get(url, timeout=self.timeout)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('totalItems', 0) > 0:
                            volume_info = data['items'][0].get('volumeInfo', {})
                            
                            # Extract description and clean it
                            description = volume_info.get('description', 'No description available')
                            if description:
                                import re
                                description = re.sub(r'<[^>]+>', '', description)
                                description = description.strip()
                                if len(description) > 500:
                                    description = description[:500] + "..."
                            
                            # Extract categories
                            categories = volume_info.get('categories', [])
                            
                            print(f"✅ Successfully found book info via Google Books API")
                            return {
                                'isbn': isbn_clean,
                                'title': volume_info.get('title', f'Book {isbn_clean}'),
                                'authors': volume_info.get('authors', []),
                                'author': ', '.join(volume_info.get('authors', ['Unknown Author'])),
                                'publisher': volume_info.get('publisher', 'Unknown Publisher'),
                                'publication_date': volume_info.get('publishedDate', ''),
                                'language': volume_info.get('language', 'en'),
                                'description': description,
                                'cover_url': volume_info.get('imageLinks', {}).get('thumbnail'),
                                'pages': volume_info.get('pageCount'),
                                'categories': categories,  # Add categories field
                                'source': 'google_books_fallback'
                            }
                except Exception as e:
                    print(f"❌ Google Books API error: {e}")
                
                # Try Open Library as final fallback
                print(f"Trying Open Library as final fallback...")
                try:
                    open_library_data = self._get_full_book_info_from_open_library(isbn_clean)
                    if open_library_data:
                        print(f"✅ Successfully found book info via Open Library")
                        return open_library_data
                except Exception as e:
                    print(f"❌ Open Library error: {e}")
                
                # If all external lookups fail, return basic info
                print(f"❌ All API lookups failed, returning basic info for ISBN: {isbn_clean}")
                return {
                    'isbn': isbn_clean,
                    'title': f'Book {isbn_clean}',
                    'authors': [],
                    'author': 'Unknown Author',
                    'publisher': 'Unknown Publisher',
                    'publication_date': '',
                    'language': 'English',
                    'description': f'Book with ISBN {isbn_clean}. Please update information manually.',
                    'cover_url': None,
                    'pages': None,
                    'categories': [],  # Add empty categories array
                    'source': 'manual_entry'
                }
                
        except Exception as e:
            print(f"Error getting book info for ISBN {isbn}: {e}")
            # Return basic fallback info
            return {
                'isbn': isbn,
                'title': f'Book {isbn}',
                'authors': [],
                'author': 'Unknown Author',
                'publisher': 'Unknown Publisher',
                'publication_date': '',
                'language': 'English',
                'description': f'Book with ISBN {isbn}. Error occurred during lookup: {str(e)}',
                'cover_url': None,
                'pages': None,
                'categories': [],  # Add empty categories array
                'source': 'error_fallback'
            }

    def _get_description_from_google_books(self, isbn):
        """Get book description, page count, and categories from Google Books API"""
        try:
            url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('totalItems', 0) > 0:
                    volume_info = data['items'][0].get('volumeInfo', {})
                    description = volume_info.get('description', '')
                    page_count = volume_info.get('pageCount')
                    categories = volume_info.get('categories', [])
                    
                    # Clean up HTML tags if present in description
                    if description:
                        import re
                        description = re.sub(r'<[^>]+>', '', description)
                        description = description.strip()
                        # Limit description length
                        if len(description) > 500:
                            description = description[:500] + "..."
                    
                    return {
                        'description': description,
                        'pageCount': page_count,
                        'categories': categories
                    }
            return None
        except Exception as e:
            print(f"Error fetching description from Google Books for ISBN {isbn}: {e}")
            return None

    def _get_description_from_open_library(self, isbn):
        """Get book description from Open Library API"""
        try:
            url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                book_key = f"ISBN:{isbn}"
                
                if book_key in data:
                    book_data = data[book_key]
                    # Try different description fields
                    description = (
                        book_data.get('description', {}).get('value') if isinstance(book_data.get('description'), dict) else
                        book_data.get('description') if isinstance(book_data.get('description'), str) else
                        book_data.get('excerpts', [{}])[0].get('text', '') if book_data.get('excerpts') else ''
                    )
                    
                    if description and isinstance(description, str):
                        description = description.strip()
                        # Limit description length
                        if len(description) > 500:
                            description = description[:500] + "..."
                        return description
            return None
        except Exception as e:
            print(f"Error fetching description from Open Library for ISBN {isbn}: {e}")
            return None

    def _get_full_book_info_from_open_library(self, isbn):
        """Get complete book information from Open Library API as fallback"""
        try:
            url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                book_key = f"ISBN:{isbn}"
                
                if book_key in data:
                    book_data = data[book_key]
                    
                    # Extract title
                    title = book_data.get('title', f'Book {isbn}')
                    
                    # Extract authors
                    authors = []
                    if 'authors' in book_data:
                        for author in book_data['authors']:
                            if isinstance(author, dict) and 'name' in author:
                                authors.append(author['name'])
                            elif isinstance(author, str):
                                authors.append(author)
                    
                    # Extract publisher
                    publisher = 'Unknown Publisher'
                    if 'publishers' in book_data and book_data['publishers']:
                        publisher = book_data['publishers'][0].get('name', 'Unknown Publisher')
                    
                    # Extract publication date
                    pub_date = book_data.get('publish_date', '')
                    
                    # Extract description
                    description = (
                        book_data.get('description', {}).get('value') if isinstance(book_data.get('description'), dict) else
                        book_data.get('description') if isinstance(book_data.get('description'), str) else
                        book_data.get('excerpts', [{}])[0].get('text', '') if book_data.get('excerpts') else
                        f'Book with ISBN {isbn} from Open Library'
                    )
                    
                    if description and isinstance(description, str):
                        description = description.strip()
                        if len(description) > 500:
                            description = description[:500] + "..."
                    
                    # Extract cover image
                    cover_url = None
                    if 'cover' in book_data:
                        cover_url = book_data['cover'].get('medium') or book_data['cover'].get('small')
                    
                    # Extract page count
                    pages = book_data.get('number_of_pages')
                    
                    return {
                        'isbn': isbn,
                        'title': title,
                        'authors': authors,
                        'author': ', '.join(authors) if authors else 'Unknown Author',
                        'publisher': publisher,
                        'publication_date': pub_date,
                        'language': book_data.get('languages', [{}])[0].get('key', 'en').replace('/languages/', ''),
                        'description': description,
                        'cover_url': cover_url,
                        'pages': pages,
                        'pageCount': pages,
                        'categories': [],  # Open Library doesn't typically have categories, so empty array
                        'source': 'open_library_fallback'
                    }
            return None
        except Exception as e:
            print(f"Error fetching full book info from Open Library for ISBN {isbn}: {e}")
            return None

    def search_books_by_isbn(self, isbn_list):
        """Search for multiple books by ISBN"""
        results = []
        for isbn in isbn_list:
            book_info = self.get_book_info_by_isbn(isbn)
            if book_info:
                results.append(book_info)
        return results

# Additional utility functions
import time

def generate_member_id():
    """Generate unique member ID"""
    return f"LIB{int(time.time())}"

def calculate_fine(due_date, return_date, fine_per_day=1.0):
    """Calculate fine for overdue books"""
    if return_date <= due_date:
        return 0.0
    
    days_overdue = (return_date - due_date).days
    return days_overdue * fine_per_day
