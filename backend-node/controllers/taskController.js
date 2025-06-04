const express = require('express');
const router = express.Router();

// 模拟任务存储（生产环境应使用数据库）
const taskHistory = [];

// 获取所有任务
router.get('/list', (req, res) => {
  try {
    const { status, limit = 50, offset = 0 } = req.query;
    
    let filteredTasks = [...taskHistory];
    
    // 按状态过滤
    if (status) {
      filteredTasks = filteredTasks.filter(task => task.status === status);
    }
    
    // 分页
    const total = filteredTasks.length;
    const tasks = filteredTasks
      .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
      .slice(parseInt(offset), parseInt(offset) + parseInt(limit));
    
    res.json({
      success: true,
      tasks,
      pagination: {
        total,
        limit: parseInt(limit),
        offset: parseInt(offset),
        hasMore: parseInt(offset) + parseInt(limit) < total
      }
    });
  } catch (error) {
    console.error('获取任务列表失败:', error);
    res.status(500).json({ error: '获取任务列表失败' });
  }
});

// 获取单个任务详情
router.get('/:taskId', (req, res) => {
  try {
    const { taskId } = req.params;
    const task = taskHistory.find(t => t.id === taskId);
    
    if (!task) {
      return res.status(404).json({ error: '任务不存在' });
    }
    
    res.json({
      success: true,
      task
    });
  } catch (error) {
    console.error('获取任务详情失败:', error);
    res.status(500).json({ error: '获取任务详情失败' });
  }
});

// 删除任务记录
router.delete('/:taskId', (req, res) => {
  try {
    const { taskId } = req.params;
    const taskIndex = taskHistory.findIndex(t => t.id === taskId);
    
    if (taskIndex === -1) {
      return res.status(404).json({ error: '任务不存在' });
    }
    
    taskHistory.splice(taskIndex, 1);
    
    res.json({
      success: true,
      message: '任务记录已删除'
    });
  } catch (error) {
    console.error('删除任务记录失败:', error);
    res.status(500).json({ error: '删除任务记录失败' });
  }
});

// 清空任务历史
router.delete('/clear/all', (req, res) => {
  try {
    const { status } = req.query;
    
    if (status) {
      // 只清空指定状态的任务
      const tasksToRemove = taskHistory.filter(task => task.status === status);
      tasksToRemove.forEach(task => {
        const index = taskHistory.indexOf(task);
        if (index > -1) {
          taskHistory.splice(index, 1);
        }
      });
    } else {
      // 清空所有任务
      taskHistory.length = 0;
    }
    
    res.json({
      success: true,
      message: '任务历史已清空'
    });
  } catch (error) {
    console.error('清空任务历史失败:', error);
    res.status(500).json({ error: '清空任务历史失败' });
  }
});

// 获取任务统计
router.get('/stats/summary', (req, res) => {
  try {
    const stats = {
      total: taskHistory.length,
      completed: taskHistory.filter(t => t.status === 'completed').length,
      failed: taskHistory.filter(t => t.status === 'error').length,
      downloading: taskHistory.filter(t => t.status === 'downloading').length,
      paused: taskHistory.filter(t => t.status === 'paused').length,
      cancelled: taskHistory.filter(t => t.status === 'cancelled').length
    };
    
    res.json({
      success: true,
      stats
    });
  } catch (error) {
    console.error('获取任务统计失败:', error);
    res.status(500).json({ error: '获取任务统计失败' });
  }
});

// 导出任务历史
router.get('/export/history', (req, res) => {
  try {
    const { format = 'json' } = req.query;
    
    if (format === 'json') {
      res.setHeader('Content-Type', 'application/json');
      res.setHeader('Content-Disposition', 'attachment; filename="task_history.json"');
      res.json(taskHistory);
    } else if (format === 'csv') {
      res.setHeader('Content-Type', 'text/csv');
      res.setHeader('Content-Disposition', 'attachment; filename="task_history.csv"');
      
      // 生成CSV
      const headers = ['ID', '标题', 'URL', '状态', '创建时间', '完成时间', '文件大小'];
      const csvData = [headers.join(',')];
      
      taskHistory.forEach(task => {
        const row = [
          task.id,
          `"${task.title}"`,
          `"${task.url}"`,
          task.status,
          task.createdAt,
          task.completedAt || '',
          task.fileSize || ''
        ];
        csvData.push(row.join(','));
      });
      
      res.send(csvData.join('\n'));
    } else {
      return res.status(400).json({ error: '不支持的导出格式' });
    }
  } catch (error) {
    console.error('导出任务历史失败:', error);
    res.status(500).json({ error: '导出任务历史失败' });
  }
});

// 添加任务到历史记录的函数（供其他模块调用）
function addTaskToHistory(task) {
  const historyTask = {
    id: task.id,
    title: task.title,
    url: task.url,
    status: task.status,
    createdAt: new Date().toISOString(),
    completedAt: task.status === 'completed' ? new Date().toISOString() : null,
    totalSegments: task.totalSegments,
    downloadedSegments: task.downloadedSegments,
    fileSize: task.fileSize,
    error: task.error
  };
  
  // 检查是否已存在
  const existingIndex = taskHistory.findIndex(t => t.id === task.id);
  if (existingIndex > -1) {
    taskHistory[existingIndex] = historyTask;
  } else {
    taskHistory.push(historyTask);
  }
}

// 更新任务历史记录的函数
function updateTaskHistory(taskId, updates) {
  const taskIndex = taskHistory.findIndex(t => t.id === taskId);
  if (taskIndex > -1) {
    Object.assign(taskHistory[taskIndex], updates);
    if (updates.status === 'completed') {
      taskHistory[taskIndex].completedAt = new Date().toISOString();
    }
  }
}

module.exports = router;
module.exports.addTaskToHistory = addTaskToHistory;
module.exports.updateTaskHistory = updateTaskHistory;
