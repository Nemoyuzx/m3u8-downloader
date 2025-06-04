# M3U8 视频下载器 🎬

一个现代化的M3U8视频流下载工具，支持多种架构和使用方式。

![工具界面](./imgs/tools.jpeg) ![M3U8示例](./imgs/m3u8.jpeg)

## ✨ 特性

- 🌐 **多架构支持**: Django + Vue.js 现代化Web应用，Node.js独立后端
- 🎯 **智能下载**: 自动解析M3U8播放列表，并发下载TS片段
- 📊 **实时监控**: WebSocket实时显示下载进度和状态
- 🔄 **断点续传**: 支持暂停、继续和重试失败的下载任务
- 📱 **响应式设计**: 现代化UI，支持桌面和移动设备
- 🛠 **多种工具**: Web应用、浏览器用户脚本、在线工具

## 🚀 快速开始

### 方式一：现代化Web应用（推荐）

使用Django后端 + Vue.js前端的完整Web应用：

```bash
# 1. 安装依赖
# Django后端
cd backend_django
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Vue.js前端
cd ../frontend
npm install

# 2. 启动服务
# 启动Django后端（端口8000）
cd ../backend_django
source venv/bin/activate
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

# 启动前端开发服务器（端口8080）
cd ../frontend
npm run dev
```

访问 `http://localhost:8080` 使用Web应用。

### 方式二：Node.js独立后端

```bash
# 启动Node.js后端
cd backend-node
npm install
npm start  # 端口3000
```

### 方式三：在线工具（传统方式）

```bash
# 使用传统的在线工具
cd legacy/web-tool
# 在Web服务器中托管这些文件，或直接打开index.html
```

## 📋 功能说明

### Web应用界面
![界面截图](./imgs/01.jpeg)

### 主要功能

1. **添加下载任务**
   - 输入M3U8播放列表URL
   - 自定义文件名和保存目录
   - 调整并发下载数量

2. **任务管理**
   - 实时查看下载进度
   - 暂停/继续/重试任务
   - 清理已完成的任务

3. **统计监控**
   - 全局下载统计
   - 实时下载速度
   - 任务状态汇总

## 🔧 使用指南

### 获取M3U8链接

1. 打开视频网页，按F12打开开发者工具
2. 切换到Network标签，筛选包含"m3u8"的请求
3. 刷新页面，找到真正的视频M3U8文件（通常包含多个.ts链接）

![获取M3U8链接](./imgs/03.jpeg)

### 识别正确的M3U8文件

- ❌ 索引文件（包含多个分辨率选项）
  ![索引文件](./imgs/04.jpeg)

- ✅ 视频文件（包含.ts片段列表）
  ![视频文件](./imgs/05.jpeg)

## 🏗 项目架构

```
m3u8-downloader/
├── frontend/              # Vue.js前端应用
├── backend_django/        # Django后端（主要）
├── backend-node/          # Node.js后端（独立）
├── downloader/           # Django下载模块
├── files/                # Django文件管理
├── tasks/                # Django任务管理
├── legacy/               # 旧版本工具
│   ├── web-tool/         # 在线HTML工具
│   └── unused-images/    # 未使用的图片
└── imgs/                 # 文档图片
```

### 技术栈

**前端:**
- Vue 3 + Composition API
- Element Plus UI组件库
- Vite构建工具
- Socket.IO客户端

**后端 (Django):**
- Django 5.2 + Django REST Framework
- Celery异步任务队列
- Channels WebSocket支持
- SQLite/PostgreSQL数据库

**后端 (Node.js):**
- Express.js框架
- Socket.IO实时通信
- 文件流处理

## 🔗 API接口

### Django后端 (端口8000)
- `GET /api/` - API根路径
- `GET /api/tasks/` - 获取下载任务列表
- `POST /api/tasks/` - 创建下载任务
- `PATCH /api/tasks/{id}/` - 更新任务状态

### Node.js后端 (端口3000)
- `POST /api/download` - 开始下载
- `GET /api/tasks` - 获取任务状态
- WebSocket连接用于实时通信

## ⚙️ 配置说明

### 环境变量

```bash
# Django配置
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3

# Node.js配置
PORT=3000
DOWNLOAD_DIR=./downloads
MAX_CONCURRENT=5
```

### 自定义配置

- 下载目录: 默认为`downloads/`
- 并发数量: 1-10个并发连接
- 超时设置: 可在配置文件中调整

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📝 更新日志

### v2.0.0 (2025-06-02)
- ✨ 新增Vue.js现代化前端界面
- ✨ 添加Django REST API后端
- ✨ 实时WebSocket进度监控
- ✨ 支持断点续传和任务管理
- 🔧 重构项目架构，分离前后端
- 📚 完善文档和使用指南

### v1.0.0
- 🎉 初始版本，基础在线工具
- 📥 M3U8视频下载功能
- 🌐 浏览器内运行，无需安装

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- 感谢所有贡献者的支持
- 基于原版[m3u8-downloader](https://github.com/Momo707577045/m3u8-downloader)项目改进

---

如有问题或建议，欢迎提交Issue或Pull Request！











































































