# ===========================
# app/core/parser.py
# ===========================
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)

class HTMLParser:
    def __init__(self, html_content, base_url):
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.base_url = base_url
    
    def extract_text_content(self):
        """Extract all text content from the page"""
        try:
            # Remove script and style elements
            for element in self.soup(["script", "style", "nav", "footer"]):
                element.decompose()
            
            # Get text from main content areas
            content_selectors = ['main', 'article', '.content', '#content', '.main']
            text_content = []
            
            # Try to find main content first
            for selector in content_selectors:
                content = self.soup.select(selector)
                if content:
                    for elem in content:
                        text = elem.get_text(strip=True, separator=' ')
                        if text and len(text) > 20:  # Filter out short texts
                            text_content.append(text)
                    break
            
            # If no main content found, get paragraphs
            if not text_content:
                paragraphs = self.soup.find_all('p')
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 20:
                        text_content.append(text)
            
            return text_content[:50]  # Limit to 50 items
        
        except Exception as e:
            logger.error(f"Error extracting text content: {e}")
            return []
    
    def extract_links(self):
        """Extract all links from the page"""
        try:
            links = []
            for link in self.soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text(strip=True)
                
                if href.startswith('#'):  # Skip anchor links
                    continue
                
                absolute_url = urljoin(self.base_url, href)
                
                links.append({
                    'text': text or 'No text',
                    'href': href,
                    'absolute_url': absolute_url
                })
            
            return links[:100]  # Limit to 100 links
        
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
            return []
    
    def extract_images(self):
        """Extract all images from the page"""
        try:
            images = []
            for img in self.soup.find_all('img'):
                src = img.get('src')
                if not src:
                    continue
                
                alt = img.get('alt', '')
                absolute_url = urljoin(self.base_url, src)
                
                images.append({
                    'alt': alt,
                    'src': src,
                    'absolute_url': absolute_url
                })
            
            return images[:50]  # Limit to 50 images
        
        except Exception as e:
            logger.error(f"Error extracting images: {e}")
            return []
    
    def extract_headings(self):
        """Extract all headings from the page"""
        try:
            headings = {}
            for i in range(1, 7):  # h1 to h6
                tag = f'h{i}'
                elements = self.soup.find_all(tag)
                if elements:
                    headings[tag] = [elem.get_text(strip=True) for elem in elements]
            
            return headings
        
        except Exception as e:
            logger.error(f"Error extracting headings: {e}")
            return {}
    
    def extract_meta_data(self):
        """Extract meta data from the page"""
        try:
            meta_data = {}
            
            # Title
            title = self.soup.find('title')
            if title:
                meta_data['title'] = title.get_text(strip=True)
            
            # Meta tags
            meta_tags = self.soup.find_all('meta')
            for meta in meta_tags:
                name = meta.get('name') or meta.get('property')
                content = meta.get('content')
                
                if name and content:
                    meta_data[name] = content
            
            return meta_data
        
        except Exception as e:
            logger.error(f"Error extracting meta data: {e}")
            return {}
    
    def extract_forms(self):
        """Extract all forms from the page"""
        try:
            forms = []
            for form in self.soup.find_all('form'):
                form_data = {
                    'action': form.get('action', ''),
                    'method': form.get('method', 'get').upper(),
                    'inputs': []
                }
                
                # Extract input fields
                for input_elem in form.find_all(['input', 'textarea', 'select']):
                    input_data = {
                        'name': input_elem.get('name', ''),
                        'type': input_elem.get('type', 'text'),
                        'placeholder': input_elem.get('placeholder', ''),
                        'required': input_elem.has_attr('required')
                    }
                    form_data['inputs'].append(input_data)
                
                forms.append(form_data)
            
            return forms
        
        except Exception as e:
            logger.error(f"Error extracting forms: {e}")
            return []