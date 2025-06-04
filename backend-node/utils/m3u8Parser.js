const axios = require('axios');
const { URL } = require('url');

class M3U8Parser {
  constructor() {
    this.defaultHeaders = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    };
  }
  
  async parse(m3u8Url) {
    try {
      // 下载M3U8文件
      const response = await axios.get(m3u8Url, {
        headers: this.defaultHeaders,
        timeout: 10000
      });
      
      const content = response.data;
      const baseUrl = this.getBaseUrl(m3u8Url);
      
      // 解析M3U8内容
      const parsed = this.parseM3U8Content(content, baseUrl);
      
      return parsed;
    } catch (error) {
      throw new Error(`解析M3U8文件失败: ${error.message}`);
    }
  }
  
  parseM3U8Content(content, baseUrl) {
    const lines = content.split('\n').map(line => line.trim()).filter(line => line);
    const segments = [];
    let encryption = null;
    let segmentIndex = 0;
    let currentDuration = 0;
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      
      // 检查是否是主播放列表
      if (line.includes('#EXT-X-STREAM-INF')) {
        throw new Error('这是一个主播放列表，请选择具体的流质量链接');
      }
      
      // 解析加密信息
      if (line.startsWith('#EXT-X-KEY:')) {
        encryption = this.parseEncryption(line, baseUrl);
      }
      
      // 解析片段时长
      if (line.startsWith('#EXTINF:')) {
        const match = line.match(/#EXTINF:([0-9.]+)/);
        if (match) {
          currentDuration = parseFloat(match[1]);
        }
      }
      
      // 解析片段URL
      if (!line.startsWith('#') && line.length > 0) {
        const segmentUrl = this.resolveUrl(line, baseUrl);
        segments.push({
          index: segmentIndex++,
          url: segmentUrl,
          duration: currentDuration,
          encryption: encryption
        });
        currentDuration = 0;
      }
    }
    
    if (segments.length === 0) {
      throw new Error('未找到有效的视频片段');
    }
    
    return {
      segments,
      encryption,
      totalDuration: segments.reduce((sum, seg) => sum + seg.duration, 0),
      baseUrl
    };
  }
  
  parseEncryption(keyLine, baseUrl) {
    const encryption = {
      method: null,
      uri: null,
      iv: null
    };
    
    // 解析METHOD
    const methodMatch = keyLine.match(/METHOD=([^,\s]+)/);
    if (methodMatch) {
      encryption.method = methodMatch[1];
    }
    
    // 解析URI
    const uriMatch = keyLine.match(/URI="([^"]+)"/);
    if (uriMatch) {
      encryption.uri = this.resolveUrl(uriMatch[1], baseUrl);
    }
    
    // 解析IV
    const ivMatch = keyLine.match(/IV=0x([0-9A-Fa-f]+)/);
    if (ivMatch) {
      encryption.iv = ivMatch[1];
    }
    
    return encryption;
  }
  
  getBaseUrl(url) {
    try {
      const urlObj = new URL(url);
      return `${urlObj.protocol}//${urlObj.host}${urlObj.pathname.substring(0, urlObj.pathname.lastIndexOf('/'))}`;
    } catch (error) {
      throw new Error(`无效的URL: ${url}`);
    }
  }
  
  resolveUrl(url, baseUrl) {
    try {
      // 如果是完整URL，直接返回
      if (url.startsWith('http://') || url.startsWith('https://')) {
        return url;
      }
      
      // 如果是相对路径
      if (url.startsWith('/')) {
        const urlObj = new URL(baseUrl);
        return `${urlObj.protocol}//${urlObj.host}${url}`;
      }
      
      // 相对于当前目录的路径
      return `${baseUrl}/${url}`;
    } catch (error) {
      throw new Error(`无法解析URL: ${url}`);
    }
  }
  
  // 验证M3U8内容是否有效
  validateM3U8(content) {
    const lines = content.split('\n');
    
    // 检查文件头
    if (!lines[0].trim().startsWith('#EXTM3U')) {
      return false;
    }
    
    // 检查是否包含视频片段
    const hasSegments = lines.some(line => 
      !line.trim().startsWith('#') && 
      line.trim().length > 0 && 
      (line.includes('.ts') || line.includes('.m4s') || line.includes('.mp4'))
    );
    
    return hasSegments;
  }
  
  // 估算总文件大小（基于片段数量和平均大小）
  estimateFileSize(segments, avgSegmentSize = 1024 * 1024) { // 默认1MB每片段
    return segments.length * avgSegmentSize;
  }
  
  // 获取视频质量信息（如果是主播放列表）
  parsePlaylist(content, baseUrl) {
    const lines = content.split('\n').map(line => line.trim()).filter(line => line);
    const playlists = [];
    let currentPlaylist = {};
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      
      if (line.startsWith('#EXT-X-STREAM-INF:')) {
        // 解析流信息
        const bandwidthMatch = line.match(/BANDWIDTH=(\d+)/);
        const resolutionMatch = line.match(/RESOLUTION=(\d+x\d+)/);
        const codecsMatch = line.match(/CODECS="([^"]+)"/);
        
        currentPlaylist = {
          bandwidth: bandwidthMatch ? parseInt(bandwidthMatch[1]) : 0,
          resolution: resolutionMatch ? resolutionMatch[1] : '',
          codecs: codecsMatch ? codecsMatch[1] : ''
        };
      } else if (!line.startsWith('#') && line.length > 0) {
        // 这是播放列表URL
        currentPlaylist.url = this.resolveUrl(line, baseUrl);
        playlists.push(currentPlaylist);
        currentPlaylist = {};
      }
    }
    
    return playlists;
  }
}

module.exports = M3U8Parser;
