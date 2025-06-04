<template>
  <div class="file-manager">
    <h1>文件管理页面</h1>
    <el-card class="toolbar-card" shadow="hover">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button type="primary">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
          <el-button type="danger">
            <el-icon><Delete /></el-icon>
            删除选中
          </el-button>
        </div>
      </div>
    </el-card>
    
    <el-card class="files-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>下载文件</span>
        </div>
      </template>
      
      <div class="no-files">
        <el-empty description="暂无文件" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Refresh, Delete } from '@element-plus/icons-vue'

// 简化的响应式数据
const loading = ref(false)
</script>

<style scoped>
.file-manager {
  padding: 20px;
}

.toolbar-card, .files-card {
  margin-bottom: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.no-files {
  text-align: center;
  padding: 40px;
}
</style>
