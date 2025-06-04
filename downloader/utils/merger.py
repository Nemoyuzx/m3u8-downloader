import os
import subprocess
import logging

logger = logging.getLogger(__name__)


class VideoMerger:
    """Merge video segments into a single file"""
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
    
    def _find_ffmpeg(self):
        """Find ffmpeg executable"""
        # Try common locations
        common_paths = [
            'ffmpeg',  # In PATH
            '/usr/bin/ffmpeg',
            '/usr/local/bin/ffmpeg',
            '/opt/homebrew/bin/ffmpeg',  # macOS Homebrew
        ]
        
        for path in common_paths:
            try:
                result = subprocess.run(
                    [path, '-version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        logger.warning("ffmpeg not found, will try simple concatenation")
        return None
    
    def merge_segments(self, segment_files, output_path):
        """
        Merge segment files into a single video file
        
        Args:
            segment_files: List of segment file paths
            output_path: Output video file path
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            if self.ffmpeg_path:
                return self._merge_with_ffmpeg(segment_files, output_path)
            else:
                return self._merge_simple_concat(segment_files, output_path)
                
        except Exception as e:
            logger.error(f"Error merging segments: {str(e)}")
            return False
    
    def _merge_with_ffmpeg(self, segment_files, output_path):
        """Merge using ffmpeg"""
        try:
            # Create a temporary file list for ffmpeg
            temp_list_file = output_path + '.filelist.txt'
            
            with open(temp_list_file, 'w') as f:
                for segment_file in segment_files:
                    # Escape file path for ffmpeg
                    escaped_path = segment_file.replace("'", "'\"'\"'")
                    f.write(f"file '{escaped_path}'\n")
            
            # Run ffmpeg
            cmd = [
                self.ffmpeg_path,
                '-f', 'concat',
                '-safe', '0',
                '-i', temp_list_file,
                '-c', 'copy',
                '-y',  # Overwrite output file
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            # Clean up temp file
            try:
                os.remove(temp_list_file)
            except:
                pass
            
            if result.returncode == 0:
                logger.info(f"Successfully merged {len(segment_files)} segments using ffmpeg")
                return True
            else:
                logger.error(f"ffmpeg error: {result.stderr}")
                # Fall back to simple concatenation
                return self._merge_simple_concat(segment_files, output_path)
                
        except subprocess.TimeoutExpired:
            logger.error("ffmpeg merge timed out")
            return False
        except Exception as e:
            logger.error(f"Error in ffmpeg merge: {str(e)}")
            # Fall back to simple concatenation
            return self._merge_simple_concat(segment_files, output_path)
    
    def _merge_simple_concat(self, segment_files, output_path):
        """Simple binary concatenation (fallback method)"""
        try:
            with open(output_path, 'wb') as output_file:
                for segment_file in segment_files:
                    if os.path.exists(segment_file):
                        with open(segment_file, 'rb') as input_file:
                            while True:
                                chunk = input_file.read(8192)
                                if not chunk:
                                    break
                                output_file.write(chunk)
                    else:
                        logger.warning(f"Segment file not found: {segment_file}")
            
            logger.info(f"Successfully merged {len(segment_files)} segments using simple concatenation")
            return True
            
        except Exception as e:
            logger.error(f"Error in simple concatenation: {str(e)}")
            return False
