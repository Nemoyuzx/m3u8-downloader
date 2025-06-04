const express = require('express');
const fs = require('fs-extra');
const path = require('path');

const router = express.Router();

// 获取下载文件列表
router.get('/list', async (req, res) => {
  try {
    const downloadDir = path.join(__dirname, '../downloads');
    await fs.ensureDir(downloadDir);
    
    const files = await fs.readdir(downloadDir);
    const fileList = [];
    
    for (const file of files) {
      const filePath = path.join(downloadDir, file);
      const stats = await fs.stat(filePath);
      
      if (stats.isFile()) {
        fileList.push({
          name: file,
          size: stats.size,
          createdAt: stats.birthtime,
          modifiedAt: stats.mtime,
          path: filePath
        });
      }
    }
    
    // 按修改时间排序，最新的在前
    fileList.sort((a, b) => new Date(b.modifiedAt) - new Date(a.modifiedAt));
    
    res.json({
      success: true,
      files: fileList
    });
  } catch (error) {
    console.error('获取文件列表失败:', error);
    res.status(500).json({ error: '获取文件列表失败' });
  }
});

// 下载文件
router.get('/download/:filename', async (req, res) => {
  try {
    const { filename } = req.params;
    const filePath = path.join(__dirname, '../downloads', filename);
    
    // 检查文件是否存在
    if (!await fs.pathExists(filePath)) {
      return res.status(404).json({ error: '文件不存在' });
    }
    
    // 获取文件信息
    const stats = await fs.stat(filePath);
    
    // 设置响应头
    res.setHeader('Content-Disposition', `attachment; filename="${encodeURIComponent(filename)}"`);
    res.setHeader('Content-Type', 'application/octet-stream');
    res.setHeader('Content-Length', stats.size);
    
    // 创建读取流并pipe到响应
    const readStream = fs.createReadStream(filePath);
    readStream.pipe(res);
    
    readStream.on('error', (error) => {
      console.error('文件读取错误:', error);
      if (!res.headersSent) {
        res.status(500).json({ error: '文件读取错误' });
      }
    });
    
  } catch (error) {
    console.error('下载文件失败:', error);
    res.status(500).json({ error: '下载文件失败' });
  }
});

// 删除文件
router.delete('/delete/:filename', async (req, res) => {
  try {
    const { filename } = req.params;
    const filePath = path.join(__dirname, '../downloads', filename);
    
    // 检查文件是否存在
    if (!await fs.pathExists(filePath)) {
      return res.status(404).json({ error: '文件不存在' });
    }
    
    // 删除文件
    await fs.remove(filePath);
    
    res.json({
      success: true,
      message: '文件已删除'
    });
  } catch (error) {
    console.error('删除文件失败:', error);
    res.status(500).json({ error: '删除文件失败' });
  }
});

// 批量删除文件
router.post('/delete-multiple', async (req, res) => {
  try {
    const { filenames } = req.body;
    
    if (!Array.isArray(filenames)) {
      return res.status(400).json({ error: '文件名列表必须是数组' });
    }
    
    const results = [];
    
    for (const filename of filenames) {
      try {
        const filePath = path.join(__dirname, '../downloads', filename);
        
        if (await fs.pathExists(filePath)) {
          await fs.remove(filePath);
          results.push({ filename, success: true });
        } else {
          results.push({ filename, success: false, error: '文件不存在' });
        }
      } catch (error) {
        results.push({ filename, success: false, error: error.message });
      }
    }
    
    res.json({
      success: true,
      results
    });
  } catch (error) {
    console.error('批量删除文件失败:', error);
    res.status(500).json({ error: '批量删除文件失败' });
  }
});

// 重命名文件
router.post('/rename/:filename', async (req, res) => {
  try {
    const { filename } = req.params;
    const { newName } = req.body;
    
    if (!newName) {
      return res.status(400).json({ error: '新文件名不能为空' });
    }
    
    const oldPath = path.join(__dirname, '../downloads', filename);
    const newPath = path.join(__dirname, '../downloads', newName);
    
    // 检查原文件是否存在
    if (!await fs.pathExists(oldPath)) {
      return res.status(404).json({ error: '文件不存在' });
    }
    
    // 检查新文件名是否已存在
    if (await fs.pathExists(newPath)) {
      return res.status(400).json({ error: '新文件名已存在' });
    }
    
    // 重命名文件
    await fs.move(oldPath, newPath);
    
    res.json({
      success: true,
      message: '文件重命名成功'
    });
  } catch (error) {
    console.error('重命名文件失败:', error);
    res.status(500).json({ error: '重命名文件失败' });
  }
});

// 获取文件信息
router.get('/info/:filename', async (req, res) => {
  try {
    const { filename } = req.params;
    const filePath = path.join(__dirname, '../downloads', filename);
    
    // 检查文件是否存在
    if (!await fs.pathExists(filePath)) {
      return res.status(404).json({ error: '文件不存在' });
    }
    
    const stats = await fs.stat(filePath);
    
    res.json({
      success: true,
      file: {
        name: filename,
        size: stats.size,
        createdAt: stats.birthtime,
        modifiedAt: stats.mtime,
        path: filePath,
        isFile: stats.isFile(),
        isDirectory: stats.isDirectory()
      }
    });
  } catch (error) {
    console.error('获取文件信息失败:', error);
    res.status(500).json({ error: '获取文件信息失败' });
  }
});

module.exports = router;
