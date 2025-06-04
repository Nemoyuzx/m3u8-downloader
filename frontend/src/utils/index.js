// 格式化文件大小
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化时间
export function formatTime(seconds) {
  if (seconds < 60) {
    return `${seconds}秒`
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}分${remainingSeconds}秒`
  } else {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}时${minutes}分`
  }
}

// 格式化日期时间
export function formatDateTime(date) {
  if (!date) return ''
  
  const d = new Date(date)
  const now = new Date()
  const diff = now - d
  
  // 小于1分钟
  if (diff < 60000) {
    return '刚刚'
  }
  
  // 小于1小时
  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000)
    return `${minutes}分钟前`
  }
  
  // 小于1天
  if (diff < 86400000) {
    const hours = Math.floor(diff / 3600000)
    return `${hours}小时前`
  }
  
  // 大于1天，显示具体日期
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化下载速度
export function formatSpeed(bytesPerSecond) {
  if (!bytesPerSecond || bytesPerSecond === 0) return '0 B/s'
  
  const k = 1024
  const sizes = ['B/s', 'KB/s', 'MB/s', 'GB/s']
  const i = Math.floor(Math.log(bytesPerSecond) / Math.log(k))
  
  return parseFloat((bytesPerSecond / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化日期（简化版本）
export function formatDate(date) {
  if (!date) return ''
  
  const d = new Date(date)
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 验证URL
export function isValidUrl(string) {
  try {
    const url = new URL(string)
    return url.protocol === 'http:' || url.protocol === 'https:'
  } catch {
    return false
  }
}

// 验证M3U8 URL
export function isM3U8Url(url) {
  if (!isValidUrl(url)) return false
  
  const urlObj = new URL(url)
  const pathname = urlObj.pathname.toLowerCase()
  
  return pathname.endsWith('.m3u8') || pathname.includes('m3u8') || url.includes('m3u8')
}

// 获取文件扩展名
export function getFileExtension(filename) {
  return filename.slice((filename.lastIndexOf('.') - 1 >>> 0) + 2)
}

// 生成唯一ID
export function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

// 深拷贝
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj.getTime())
  if (obj instanceof Array) return obj.map(item => deepClone(item))
  if (typeof obj === 'object') {
    const cloned = {}
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        cloned[key] = deepClone(obj[key])
      }
    }
    return cloned
  }
}

// 防抖函数
export function debounce(func, wait, immediate = false) {
  let timeout
  return function (...args) {
    const later = () => {
      timeout = null
      if (!immediate) func.apply(this, args)
    }
    const callNow = immediate && !timeout
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
    if (callNow) func.apply(this, args)
  }
}

// 节流函数
export function throttle(func, wait) {
  let timeout
  return function (...args) {
    if (!timeout) {
      timeout = setTimeout(() => {
        timeout = null
        func.apply(this, args)
      }, wait)
    }
  }
}

// 获取状态文本
export function getStatusText(status) {
  const statusMap = {
    'pending': '等待中',
    'parsing': '解析中',
    'downloading': '下载中',
    'paused': '已暂停',
    'merging': '合并中',
    'completed': '已完成',
    'error': '下载失败',
    'cancelled': '已取消'
  }
  return statusMap[status] || status
}

// 获取状态类型
export function getStatusType(status) {
  const typeMap = {
    'pending': 'info',
    'parsing': 'info',
    'downloading': 'primary',
    'paused': 'warning',
    'merging': 'primary',
    'completed': 'success',
    'error': 'danger',
    'cancelled': 'info'
  }
  return typeMap[status] || 'info'
}

// 复制到剪贴板
export async function copyToClipboard(text) {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text)
    } else {
      // 回退方案
      const textArea = document.createElement('textarea')
      textArea.value = text
      textArea.style.position = 'fixed'
      textArea.style.left = '-999999px'
      textArea.style.top = '-999999px'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      document.execCommand('copy')
      textArea.remove()
    }
    return true
  } catch (err) {
    console.error('复制失败:', err)
    return false
  }
}

// 下载Blob文件
export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

// 获取视频标题（从URL中提取）
export function extractTitleFromUrl(url) {
  try {
    const urlObj = new URL(url)
    const pathname = urlObj.pathname
    
    // 提取文件名（不含扩展名）
    const filename = pathname.split('/').pop().split('.')[0]
    
    if (filename && filename !== 'index') {
      return filename
    }
    
    // 如果没有合适的文件名，使用域名
    return urlObj.hostname.replace(/^www\./, '')
  } catch {
    return `video_${Date.now()}`
  }
}
