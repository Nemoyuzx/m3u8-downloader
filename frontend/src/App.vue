<template>
  <div class="main-layout">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="header-content">
        <div class="logo">
          <el-icon><VideoCamera /></el-icon>
          M3U8下载器专业版
        </div>
        <nav class="nav-menu">
          <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
            <el-icon><Download /></el-icon>
            下载中心
          </router-link>
          <router-link to="/files" class="nav-item" :class="{ active: $route.path === '/files' }">
            <el-icon><Folder /></el-icon>
            文件管理
          </router-link>
          <router-link to="/history" class="nav-item" :class="{ active: $route.path === '/history' }">
            <el-icon><Clock /></el-icon>
            下载历史
          </router-link>
        </nav>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="content">
      <router-view :key="$route.fullPath" />
    </main>
  </div>
</template>

<script>
import { VideoCamera, Download, Folder, Clock } from '@element-plus/icons-vue'

export default {
  name: 'App',
  components: {
    VideoCamera,
    Download,
    Folder,
    Clock
  },
  methods: {
    handleNavClick(path) {
      console.log('Navigation clicked:', path)
      this.$router.push(path)
    }
  }
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 20px;
  font-weight: bold;
  gap: 8px;
}

.nav-menu {
  display: flex;
  gap: 20px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  color: inherit;
  user-select: none;
  position: relative;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.nav-item.active {
  background-color: rgba(255, 255, 255, 0.3);
  font-weight: 600;
}

.nav-item:active {
  background-color: rgba(255, 255, 255, 0.4);
  transform: translateY(0);
}

.content {
  flex: 1;
  overflow: auto;
  padding: 20px;
  background-color: #f5f7fa;
}
</style>
