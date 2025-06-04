<template>
  <div class="download-center">
    <!-- 添加新下载任务 -->
    <el-card class="add-task-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>添加下载任务</span>
        </div>
      </template>
      
      <el-form :model="newTask" :rules="rules" ref="taskForm" label-width="100px">
        <el-form-item label="M3U8 URL" prop="url">
          <el-input
            v-model="newTask.url"
            placeholder="请输入M3U8播放列表URL"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="文件名" prop="filename">
          <el-input
            v-model="newTask.filename"
            placeholder="请输入文件名（可选，不带扩展名）"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="下载目录" prop="outputDir">
          <el-input
            v-model="newTask.outputDir"
            placeholder="下载保存目录（可选，默认为downloads）"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="并发数">
          <el-slider
            v-model="newTask.concurrency"
            :min="1"
            :max="10"
            :step="1"
            show-input
            input-size="small"
            style="width: 300px"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="startDownload"
            :loading="downloading"
          >
            {{ downloading ? '正在添加...' : '开始下载' }}
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 当前下载任务列表 -->
    <el-card class="tasks-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>下载任务列表</span>
          <div class="header-actions">
            <el-button size="small" @click="refreshTasks">刷新</el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="clearCompletedTasks"
              :disabled="!hasCompletedTasks"
            >
              清理已完成
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="tasks.length === 0" class="no-tasks">
        <el-empty description="暂无下载任务" />
      </div>

      <div v-else class="tasks-list">
        <div
          v-for="task in tasks"
          :key="task.id"
          class="task-item"
          :class="{ 'task-completed': task.status === 'completed' }"
        >
          <div class="task-info">
            <div class="task-title">
              <el-icon class="task-icon">
                <VideoPlay v-if="task.status === 'downloading'" />
                <Check v-else-if="task.status === 'completed'" />
                <Close v-else-if="task.status === 'failed'" />
                <Loading v-else />
              </el-icon>
              <span class="filename">{{ task.filename || '未命名' }}</span>
              <el-tag 
                :type="getStatusType(task.status)" 
                size="small"
                class="status-tag"
              >
                {{ getStatusText(task.status) }}
              </el-tag>
            </div>
            
            <div class="task-url">{{ task.url }}</div>
            
            <div class="task-progress">
              <el-progress
                :percentage="task.progress"
                :status="getProgressStatus(task.status)"
                :stroke-width="8"
              />
              <div class="progress-info">
                <span>{{ task.downloadedSegments || 0 }} / {{ task.totalSegments || 0 }} 片段</span>
                <span v-if="task.speed">{{ formatSpeed(task.speed) }}</span>
                <span v-if="task.estimatedTime">剩余: {{ formatTime(task.estimatedTime) }}</span>
              </div>
            </div>
          </div>
          
          <div class="task-actions">
            <el-button 
              v-if="task.status === 'paused'"
              size="small" 
              type="primary"
              @click="resumeTask(task.id)"
            >
              继续
            </el-button>
            <el-button 
              v-if="task.status === 'downloading'"
              size="small" 
              type="warning"
              @click="pauseTask(task.id)"
            >
              暂停
            </el-button>
            <el-button 
              v-if="['failed', 'paused'].includes(task.status)"
              size="small" 
              type="success"
              @click="retryTask(task.id)"
            >
              重试
            </el-button>
            <el-button 
              size="small" 
              type="danger"
              @click="cancelTask(task.id)"
            >
              取消
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 全局统计信息 -->
    <el-card class="stats-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>下载统计</span>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic title="总任务数" :value="stats.totalTasks" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="下载中" :value="stats.downloadingTasks" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="已完成" :value="stats.completedTasks" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="总下载速度" :value="stats.totalSpeed" suffix=" B/s" />
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VideoPlay, Check, Close, Loading } from '@element-plus/icons-vue'
import { downloadAPI } from '@/api'
import socketService from '@/services/socket'
import { formatSpeed, formatTime } from '@/utils'

// 响应式数据
const tasks = ref([])
const downloading = ref(false)
const taskForm = ref(null)

// 新任务表单
const newTask = reactive({
  url: '',
  filename: '',
  outputDir: '',
  concurrency: 3
})

// 表单验证规则
const rules = {
  url: [
    { required: true, message: '请输入M3U8 URL', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL', trigger: 'blur' }
  ]
}

// 统计信息
const stats = computed(() => {
  const totalTasks = tasks.value.length
  const downloadingTasks = tasks.value.filter(t => t.status === 'downloading').length
  const completedTasks = tasks.value.filter(t => t.status === 'completed').length
  const totalSpeed = tasks.value
    .filter(t => t.status === 'downloading')
    .reduce((sum, task) => sum + (task.speed || 0), 0)
  
  return {
    totalTasks,
    downloadingTasks,
    completedTasks,
    totalSpeed
  }
})

// 是否有已完成的任务
const hasCompletedTasks = computed(() => 
  tasks.value.some(task => task.status === 'completed')
)

// 获取任务状态对应的标签类型
const getStatusType = (status) => {
  const statusMap = {
    downloading: 'primary',
    completed: 'success',
    failed: 'danger',
    paused: 'warning',
    pending: 'info'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    downloading: '下载中',
    completed: '已完成',
    failed: '失败',
    paused: '已暂停',
    pending: '等待中'
  }
  return statusMap[status] || '未知'
}

// 获取进度条状态
const getProgressStatus = (status) => {
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  return null
}

// 开始下载
const startDownload = async () => {
  if (!taskForm.value) return
  
  try {
    await taskForm.value.validate()
    downloading.value = true
    
    const response = await downloadAPI.startDownload({
      url: newTask.url,
      filename: newTask.filename || undefined,
      outputDir: newTask.outputDir || undefined,
      concurrency: newTask.concurrency
    })
    
    ElMessage.success('下载任务已添加')
    resetForm()
    refreshTasks()
  } catch (error) {
    console.error('启动下载失败:', error)
    ElMessage.error(error.message || '启动下载失败')
  } finally {
    downloading.value = false
  }
}

// 重置表单
const resetForm = () => {
  if (taskForm.value) {
    taskForm.value.resetFields()
  }
  Object.assign(newTask, {
    url: '',
    filename: '',
    outputDir: '',
    concurrency: 3
  })
}

// 刷新任务列表
const refreshTasks = async () => {
  try {
    const response = await downloadAPI.getTasks()
    // 只显示未取消的任务
    tasks.value = (response.results || []).filter(t => t.status !== 'cancelled')
  } catch (error) {
    console.error('获取任务列表失败:', error)
    ElMessage.error('获取任务列表失败')
    // 设置默认值以保证组件能正常显示
    tasks.value = []
  }
}

// 暂停任务
const pauseTask = async (taskId) => {
  try {
    await downloadAPI.pauseDownload(taskId)
    ElMessage.success('任务已暂停')
  } catch (error) {
    console.error('暂停任务失败:', error)
    ElMessage.error('暂停任务失败')
  }
}

// 继续任务
const resumeTask = async (taskId) => {
  try {
    await downloadAPI.resumeDownload(taskId)
    ElMessage.success('任务已继续')
  } catch (error) {
    console.error('继续任务失败:', error)
    ElMessage.error('继续任务失败')
  }
}

// 重试任务
const retryTask = async (taskId) => {
  try {
    await downloadAPI.retryDownload(taskId)
    ElMessage.success('任务重试已开始')
  } catch (error) {
    console.error('重试任务失败:', error)
    ElMessage.error('重试任务失败')
  }
}

// 取消任务
const cancelTask = async (taskId) => {
  try {
    await ElMessageBox.confirm('确定要取消这个下载任务吗？', '确认取消', {
      type: 'warning'
    })
    
    await downloadAPI.cancelDownload(taskId)
    ElMessage.success('任务已取消')
    refreshTasks() // 取消后自动刷新
  } catch (error) {
    if (error === 'cancel') return
    console.error('取消任务失败:', error)
    ElMessage.error('取消任务失败')
  }
}

// 清理已完成的任务
const clearCompletedTasks = async () => {
  try {
    await ElMessageBox.confirm('确定要清理所有已完成的任务吗？', '确认清理', {
      type: 'warning'
    })
    
    const completedTaskIds = tasks.value
      .filter(task => task.status === 'completed')
      .map(task => task.id)
    
    for (const taskId of completedTaskIds) {
      await downloadAPI.cancelDownload(taskId)
    }
    
    ElMessage.success('已完成任务已清理')
    refreshTasks() // 清理后自动刷新
  } catch (error) {
    if (error === 'cancel') return
    console.error('清理任务失败:', error)
    ElMessage.error('清理任务失败')
  }
}

// Socket事件处理
const handleTaskProgress = (data) => {
  const taskIndex = tasks.value.findIndex(task => task.id === data.taskId)
  if (taskIndex !== -1) {
    tasks.value[taskIndex] = { ...tasks.value[taskIndex], ...data }
  }
}

const handleTaskComplete = (data) => {
  const taskIndex = tasks.value.findIndex(task => task.id === data.taskId)
  if (taskIndex !== -1) {
    tasks.value[taskIndex] = { ...tasks.value[taskIndex], ...data, status: 'completed' }
  }
  ElMessage.success(`任务 "${data.filename}" 下载完成`)
}

const handleTaskError = (data) => {
  const taskIndex = tasks.value.findIndex(task => task.id === data.taskId)
  if (taskIndex !== -1) {
    tasks.value[taskIndex] = { ...tasks.value[taskIndex], ...data, status: 'failed' }
  }
  ElMessage.error(`任务 "${data.filename}" 下载失败: ${data.error}`)
}

// 生命周期
onMounted(() => {
  refreshTasks()
  
  // TODO: 实现WebSocket连接以接收实时进度更新
  // 暂时注释掉Socket.IO代码，因为后端使用Django Channels WebSocket
  // socketService.connect('http://localhost:8000')
  // socketService.on('downloadProgress', handleTaskProgress)
  // socketService.on('downloadComplete', handleTaskComplete)
  // socketService.on('downloadError', handleTaskError)
})

onUnmounted(() => {
  // TODO: 清理WebSocket连接
  // 暂时注释掉Socket.IO代码
  // socketService.off('downloadProgress', handleTaskProgress)
  // socketService.off('downloadComplete', handleTaskComplete)
  // socketService.off('downloadError', handleTaskError)
})
</script>

<style scoped>
.download-center {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.add-task-card,
.tasks-card,
.stats-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.no-tasks {
  text-align: center;
  padding: 40px 0;
}

.tasks-list {
  max-height: 600px;
  overflow-y: auto;
}

.task-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 15px;
  transition: all 0.3s ease;
}

.task-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #409eff;
}

.task-completed {
  background-color: #f0f9ff;
  border-color: #67c23a;
}

.task-info {
  flex: 1;
  margin-right: 20px;
}

.task-title {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.task-icon {
  margin-right: 8px;
  font-size: 16px;
}

.filename {
  font-weight: 600;
  margin-right: 10px;
  color: #303133;
}

.status-tag {
  margin-left: auto;
}

.task-url {
  color: #909399;
  font-size: 12px;
  margin-bottom: 10px;
  word-break: break-all;
}

.task-progress {
  margin-top: 10px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-top: 5px;
  font-size: 12px;
  color: #909399;
}

.task-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 80px;
}

@media (max-width: 768px) {
  .download-center {
    padding: 10px;
  }
  
  .task-item {
    flex-direction: column;
    align-items: stretch;
  }
  
  .task-info {
    margin-right: 0;
    margin-bottom: 15px;
  }
  
  .task-actions {
    flex-direction: row;
    justify-content: flex-end;
  }
}
</style>
