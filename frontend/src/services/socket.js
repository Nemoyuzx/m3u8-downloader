import { io } from 'socket.io-client'

class SocketService {
  constructor() {
    this.socket = null
    this.listeners = new Map()
  }
  
  connect(url = 'http://localhost:3000') {
    if (this.socket?.connected) {
      return this.socket
    }
    
    this.socket = io(url, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
      maxReconnectionAttempts: 5
    })
    
    this.socket.on('connect', () => {
      console.log('Socket connected:', this.socket.id)
    })
    
    this.socket.on('disconnect', (reason) => {
      console.log('Socket disconnected:', reason)
    })
    
    this.socket.on('connect_error', (error) => {
      console.error('Socket connection error:', error)
    })
    
    return this.socket
  }
  
  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }
  
  // 加入任务房间，接收特定任务的更新
  joinTask(taskId) {
    if (this.socket) {
      this.socket.emit('joinTask', taskId)
    }
  }
  
  // 通用的事件监听方法
  on(event, callback) {
    if (this.socket) {
      this.socket.on(event, callback)
      this.listeners.set(event, callback)
    }
  }
  
  // 通用的移除监听方法
  off(event, callback) {
    if (this.socket && this.listeners.has(event)) {
      this.socket.off(event, callback || this.listeners.get(event))
      this.listeners.delete(event)
    }
  }
  
  // 监听进度更新
  onProgress(callback) {
    if (this.socket) {
      this.socket.on('progress', callback)
      this.listeners.set('progress', callback)
    }
  }
  
  // 移除进度监听
  offProgress() {
    if (this.socket && this.listeners.has('progress')) {
      this.socket.off('progress', this.listeners.get('progress'))
      this.listeners.delete('progress')
    }
  }
  
  // 监听任务完成
  onTaskComplete(callback) {
    if (this.socket) {
      this.socket.on('taskComplete', callback)
      this.listeners.set('taskComplete', callback)
    }
  }
  
  // 移除任务完成监听
  offTaskComplete() {
    if (this.socket && this.listeners.has('taskComplete')) {
      this.socket.off('taskComplete', this.listeners.get('taskComplete'))
      this.listeners.delete('taskComplete')
    }
  }
  
  // 监听错误
  onError(callback) {
    if (this.socket) {
      this.socket.on('error', callback)
      this.listeners.set('error', callback)
    }
  }
  
  // 移除错误监听
  offError() {
    if (this.socket && this.listeners.has('error')) {
      this.socket.off('error', this.listeners.get('error'))
      this.listeners.delete('error')
    }
  }
  
  // 清理所有监听器
  clearListeners() {
    if (this.socket) {
      this.listeners.forEach((callback, event) => {
        this.socket.off(event, callback)
      })
      this.listeners.clear()
    }
  }
  
  // 获取连接状态
  isConnected() {
    return this.socket?.connected || false
  }
}

// 创建单例实例
const socketService = new SocketService()

export default socketService
