import { createRouter, createWebHistory } from 'vue-router'
import DownloadCenter from '../views/DownloadCenter.vue'
import FileManager from '../views/FileManager.vue'
import TaskHistory from '../views/TaskHistory.vue'

const routes = [
  {
    path: '/',
    name: 'DownloadCenter',
    component: DownloadCenter,
    meta: {
      title: '下载中心'
    }
  },
  {
    path: '/files',
    name: 'FileManager',
    component: FileManager,
    meta: {
      title: '文件管理'
    }
  },
  {
    path: '/history',
    name: 'TaskHistory',
    component: TaskHistory,
    meta: {
      title: '下载历史'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - M3U8下载器专业版`
  }
  next()
})

export default router
