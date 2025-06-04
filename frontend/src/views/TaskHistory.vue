<template>
  <div class="task-history">
    <!-- 搜索和过滤工具栏 -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-toolbar">
        <div class="filter-left">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索任务..."
            clearable
            style="width: 250px; margin-right: 15px;"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <el-select
            v-model="statusFilter"
            placeholder="状态筛选"
            clearable
            style="width: 120px; margin-right: 15px;"
          >
            <el-option label="全部" value="" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
          
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 240px;"
          />
        </div>
        
        <div class="filter-right">
          <el-button type="primary" @click="refreshHistory">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
          <el-button type="warning" @click="exportHistory">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
          <el-button type="danger" @click="clearHistory">
            <el-icon><Delete /></el-icon>
            清空历史
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 统计信息 -->
    <el-card class="stats-card" shadow="hover">
      <el-row :gutter="20">
        <el-col :span="4">
          <el-statistic title="总任务数" :value="stats.total" />
        </el-col>
        <el-col :span="4">
          <el-statistic title="成功完成" :value="stats.completed" />
        </el-col>
        <el-col :span="4">
          <el-statistic title="失败任务" :value="stats.failed" />
        </el-col>
        <el-col :span="4">
          <el-statistic title="成功率" :value="stats.successRate" suffix="%" />
        </el-col>
        <el-col :span="4">
          <el-statistic title="总下载量" :value="totalSizeFormatted.value" :suffix="totalSizeFormatted.suffix" />
        </el-col>
        <el-col :span="4">
          <el-statistic title="平均速度" :value="avgSpeedFormatted.value" :suffix="avgSpeedFormatted.suffix" />
        </el-col>
      </el-row>
    </el-card>

    <!-- 任务历史列表 -->
    <el-card class="history-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>下载历史</span>
          <div class="header-info">
            共 {{ filteredHistory.length }} 条记录
          </div>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="paginatedHistory"
        :default-sort="{ prop: 'createdAt', order: 'descending' }"
        stripe
        @sort-change="handleSortChange"
      >
        <el-table-column label="任务ID" prop="id" width="200">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ row.id.slice(0, 8) }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="文件名" prop="filename" min-width="200">
          <template #default="{ row }">
            <div class="filename-cell">
              <el-icon class="file-icon">
                <VideoPlay />
              </el-icon>
              <span :title="row.filename">{{ row.filename || '未命名' }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="URL" prop="url" min-width="300">
          <template #default="{ row }">
            <el-tooltip :content="row.url" placement="top">
              <span class="url-text">{{ truncateUrl(row.url) }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" prop="status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="进度" prop="progress" width="120">
          <template #default="{ row }">
            <el-progress
              :percentage="row.progress || 0"
              :status="getProgressStatus(row.status)"
              :stroke-width="6"
              text-inside
            />
          </template>
        </el-table-column>
        
        <el-table-column label="文件大小" prop="fileSize" width="100" sortable>
          <template #default="{ row }">
            {{ row.fileSize ? formatFileSize(row.fileSize) : '-' }}
          </template>
        </el-table-column>
        
        <el-table-column label="下载速度" prop="averageSpeed" width="120" sortable>
          <template #default="{ row }">
            {{ row.averageSpeed ? formatSpeed(row.averageSpeed) : '-' }}
          </template>
        </el-table-column>
        
        <el-table-column label="耗时" prop="duration" width="100" sortable>
          <template #default="{ row }">
            {{ row.duration ? formatDuration(row.duration) : '-' }}
          </template>
        </el-table-column>
        
        <el-table-column label="开始时间" prop="createdAt" width="160" sortable>
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>
        
        <el-table-column label="完成时间" prop="completedAt" width="160" sortable>
          <template #default="{ row }">
            {{ row.completedAt ? formatDate(row.completedAt) : '-' }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'completed' && row.filePath"
              type="text"
              size="small"
              @click="downloadFile(row.filePath)"
            >
              <el-icon><Download /></el-icon>
              下载
            </el-button>
            <el-button
              v-if="['failed', 'cancelled'].includes(row.status)"
              type="text"
              size="small"
              @click="retryTask(row)"
            >
              <el-icon><RefreshRight /></el-icon>
              重试
            </el-button>
            <el-button
              type="text"
              size="small"
              @click="viewTaskDetails(row)"
            >
              <el-icon><View /></el-icon>
              详情
            </el-button>
            <el-button
              type="text"
              size="small"
              @click="deleteTask(row.id)"
              style="color: #f56c6c;"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[20, 50, 100, 200]"
          :total="filteredHistory.length"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 任务详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="任务详情" width="80%">
      <div v-if="selectedTask" class="task-details">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务ID">
            {{ selectedTask.id }}
          </el-descriptions-item>
          <el-descriptions-item label="文件名">
            {{ selectedTask.filename || '未命名' }}
          </el-descriptions-item>
          <el-descriptions-item label="M3U8 URL" :span="2">
            <el-link :href="selectedTask.url" type="primary" target="_blank">
              {{ selectedTask.url }}
            </el-link>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedTask.status)">
              {{ getStatusText(selectedTask.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="进度">
            {{ selectedTask.progress || 0 }}%
          </el-descriptions-item>
          <el-descriptions-item label="总片段数">
            {{ selectedTask.totalSegments || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="已下载片段">
            {{ selectedTask.downloadedSegments || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="文件大小">
            {{ selectedTask.fileSize ? formatFileSize(selectedTask.fileSize) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="平均速度">
            {{ selectedTask.averageSpeed ? formatSpeed(selectedTask.averageSpeed) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="并发数">
            {{ selectedTask.concurrency || 3 }}
          </el-descriptions-item>
          <el-descriptions-item label="输出目录">
            {{ selectedTask.outputDir || 'downloads' }}
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ formatDate(selectedTask.createdAt) }}
          </el-descriptions-item>
          <el-descriptions-item label="完成时间">
            {{ selectedTask.completedAt ? formatDate(selectedTask.completedAt) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="耗时">
            {{ selectedTask.duration ? formatDuration(selectedTask.duration) : '-' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div v-if="selectedTask.error" class="error-info">
          <h4>错误信息</h4>
          <el-alert
            :title="selectedTask.error"
            type="error"
            :closable="false"
            show-icon
          />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Refresh, Download, Delete, VideoPlay, RefreshRight, View
} from '@element-plus/icons-vue'
import { taskAPI, downloadAPI } from '@/api'
import { formatFileSize, formatSpeed, formatDate } from '@/utils'

// 响应式数据
const history = ref([])
const loading = ref(false)
const searchKeyword = ref('')
const statusFilter = ref('')
const dateRange = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const sortConfig = reactive({
  prop: 'createdAt',
  order: 'descending'
})

// 详情对话框
const detailDialogVisible = ref(false)
const selectedTask = ref(null)

// 计算属性
const filteredHistory = computed(() => {
  let result = history.value

  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(task => 
      (task.filename && task.filename.toLowerCase().includes(keyword)) ||
      task.url.toLowerCase().includes(keyword) ||
      task.id.toLowerCase().includes(keyword)
    )
  }

  // 状态过滤
  if (statusFilter.value) {
    result = result.filter(task => task.status === statusFilter.value)
  }

  // 日期范围过滤
  if (dateRange.value && dateRange.value.length === 2) {
    const [startDate, endDate] = dateRange.value
    result = result.filter(task => {
      const taskDate = new Date(task.createdAt).toISOString().split('T')[0]
      return taskDate >= startDate && taskDate <= endDate
    })
  }

  // 排序
  result.sort((a, b) => {
    const { prop, order } = sortConfig
    let aVal = a[prop]
    let bVal = b[prop]
    
    if (prop === 'createdAt' || prop === 'completedAt') {
      aVal = new Date(aVal || 0)
      bVal = new Date(bVal || 0)
    }
    
    if (order === 'ascending') {
      return aVal > bVal ? 1 : -1
    } else {
      return aVal < bVal ? 1 : -1
    }
  })

  return result
})

const paginatedHistory = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredHistory.value.slice(start, end)
})

const stats = computed(() => {
  const total = history.value.length
  const completed = history.value.filter(t => t.status === 'completed').length
  const failed = history.value.filter(t => t.status === 'failed').length
  const successRate = total > 0 ? Math.round((completed / total) * 100) : 0
  const totalSize = history.value
    .filter(t => t.fileSize)
    .reduce((sum, task) => sum + task.fileSize, 0)
  const avgSpeed = completed > 0 
    ? history.value
        .filter(t => t.averageSpeed)
        .reduce((sum, task) => sum + task.averageSpeed, 0) / completed
    : 0

  return {
    total,
    completed,
    failed,
    successRate,
    totalSize,
    avgSpeed
  }
})

// 格式化总下载量的计算属性
const totalSizeFormatted = computed(() => {
  if (stats.value.totalSize === 0) return { value: 0, suffix: 'B' }
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(stats.value.totalSize) / Math.log(k))
  
  return {
    value: parseFloat((stats.value.totalSize / Math.pow(k, i)).toFixed(2)),
    suffix: sizes[i]
  }
})

// 格式化平均速度的计算属性
const avgSpeedFormatted = computed(() => {
  if (!stats.value.avgSpeed || stats.value.avgSpeed === 0) return { value: 0, suffix: 'B/s' }
  
  const k = 1024
  const sizes = ['B/s', 'KB/s', 'MB/s', 'GB/s']
  const i = Math.floor(Math.log(stats.value.avgSpeed) / Math.log(k))
  
  return {
    value: parseFloat((stats.value.avgSpeed / Math.pow(k, i)).toFixed(2)),
    suffix: sizes[i]
  }
})

// 方法
const refreshHistory = async () => {
  loading.value = true
  try {
    const response = await taskAPI.getHistory()
    // axios拦截器已经返回response.data，所以这里直接使用response
    // Django REST框架返回分页格式：{count, next, previous, results}
    history.value = response.results || []
  } catch (error) {
    console.error('获取任务历史失败:', error)
    ElMessage.error('获取任务历史失败')
    // 即使API失败，也要设置默认值以保证组件能正常显示
    history.value = []
  } finally {
    loading.value = false
  }
}

const handleSortChange = ({ prop, order }) => {
  sortConfig.prop = prop
  sortConfig.order = order
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

const getStatusType = (status) => {
  const statusMap = {
    completed: 'success',
    failed: 'danger',
    cancelled: 'warning'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return statusMap[status] || '未知'
}

const getProgressStatus = (status) => {
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  return null
}

const truncateUrl = (url) => {
  if (url.length <= 50) return url
  return url.substring(0, 47) + '...'
}

const formatDuration = (seconds) => {
  if (!seconds) return '-'
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`
  } else {
    return `${secs}s`
  }
}

const downloadFile = (filePath) => {
  const fileName = filePath.split('/').pop()
  const downloadUrl = `/api/files/download/${encodeURIComponent(fileName)}`
  const link = document.createElement('a')
  link.href = downloadUrl
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const retryTask = async (task) => {
  try {
    await downloadAPI.startDownload({
      url: task.url,
      filename: task.filename,
      outputDir: task.outputDir,
      concurrency: task.concurrency
    })
    ElMessage.success('任务重试已开始')
  } catch (error) {
    console.error('重试任务失败:', error)
    ElMessage.error('重试任务失败')
  }
}

const viewTaskDetails = (task) => {
  selectedTask.value = task
  detailDialogVisible.value = true
}

const deleteTask = async (taskId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个任务记录吗？', '确认删除', {
      type: 'warning'
    })
    
    await taskAPI.deleteTask(taskId)
    ElMessage.success('任务记录已删除')
    refreshHistory()
  } catch (error) {
    if (error === 'cancel') return
    console.error('删除任务失败:', error)
    ElMessage.error('删除任务失败')
  }
}

const clearHistory = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有历史记录吗？此操作不可恢复。', '确认清空', {
      type: 'warning'
    })
    
    await taskAPI.clearHistory()
    ElMessage.success('历史记录已清空')
    history.value = []
  } catch (error) {
    if (error === 'cancel') return
    console.error('清空历史失败:', error)
    ElMessage.error('清空历史失败')
  }
}

const exportHistory = async () => {
  try {
    const response = await taskAPI.exportHistory()
    // axios拦截器已经返回response.data，所以这里直接使用response
    const blob = new Blob([JSON.stringify(response, null, 2)], {
      type: 'application/json'
    })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `download-history-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    ElMessage.success('历史记录已导出')
  } catch (error) {
    console.error('导出历史失败:', error)
    ElMessage.error('导出历史失败')
  }
}

// 生命周期
onMounted(() => {
  refreshHistory()
})
</script>

<style scoped>
.task-history {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.filter-card,
.stats-card,
.history-card {
  margin-bottom: 20px;
}

.filter-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.filter-left,
.filter-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-info {
  color: #909399;
  font-size: 14px;
}

.filename-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  color: #409eff;
  font-size: 16px;
}

.url-text {
  color: #909399;
  font-size: 12px;
  font-family: monospace;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.task-details {
  max-height: 60vh;
  overflow-y: auto;
}

.error-info {
  margin-top: 20px;
}

.error-info h4 {
  margin-bottom: 10px;
  color: #f56c6c;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .task-history {
    padding: 10px;
  }
  
  .filter-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-left,
  .filter-right {
    justify-content: center;
    flex-wrap: wrap;
  }
}
</style>
