import requests
import os
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import logging

logger = logging.getLogger(__name__)


class SegmentDownloader:
    """Download and decrypt individual segments"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def download_segment(self, url, temp_dir, index, headers=None, encryption_key=None, encryption_iv=None, max_retries=3):
        """
        Download a single segment
        
        Args:
            url: Segment URL
            temp_dir: Temporary directory to save the segment
            index: Segment index
            headers: Additional headers
            encryption_key: AES encryption key (hex string)
            encryption_iv: AES encryption IV (hex string)
            max_retries: Maximum retry attempts
            
        Returns:
            str: Path to downloaded file, or None if failed
        """
        file_path = os.path.join(temp_dir, f'segment_{index:06d}.ts')
        
        if headers:
            session_headers = self.session.headers.copy()
            session_headers.update(headers)
        else:
            session_headers = self.session.headers
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(
                    url,
                    headers=session_headers,
                    timeout=30,
                    stream=True
                )
                response.raise_for_status()
                
                # Download the segment
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # Decrypt if needed
                if encryption_key:
                    self._decrypt_segment(file_path, encryption_key, encryption_iv, index)
                
                logger.debug(f"Downloaded segment {index}: {url}")
                return file_path
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for segment {index}: {str(e)}")
                
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                if attempt < max_retries - 1:
                    time.sleep(1 * (attempt + 1))  # Exponential backoff
                else:
                    logger.error(f"Failed to download segment {index} after {max_retries} attempts")
        
        return None
    
    def _decrypt_segment(self, file_path, encryption_key, encryption_iv, segment_index):
        """Decrypt an AES-encrypted segment"""
        try:
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Convert hex key to bytes
            key = bytes.fromhex(encryption_key)
            
            # Determine IV
            if encryption_iv:
                # Use provided IV
                iv = bytes.fromhex(encryption_iv)
            else:
                # Use segment index as IV (common in HLS)
                iv = segment_index.to_bytes(16, byteorder='big')
            
            # Decrypt
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_data = cipher.decrypt(encrypted_data)
            
            # Remove PKCS7 padding
            try:
                decrypted_data = unpad(decrypted_data, AES.block_size)
            except ValueError:
                # If unpadding fails, the data might not be padded
                pass
            
            # Write decrypted data back to file
            with open(file_path, 'wb') as f:
                f.write(decrypted_data)
            
            logger.debug(f"Decrypted segment {segment_index}")
            
        except Exception as e:
            logger.error(f"Error decrypting segment {segment_index}: {str(e)}")
            raise
