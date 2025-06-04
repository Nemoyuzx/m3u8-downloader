import requests
import re
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)


class M3U8Parser:
    """M3U8 playlist parser"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def parse(self, url, headers=None):
        """
        Parse M3U8 playlist and return segments and encryption info
        
        Args:
            url: M3U8 playlist URL
            headers: Additional headers
            
        Returns:
            tuple: (segments_list, encryption_info)
        """
        try:
            if headers:
                self.session.headers.update(headers)
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            content = response.text
            base_url = self._get_base_url(url)
            
            # Check if this is a master playlist
            if '#EXT-X-STREAM-INF' in content:
                # This is a master playlist, get the best quality stream
                stream_url = self._parse_master_playlist(content, base_url)
                if stream_url:
                    return self.parse(stream_url, headers)
                else:
                    logger.error("No suitable stream found in master playlist")
                    return [], {}
            
            # Parse media playlist
            segments = self._parse_media_playlist(content, base_url)
            encryption_info = self._parse_encryption_info(content, base_url)
            
            return segments, encryption_info
            
        except Exception as e:
            logger.error(f"Error parsing M3U8 playlist {url}: {str(e)}")
            return [], {}
    
    def _get_base_url(self, url):
        """Get base URL for resolving relative URLs"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{'/'.join(parsed.path.split('/')[:-1])}/"
    
    def _parse_master_playlist(self, content, base_url):
        """Parse master playlist and return the best quality stream URL"""
        lines = content.strip().split('\n')
        streams = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('#EXT-X-STREAM-INF'):
                # Parse stream info
                bandwidth = self._extract_attribute(line, 'BANDWIDTH')
                resolution = self._extract_attribute(line, 'RESOLUTION')
                
                # Get the stream URL (next line)
                if i + 1 < len(lines):
                    stream_url = lines[i + 1].strip()
                    if not stream_url.startswith('http'):
                        stream_url = urljoin(base_url, stream_url)
                    
                    streams.append({
                        'url': stream_url,
                        'bandwidth': int(bandwidth) if bandwidth else 0,
                        'resolution': resolution
                    })
                
                i += 1
            
            i += 1
        
        # Return the stream with highest bandwidth
        if streams:
            best_stream = max(streams, key=lambda x: x['bandwidth'])
            return best_stream['url']
        
        return None
    
    def _parse_media_playlist(self, content, base_url):
        """Parse media playlist and return segment URLs"""
        lines = content.strip().split('\n')
        segments = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and comments (except segment URLs)
            if not line or line.startswith('#'):
                continue
            
            # This should be a segment URL
            if not line.startswith('http'):
                line = urljoin(base_url, line)
            
            segments.append(line)
        
        return segments
    
    def _parse_encryption_info(self, content, base_url):
        """Parse encryption information from playlist"""
        encryption_info = {}
        
        # Look for EXT-X-KEY tag
        key_match = re.search(r'#EXT-X-KEY:(.+)', content)
        if key_match:
            key_attributes = key_match.group(1)
            
            # Extract method
            method = self._extract_attribute(key_attributes, 'METHOD')
            if method:
                encryption_info['method'] = method
            
            # Extract key URI
            uri = self._extract_attribute(key_attributes, 'URI')
            if uri:
                # Remove quotes
                uri = uri.strip('"\'')
                if not uri.startswith('http'):
                    uri = urljoin(base_url, uri)
                
                # Download the key
                try:
                    key_response = self.session.get(uri, timeout=10)
                    key_response.raise_for_status()
                    encryption_info['key'] = key_response.content.hex()
                except Exception as e:
                    logger.error(f"Error downloading encryption key from {uri}: {str(e)}")
            
            # Extract IV
            iv = self._extract_attribute(key_attributes, 'IV')
            if iv:
                # Remove 0x prefix if present
                if iv.startswith('0x') or iv.startswith('0X'):
                    iv = iv[2:]
                encryption_info['iv'] = iv
        
        return encryption_info
    
    def _extract_attribute(self, text, attribute):
        """Extract attribute value from M3U8 line"""
        pattern = f'{attribute}=([^,\\s]+)'
        match = re.search(pattern, text)
        if match:
            value = match.group(1)
            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            return value
        return None
