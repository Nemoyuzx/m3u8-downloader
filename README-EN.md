# M3U8 Video Downloader 🎬

A modern M3U8 video stream downloader tool with multi-architecture support and various usage options.

![Tool Interface](./imgs/tools.jpeg) ![M3U8 Example](./imgs/m3u8.jpeg)

## ✨ Features

- 🌐 **Multi-Architecture Support**: Modern Django + Vue.js web app, standalone Node.js backend
- 🎯 **Smart Download**: Auto-parse M3U8 playlists and concurrent TS segment downloads
- 📊 **Real-time Monitoring**: WebSocket real-time download progress and status display
- 🔄 **Resume Support**: Pause, resume, and retry failed download tasks
- 📱 **Responsive Design**: Modern UI supporting desktop and mobile devices
- 🛠 **Multiple Tools**: Web app, browser userscripts, online tools

## 🚀 Quick Start

### Option 1: Modern Web Application (Recommended)

Complete web application using Django backend + Vue.js frontend:

```bash
# 1. Install dependencies
# Django backend
cd backend_django
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Vue.js frontend
cd ../frontend
npm install

# 2. Start services
# Start Django backend (port 8000)
cd ../backend_django
source venv/bin/activate
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

# Start frontend dev server (port 8080)
cd ../frontend
npm run dev
```

Visit `http://localhost:8080` to use the web application.

### Option 2: Standalone Node.js Backend

```bash
# Start Node.js backend
cd backend-node
npm install
npm start  # port 3000
```

### Option 3: Online Tools (Legacy)

```bash
# Use traditional online tools
cd legacy/web-tool
# Host these files on a web server or open index.html directly
```

## 📋 Features

### Web Application Interface
![Interface Screenshot](./imgs/01.jpeg)

### Main Functions

1. **Add Download Tasks**
   - Input M3U8 playlist URL
   - Custom filename and save directory
   - Adjust concurrent download count

2. **Task Management**
   - Real-time download progress view
   - Pause/resume/retry tasks
   - Clean completed tasks

3. **Statistics Monitoring**
   - Global download statistics
   - Real-time download speed
   - Task status summary

## 🔧 Usage Guide

### Getting M3U8 Links

1. Open video webpage, press F12 to open developer tools
2. Switch to Network tab, filter requests containing "m3u8"
3. Refresh page, find the actual video M3U8 file (usually contains multiple .ts links)

![Getting M3U8 Links](./imgs/03.jpeg)

### Identifying Correct M3U8 Files

- ❌ Index file (contains multiple resolution options)
  ![Index File](./imgs/04.jpeg)

- ✅ Video file (contains .ts segment list)
  ![Video File](./imgs/05.jpeg)

## 🏗 Project Architecture

```
m3u8-downloader/
├── frontend/              # Vue.js frontend application
├── backend_django/        # Django backend (main)
├── backend-node/          # Node.js backend (standalone)
├── downloader/           # Django download module
├── files/                # Django file management
├── tasks/                # Django task management
├── legacy/               # Legacy tools
│   ├── web-tool/         # Online HTML tools
│   └── unused-images/    # Unused images
└── imgs/                 # Documentation images
```

### Technology Stack

**Frontend:**
- Vue 3 + Composition API
- Element Plus UI component library
- Vite build tool
- Socket.IO client

**Backend (Django):**
- Django 5.2 + Django REST Framework
- Celery async task queue
- Channels WebSocket support
- SQLite/PostgreSQL database

**Backend (Node.js):**
- Express.js framework
- Socket.IO real-time communication
- File stream processing

## 🔗 API Endpoints

### Django Backend (Port 8000)
- `GET /api/` - API root path
- `GET /api/tasks/` - Get download task list
- `POST /api/tasks/` - Create download task
- `PATCH /api/tasks/{id}/` - Update task status

### Node.js Backend (Port 3000)
- `POST /api/download` - Start download
- `GET /api/tasks` - Get task status
- WebSocket connection for real-time communication

## ⚙️ Configuration

### Environment Variables

```bash
# Django configuration
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3

# Node.js configuration
PORT=3000
DOWNLOAD_DIR=./downloads
MAX_CONCURRENT=5
```

### Custom Configuration

- Download directory: Default `downloads/`
- Concurrent count: 1-10 concurrent connections
- Timeout settings: Adjustable in configuration files

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Changelog

### v2.0.0 (2025-06-02)
- ✨ Added Vue.js modern frontend interface
- ✨ Added Django REST API backend
- ✨ Real-time WebSocket progress monitoring
- ✨ Support for resume and task management
- 🔧 Refactored project architecture, separated frontend and backend
- 📚 Improved documentation and usage guides

### v1.0.0
- 🎉 Initial version, basic online tools
- 📥 M3U8 video download functionality
- 🌐 Browser-based, no installation required

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- Thanks to all contributors for their support
- Improved based on the original [m3u8-downloader](https://github.com/Momo707577045/m3u8-downloader) project

---

For questions or suggestions, feel free to submit Issues or Pull Requests!











































































