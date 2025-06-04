class DownloadTask {
  constructor(options) {
    this.id = options.id;
    this.url = options.url;
    this.title = options.title;
    this.convertToMp4 = options.convertToMp4 || false;
    this.startSegment = options.startSegment;
    this.endSegment = options.endSegment;
    this.status = options.status || 'pending'; // pending, parsing, downloading, paused, merging, completed, error, cancelled
    this.createdAt = new Date();
    this.updatedAt = new Date();
    
    // 下载进度相关
    this.segments = [];
    this.totalSegments = 0;
    this.downloadedSegments = 0;
    this.failedSegments = [];
    this.progress = 0;
    
    // 文件相关
    this.tempDir = '';
    this.outputFile = '';
    this.fileSize = 0;
    
    // 加密相关
    this.encryption = null;
    this.encryptionKey = null;
    
    // 错误信息
    this.error = null;
    
    // 下载速度统计
    this.downloadSpeed = 0;
    this.lastDownloadTime = Date.now();
    this.lastDownloadedBytes = 0;
  }
  
  // 更新状态
  updateStatus(status) {
    this.status = status;
    this.updatedAt = new Date();
    this.calculateProgress();
  }
  
  // 计算进度
  calculateProgress() {
    if (this.totalSegments === 0) {
      this.progress = 0;
    } else {
      this.progress = Math.round((this.downloadedSegments / this.totalSegments) * 100);
    }
  }
  
  // 计算下载速度
  calculateSpeed(downloadedBytes) {
    const now = Date.now();
    const timeDiff = now - this.lastDownloadTime;
    
    if (timeDiff >= 1000) { // 每秒更新一次速度
      const bytesDiff = downloadedBytes - this.lastDownloadedBytes;
      this.downloadSpeed = Math.round(bytesDiff / (timeDiff / 1000)); // bytes per second
      this.lastDownloadTime = now;
      this.lastDownloadedBytes = downloadedBytes;
    }
  }
  
  // 暂停任务
  pause() {
    if (this.status === 'downloading') {
      this.status = 'paused';
      this.updatedAt = new Date();
    }
  }
  
  // 恢复任务
  resume() {
    if (this.status === 'paused') {
      this.status = 'downloading';
      this.updatedAt = new Date();
    }
  }
  
  // 取消任务
  cancel() {
    this.status = 'cancelled';
    this.updatedAt = new Date();
  }
  
  // 重试失败的片段
  retryFailedSegments() {
    this.failedSegments = [];
    this.status = 'downloading';
    this.updatedAt = new Date();
  }
  
  // 获取任务状态信息
  getStatus() {
    return {
      id: this.id,
      url: this.url,
      title: this.title,
      status: this.status,
      progress: this.progress,
      totalSegments: this.totalSegments,
      downloadedSegments: this.downloadedSegments,
      failedSegments: this.failedSegments.length,
      downloadSpeed: this.downloadSpeed,
      fileSize: this.fileSize,
      outputFile: this.outputFile,
      createdAt: this.createdAt,
      updatedAt: this.updatedAt,
      error: this.error,
      convertToMp4: this.convertToMp4
    };
  }
  
  // 获取预计剩余时间
  getEstimatedTimeRemaining() {
    if (this.downloadSpeed === 0 || this.progress === 100) {
      return 0;
    }
    
    const remainingSegments = this.totalSegments - this.downloadedSegments;
    const avgBytesPerSegment = this.fileSize / this.totalSegments || 1000000; // 假设每个片段1MB
    const remainingBytes = remainingSegments * avgBytesPerSegment;
    
    return Math.round(remainingBytes / this.downloadSpeed); // seconds
  }
  
  // 格式化文件大小
  static formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
  
  // 格式化下载速度
  formatDownloadSpeed() {
    return DownloadTask.formatFileSize(this.downloadSpeed) + '/s';
  }
  
  // 格式化时间
  static formatTime(seconds) {
    if (seconds < 60) {
      return `${seconds}秒`;
    } else if (seconds < 3600) {
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = seconds % 60;
      return `${minutes}分${remainingSeconds}秒`;
    } else {
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      return `${hours}时${minutes}分`;
    }
  }
  
  // 获取格式化的预计剩余时间
  getFormattedEstimatedTime() {
    const seconds = this.getEstimatedTimeRemaining();
    return DownloadTask.formatTime(seconds);
  }
}

module.exports = DownloadTask;
