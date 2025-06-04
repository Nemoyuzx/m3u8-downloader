import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    
    let message = '请求失败'
    if (error.response) {
      message = error.response.data?.error || `请求失败 (${error.response.status})`
    } else if (error.request) {
      message = '网络连接失败'
    } else {
      message = error.message
    }
    
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// 下载相关API
export const downloadAPI = {
  // 开始下载
  startDownload: (params) => api.post('/tasks/', params),
  
  // 获取任务列表
  getTasks: () => api.get('/tasks/'),
  
  // 暂停任务
  pauseDownload: (taskId) => api.post(`/tasks/${taskId}/pause/`),
  
  // 继续任务
  resumeDownload: (taskId) => api.post(`/tasks/${taskId}/resume/`),
  
  // 重试任务
  retryDownload: (taskId) => api.post(`/tasks/${taskId}/retry/`),
  
  // 取消任务
  cancelDownload: (taskId) => api.post(`/tasks/${taskId}/cancel/`)
}

// 文件管理API
export const fileAPI = {
  // 获取文件列表
  getFiles: () => api.get('/files/'),
  
  // 删除文件
  deleteFile: (fileId) => api.delete(`/files/${fileId}/`),
  
  // 重命名文件
  renameFile: (fileId, newName) => api.post(`/files/${fileId}/file_action/`, { 
    action: 'rename', 
    new_name: newName 
  }),
  
  // 获取文件信息
  getFileInfo: (fileId) => api.get(`/files/${fileId}/`)
}

// 任务历史API
export const taskAPI = {
  // 获取任务历史
  getHistory: () => api.get('/history/'),
  
  // 获取任务详情
  getTask: (taskId) => api.get(`/tasks/${taskId}/`),
  
  // 删除任务记录
  deleteTask: (taskId) => api.delete(`/tasks/${taskId}/`),
  
  // 清空任务历史
  clearHistory: () => api.delete('/history/cleanup_old/'),
  
  // 获取任务统计
  getStats: () => api.get('/files/stats/'),
  
  // 导出任务历史
  exportHistory: () => api.get('/history/recent/')
}

export default api
