<template>
  <div class="file-manager">
    <!-- 工具栏 -->
    <el-card class="toolbar-card" shadow="hover">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button type="primary" @click="refreshFiles">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
          <el-button 
            type="danger" 
            @click="deleteSelectedFiles"
            :disabled="selectedFiles.length === 0"
          >
            <el-icon><Delete /></el-icon>
            删除选中 ({{ selectedFiles.length }})
          </el-button>
          <el-button 
            type="warning"
            @click="toggleSelectAll"
          >
            {{ isAllSelected ? '取消全选' : '全选' }}
          </el-button>
        </div>
        
        <div class="toolbar-right">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索文件..."
            clearable
            style="width: 200px; margin-right: 10px;"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <el-select v-model="sortBy" placeholder="排序方式" style="width: 120px; margin-right: 10px;">
            <el-option label="名称" value="name" />
            <el-option label="大小" value="size" />
            <el-option label="修改时间" value="mtime" />
          </el-select>
          
          <el-button-group>
            <el-button 
              :type="viewMode === 'grid' ? 'primary' : ''"
              @click="viewMode = 'grid'"
            >
              <el-icon><Grid /></el-icon>
            </el-button>
            <el-button 
              :type="viewMode === 'list' ? 'primary' : ''"
              @click="viewMode = 'list'"
            >
              <el-icon><List /></el-icon>
            </el-button>
          </el-button-group>
        </div>
      </div>
    </el-card>

    <!-- 文件统计 -->
    <el-card class="stats-card" shadow="hover">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic title="文件总数" :value="filteredFiles.length" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="选中文件" :value="selectedFiles.length" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="总大小" :value="totalSizeFormatted.value" :suffix="totalSizeFormatted.suffix" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="可用空间" :value="availableSpaceFormatted.value" :suffix="availableSpaceFormatted.suffix" />
        </el-col>
      </el-row>
    </el-card>

    <!-- 文件列表 -->
    <el-card class="files-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>下载文件</span>
          <div class="header-info">
            共 {{ filteredFiles.length }} 个文件
          </div>
        </div>
      </template>

      <div v-if="loading" class="loading-container">
        <el-icon class="is-loading">
          <Loading />
        </el-icon>
        <p>正在加载文件列表...</p>
      </div>

      <div v-else-if="filteredFiles.length === 0" class="no-files">
        <el-empty description="暂无文件" />
      </div>

      <!-- 网格视图 -->
      <div v-else-if="viewMode === 'grid'" class="files-grid">
        <div
          v-for="file in paginatedFiles"
          :key="file.name"
          class="file-card"
          :class="{ 'selected': selectedFiles.includes(file.name) }"
          @click="toggleFileSelection(file.name)"
        >
          <div class="file-preview">
            <el-icon class="file-icon">
              <VideoPlay v-if="isVideoFile(file.name)" />
              <Document v-else />
            </el-icon>
          </div>
          
          <div class="file-info">
            <div class="file-name" :title="file.name">{{ file.name }}</div>
            <div class="file-meta">
              <span class="file-size">{{ formatFileSize(file.size) }}</span>
              <span class="file-date">{{ formatDate(file.mtime) }}</span>
            </div>
          </div>
          
          <div class="file-actions" @click.stop>
            <el-dropdown trigger="click">
              <el-button type="text" size="small">
                <el-icon><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="downloadFile(file.name)">
                    <el-icon><Download /></el-icon>
                    下载
                  </el-dropdown-item>
                  <el-dropdown-item @click="renameFile(file)">
                    <el-icon><Edit /></el-icon>
                    重命名
                  </el-dropdown-item>
                  <el-dropdown-item @click="deleteFile(file.name)" divided>
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>

      <!-- 列表视图 -->
      <el-table v-else v-loading="loading" :data="paginatedFiles" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        
        <el-table-column label="文件名" prop="name" min-width="200">
          <template #default="{ row }">
            <div class="file-name-cell">
              <el-icon class="file-icon">
                <VideoPlay v-if="isVideoFile(row.name)" />
                <Document v-else />
              </el-icon>
              <span :title="row.name">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="大小" prop="size" width="120" sortable>
          <template #default="{ row }">
            {{ formatFileSize(row.size) }}
          </template>
        </el-table-column>
        
        <el-table-column label="修改时间" prop="mtime" width="180" sortable>
          <template #default="{ row }">
            {{ formatDate(row.mtime) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="text" size="small" @click="downloadFile(row.name)">
              <el-icon><Download /></el-icon>
              下载
            </el-button>
            <el-button type="text" size="small" @click="renameFile(row)">
              <el-icon><Edit /></el-icon>
              重命名
            </el-button>
            <el-button type="text" size="small" @click="deleteFile(row.name)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div v-if="filteredFiles.length > pageSize" class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[20, 50, 100]"
          :total="filteredFiles.length"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 重命名对话框 -->
    <el-dialog v-model="renameDialogVisible" title="重命名文件" width="500px">
      <el-form :model="renameForm" :rules="renameRules" ref="renameFormRef">
        <el-form-item label="新文件名" prop="newName">
          <el-input
            v-model="renameForm.newName"
            placeholder="请输入新文件名"
            @keyup.enter="confirmRename"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="renameDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmRename">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh, Delete, Search, Grid, List, Download, Edit, MoreFilled,
  VideoPlay, Document, Loading
} from '@element-plus/icons-vue'
import { fileAPI } from '@/api'
import { formatFileSize, formatDate } from '@/utils'

// 响应式数据
const files = ref([])
const loading = ref(false)
const searchKeyword = ref('')
const sortBy = ref('name')
const viewMode = ref('grid')
const selectedFiles = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const availableSpace = ref(0)

// 重命名相关
const renameDialogVisible = ref(false)
const renameFormRef = ref(null)
const renameForm = reactive({
  oldName: '',
  newName: ''
})

const renameRules = {
  newName: [
    { required: true, message: '请输入新文件名', trigger: 'blur' },
    { min: 1, max: 255, message: '文件名长度应在 1 到 255 个字符', trigger: 'blur' }
  ]
}

// 计算属性
const filteredFiles = computed(() => {
  let result = files.value

  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(file => 
      file.name.toLowerCase().includes(keyword)
    )
  }

  // 排序
  result.sort((a, b) => {
    switch (sortBy.value) {
      case 'size':
        return b.size - a.size
      case 'mtime':
        return new Date(b.mtime) - new Date(a.mtime)
      default:
        return a.name.localeCompare(b.name)
    }
  })

  return result
})

const paginatedFiles = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredFiles.value.slice(start, end)
})

const totalSize = computed(() => {
  return files.value.reduce((sum, file) => sum + file.size, 0)
})

// 添加总大小的数值和单位计算属性
const totalSizeFormatted = computed(() => {
  if (totalSize.value === 0) return { value: 0, suffix: 'B' }
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(totalSize.value) / Math.log(k))
  
  return {
    value: parseFloat((totalSize.value / Math.pow(k, i)).toFixed(2)),
    suffix: sizes[i]
  }
})

// 添加可用空间的数值和单位计算属性
const availableSpaceFormatted = computed(() => {
  if (availableSpace.value === 0) return { value: 0, suffix: 'B' }
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(availableSpace.value) / Math.log(k))
  
  return {
    value: parseFloat((availableSpace.value / Math.pow(k, i)).toFixed(2)),
    suffix: sizes[i]
  }
})

const isAllSelected = computed(() => {
  return filteredFiles.value.length > 0 && 
         selectedFiles.value.length === filteredFiles.value.length
})

// 方法
const refreshFiles = async () => {
  loading.value = true
  try {
    const response = await fileAPI.getFiles()
    // axios拦截器已经返回response.data，所以这里直接使用response
    // Django REST框架返回分页格式：{count, next, previous, results}
    files.value = response.results || []
    availableSpace.value = response.availableSpace || 0
  } catch (error) {
    console.error('获取文件列表失败:', error)
    ElMessage.error('获取文件列表失败')
    // 即使API失败，也要设置默认值以保证组件能正常显示
    files.value = []
    availableSpace.value = 0
  } finally {
    loading.value = false
  }
}

const toggleFileSelection = (fileName) => {
  const index = selectedFiles.value.indexOf(fileName)
  if (index > -1) {
    selectedFiles.value.splice(index, 1)
  } else {
    selectedFiles.value.push(fileName)
  }
}

const handleSelectionChange = (selection) => {
  selectedFiles.value = selection.map(file => file.name)
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedFiles.value = []
  } else {
    selectedFiles.value = filteredFiles.value.map(file => file.name)
  }
}

const downloadFile = (fileName) => {
  const downloadUrl = `/api/files/download/${encodeURIComponent(fileName)}`
  const link = document.createElement('a')
  link.href = downloadUrl
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const deleteFile = async (fileName) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文件 "${fileName}" 吗？此操作不可恢复。`,
      '确认删除',
      { type: 'warning' }
    )
    
    await fileAPI.deleteFile(fileName)
    ElMessage.success('文件已删除')
    refreshFiles()
    
    // 从选中列表中移除
    const index = selectedFiles.value.indexOf(fileName)
    if (index > -1) {
      selectedFiles.value.splice(index, 1)
    }
  } catch (error) {
    if (error === 'cancel') return
    console.error('删除文件失败:', error)
    ElMessage.error('删除文件失败')
  }
}

const deleteSelectedFiles = async () => {
  if (selectedFiles.value.length === 0) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedFiles.value.length} 个文件吗？此操作不可恢复。`,
      '确认删除',
      { type: 'warning' }
    )
    
    for (const fileName of selectedFiles.value) {
      await fileAPI.deleteFile(fileName)
    }
    
    ElMessage.success(`已删除 ${selectedFiles.value.length} 个文件`)
    selectedFiles.value = []
    refreshFiles()
  } catch (error) {
    if (error === 'cancel') return
    console.error('批量删除文件失败:', error)
    ElMessage.error('批量删除文件失败')
  }
}

const renameFile = (file) => {
  renameForm.oldName = file.name
  renameForm.newName = file.name
  renameDialogVisible.value = true
}

const confirmRename = async () => {
  if (!renameFormRef.value) return
  
  try {
    await renameFormRef.value.validate()
    
    if (renameForm.oldName === renameForm.newName) {
      ElMessage.warning('新文件名与原文件名相同')
      return
    }
    
    await fileAPI.renameFile(renameForm.oldName, renameForm.newName)
    ElMessage.success('文件重命名成功')
    renameDialogVisible.value = false
    refreshFiles()
  } catch (error) {
    console.error('重命名文件失败:', error)
    ElMessage.error('重命名文件失败')
  }
}

const isVideoFile = (fileName) => {
  const videoExtensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.ts']
  return videoExtensions.some(ext => fileName.toLowerCase().endsWith(ext))
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

// 生命周期
onMounted(() => {
  refreshFiles()
})
</script>

<style scoped>
.file-manager {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.toolbar-card,
.stats-card,
.files-card {
  margin-bottom: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
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

.loading-container {
  text-align: center;
  padding: 40px 0;
  color: #909399;
}

.no-files {
  text-align: center;
  padding: 40px 0;
}

/* 网格视图样式 */
.files-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  padding: 20px 0;
}

.file-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.file-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #409eff;
}

.file-card.selected {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.file-preview {
  text-align: center;
  margin-bottom: 10px;
}

.file-icon {
  font-size: 48px;
  color: #409eff;
}

.file-info {
  text-align: center;
}

.file-name {
  font-weight: 600;
  margin-bottom: 5px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
}

.file-actions {
  position: absolute;
  top: 10px;
  right: 10px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.file-card:hover .file-actions {
  opacity: 1;
}

/* 列表视图样式 */
.file-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-name-cell .file-icon {
  font-size: 16px;
  color: #409eff;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .file-manager {
    padding: 10px;
  }
  
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .toolbar-left,
  .toolbar-right {
    justify-content: center;
  }
  
  .files-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 15px;
  }
}
</style>
