const express = require('express');
const axios = require('axios');
const fs = require('fs-extra');
const path = require('path');
const crypto = require('crypto');
const { v4: uuidv4 } = require('uuid');

const DownloadTask = require('../models/DownloadTask');
const M3U8Parser = require('../utils/m3u8Parser');
const AESDecryptor = require('../utils/aesDecryptor');

const router = express.Router();

// 存储活动任务
const activeTasks = new Map();

// 开始下载
router.post('/start', async (req, res) => {
  try {
    const { url, title, convertToMp4 = false, startSegment, endSegment } = req.body;
    
    if (!url) {
      return res.status(400).json({ error: 'M3U8链接不能为空' });
    }
    
    const taskId = uuidv4();
    const task = new DownloadTask({
      id: taskId,
      url,
      title: title || `video_${Date.now()}`,
      convertToMp4,
      startSegment,
      endSegment,
      status: 'pending'
    });
    
    activeTasks.set(taskId, task);
    
    // 异步开始下载过程
    startDownloadProcess(task, req.app.get('io'));
    
    res.json({
      success: true,
      taskId,
      message: '下载任务已创建'
    });
  } catch (error) {
    console.error('创建下载任务失败:', error);
    res.status(500).json({ error: '创建下载任务失败' });
  }
});

// 获取任务状态
router.get('/status/:taskId', (req, res) => {
  const { taskId } = req.params;
  const task = activeTasks.get(taskId);
  
  if (!task) {
    return res.status(404).json({ error: '任务不存在' });
  }
  
  res.json({
    success: true,
    task: task.getStatus()
  });
});

// 暂停/恢复任务
router.post('/toggle/:taskId', (req, res) => {
  const { taskId } = req.params;
  const task = activeTasks.get(taskId);
  
  if (!task) {
    return res.status(404).json({ error: '任务不存在' });
  }
  
  if (task.status === 'downloading') {
    task.pause();
  } else if (task.status === 'paused') {
    task.resume();
    // 继续下载过程
    continueDownloadProcess(task, req.app.get('io'));
  }
  
  res.json({
    success: true,
    status: task.status
  });
});

// 取消任务
router.delete('/cancel/:taskId', async (req, res) => {
  const { taskId } = req.params;
  const task = activeTasks.get(taskId);
  
  if (!task) {
    return res.status(404).json({ error: '任务不存在' });
  }
  
  task.cancel();
  
  // 清理临时文件
  try {
    await fs.remove(task.tempDir);
  } catch (error) {
    console.error('清理临时文件失败:', error);
  }
  
  activeTasks.delete(taskId);
  
  res.json({
    success: true,
    message: '任务已取消'
  });
});

// 重试失败的片段
router.post('/retry/:taskId', async (req, res) => {
  const { taskId } = req.params;
  const task = activeTasks.get(taskId);
  
  if (!task) {
    return res.status(404).json({ error: '任务不存在' });
  }
  
  // 重置失败的片段
  task.retryFailedSegments();
  
  // 继续下载过程
  continueDownloadProcess(task, req.app.get('io'));
  
  res.json({
    success: true,
    message: '重试已开始'
  });
});

// 下载过程主函数
async function startDownloadProcess(task, io) {
  try {
    task.updateStatus('parsing');
    emitProgress(io, task);
    
    // 解析M3U8文件
    const parser = new M3U8Parser();
    const m3u8Data = await parser.parse(task.url);
    
    task.segments = m3u8Data.segments;
    task.totalSegments = m3u8Data.segments.length;
    task.encryption = m3u8Data.encryption;
    
    // 应用范围限制
    if (task.startSegment || task.endSegment) {
      const start = Math.max(0, (task.startSegment || 1) - 1);
      const end = Math.min(task.segments.length, task.endSegment || task.segments.length);
      task.segments = task.segments.slice(start, end);
      task.totalSegments = task.segments.length;
    }
    
    // 创建临时目录
    task.tempDir = path.join(__dirname, '../temp', task.id);
    await fs.ensureDir(task.tempDir);
    
    // 如果有加密，先获取密钥
    if (task.encryption) {
      await downloadEncryptionKey(task);
    }
    
    task.updateStatus('downloading');
    emitProgress(io, task);
    
    // 开始并发下载片段
    await downloadSegmentsConcurrently(task, io);
    
  } catch (error) {
    console.error('下载过程出错:', error);
    task.updateStatus('error');
    task.error = error.message;
    emitProgress(io, task);
  }
}

// 并发下载片段
async function downloadSegmentsConcurrently(task, io, maxConcurrency = 5) {
  const downloadQueue = [...task.segments];
  const workers = [];
  
  // 创建工作线程
  for (let i = 0; i < Math.min(maxConcurrency, downloadQueue.length); i++) {
    workers.push(downloadWorker(task, downloadQueue, io));
  }
  
  // 等待所有工作线程完成
  await Promise.all(workers);
  
  if (task.status === 'cancelled') {
    return;
  }
  
  // 检查是否有失败的片段
  if (task.failedSegments.length > 0) {
    task.updateStatus('partial');
  } else {
    // 合并文件
    await mergeSegments(task, io);
  }
  
  emitProgress(io, task);
}

// 工作线程函数
async function downloadWorker(task, downloadQueue, io) {
  while (downloadQueue.length > 0 && task.status !== 'cancelled') {
    if (task.status === 'paused') {
      await new Promise(resolve => {
        const checkResume = () => {
          if (task.status !== 'paused') {
            resolve();
          } else {
            setTimeout(checkResume, 100);
          }
        };
        checkResume();
      });
    }
    
    const segment = downloadQueue.shift();
    if (!segment) break;
    
    try {
      await downloadSegment(task, segment, io);
    } catch (error) {
      console.error(`下载片段失败: ${segment.url}`, error);
      task.failedSegments.push(segment);
    }
  }
}

// 下载单个片段
async function downloadSegment(task, segment, io) {
  const segmentPath = path.join(task.tempDir, `segment_${segment.index}.ts`);
  
  // 检查文件是否已存在
  if (await fs.pathExists(segmentPath)) {
    task.downloadedSegments++;
    emitProgress(io, task);
    return;
  }
  
  const response = await axios({
    method: 'GET',
    url: segment.url,
    responseType: 'arraybuffer',
    timeout: 30000,
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
  });
  
  let data = Buffer.from(response.data);
  
  // 如果有加密，解密数据
  if (task.encryption && task.encryptionKey) {
    const decryptor = new AESDecryptor();
    data = decryptor.decrypt(data, task.encryptionKey, task.encryption.iv || segment.index);
  }
  
  // 保存到临时文件
  await fs.writeFile(segmentPath, data);
  
  task.downloadedSegments++;
  emitProgress(io, task);
}

// 下载加密密钥
async function downloadEncryptionKey(task) {
  if (!task.encryption.uri) {
    throw new Error('缺少加密密钥URI');
  }
  
  const response = await axios({
    method: 'GET',
    url: task.encryption.uri,
    responseType: 'arraybuffer',
    timeout: 10000
  });
  
  task.encryptionKey = Buffer.from(response.data);
}

// 合并片段
async function mergeSegments(task, io) {
  task.updateStatus('merging');
  emitProgress(io, task);
  
  const outputDir = path.join(__dirname, '../downloads');
  await fs.ensureDir(outputDir);
  
  const outputFile = path.join(outputDir, `${task.title}.${task.convertToMp4 ? 'mp4' : 'ts'}`);
  const writeStream = fs.createWriteStream(outputFile);
  
  try {
    for (let i = 0; i < task.segments.length; i++) {
      const segmentPath = path.join(task.tempDir, `segment_${i}.ts`);
      
      if (await fs.pathExists(segmentPath)) {
        const data = await fs.readFile(segmentPath);
        writeStream.write(data);
      }
    }
    
    writeStream.end();
    
    await new Promise((resolve, reject) => {
      writeStream.on('finish', resolve);
      writeStream.on('error', reject);
    });
    
    task.outputFile = outputFile;
    task.updateStatus('completed');
    
    // 清理临时文件
    await fs.remove(task.tempDir);
    
  } catch (error) {
    writeStream.destroy();
    throw error;
  }
}

// 继续下载过程
async function continueDownloadProcess(task, io) {
  if (task.status === 'paused') {
    task.updateStatus('downloading');
    await downloadSegmentsConcurrently(task, io);
  }
}

// 发送进度更新
function emitProgress(io, task) {
  io.to(`task_${task.id}`).emit('progress', {
    taskId: task.id,
    ...task.getStatus()
  });
}

module.exports = router;
