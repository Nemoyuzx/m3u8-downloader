const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const path = require('path');
const fs = require('fs-extra');
const { v4: uuidv4 } = require('uuid');

const downloadController = require('./controllers/downloadController');
const fileController = require('./controllers/fileController');
const taskController = require('./controllers/taskController');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// 中间件
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../frontend/dist')));

// 确保下载目录存在
const DOWNLOAD_DIR = path.join(__dirname, 'downloads');
const TEMP_DIR = path.join(__dirname, 'temp');
fs.ensureDirSync(DOWNLOAD_DIR);
fs.ensureDirSync(TEMP_DIR);

// 将io对象添加到app中，以便在控制器中使用
app.set('io', io);

// 路由
app.use('/api/download', downloadController);
app.use('/api/files', fileController);
app.use('/api/tasks', taskController);

// Socket.io连接处理
io.on('connection', (socket) => {
  console.log('用户连接:', socket.id);
  
  socket.on('disconnect', () => {
    console.log('用户断开连接:', socket.id);
  });
  
  socket.on('joinTask', (taskId) => {
    socket.join(`task_${taskId}`);
    console.log(`Socket ${socket.id} 加入任务 ${taskId}`);
  });
});

// 错误处理中间件
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: '服务器内部错误' });
});

// 捕获404
app.use((req, res) => {
  res.status(404).json({ error: '接口不存在' });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`服务器运行在端口 ${PORT}`);
});

module.exports = { app, io };
