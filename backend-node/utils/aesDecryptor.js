const crypto = require('crypto');

class AESDecryptor {
  constructor() {
    this.algorithm = 'aes-128-cbc';
  }
  
  decrypt(encryptedData, key, iv) {
    try {
      // 准备IV
      let ivBuffer;
      if (typeof iv === 'string') {
        // 如果IV是十六进制字符串
        ivBuffer = Buffer.from(iv, 'hex');
      } else if (typeof iv === 'number') {
        // 如果IV是数字（片段索引），创建16字节的IV
        ivBuffer = Buffer.alloc(16);
        ivBuffer.writeUInt32BE(iv, 12); // 将索引写入最后4字节
      } else if (Buffer.isBuffer(iv)) {
        ivBuffer = iv;
      } else {
        // 默认IV全为0
        ivBuffer = Buffer.alloc(16);
      }
      
      // 确保IV长度为16字节
      if (ivBuffer.length < 16) {
        const paddedIv = Buffer.alloc(16);
        ivBuffer.copy(paddedIv);
        ivBuffer = paddedIv;
      } else if (ivBuffer.length > 16) {
        ivBuffer = ivBuffer.slice(0, 16);
      }
      
      // 确保密钥长度正确
      let keyBuffer = key;
      if (typeof key === 'string') {
        keyBuffer = Buffer.from(key, 'hex');
      }
      
      if (keyBuffer.length !== 16) {
        throw new Error(`密钥长度错误: ${keyBuffer.length}，应为16字节`);
      }
      
      // 创建解密器
      const decipher = crypto.createDecipheriv(this.algorithm, keyBuffer, ivBuffer);
      decipher.setAutoPadding(false); // 关闭自动填充
      
      // 解密数据
      const decrypted = Buffer.concat([
        decipher.update(encryptedData),
        decipher.final()
      ]);
      
      // 移除PKCS7填充
      return this.removePKCS7Padding(decrypted);
      
    } catch (error) {
      throw new Error(`AES解密失败: ${error.message}`);
    }
  }
  
  // 移除PKCS7填充
  removePKCS7Padding(data) {
    if (data.length === 0) {
      return data;
    }
    
    const paddingLength = data[data.length - 1];
    
    // 验证填充是否有效
    if (paddingLength === 0 || paddingLength > 16) {
      return data; // 可能没有填充
    }
    
    // 检查所有填充字节是否相同
    for (let i = data.length - paddingLength; i < data.length; i++) {
      if (data[i] !== paddingLength) {
        return data; // 填充无效，返回原数据
      }
    }
    
    // 移除填充
    return data.slice(0, data.length - paddingLength);
  }
  
  // 验证密钥格式
  validateKey(key) {
    let keyBuffer = key;
    if (typeof key === 'string') {
      if (key.startsWith('0x')) {
        keyBuffer = Buffer.from(key.slice(2), 'hex');
      } else {
        keyBuffer = Buffer.from(key, 'hex');
      }
    }
    
    return keyBuffer.length === 16;
  }
  
  // 验证IV格式
  validateIV(iv) {
    if (typeof iv === 'number') {
      return true; // 数字索引总是有效的
    }
    
    if (typeof iv === 'string') {
      try {
        const ivBuffer = Buffer.from(iv.startsWith('0x') ? iv.slice(2) : iv, 'hex');
        return ivBuffer.length <= 16;
      } catch (error) {
        return false;
      }
    }
    
    if (Buffer.isBuffer(iv)) {
      return iv.length <= 16;
    }
    
    return false;
  }
  
  // 生成随机IV
  generateRandomIV() {
    return crypto.randomBytes(16);
  }
  
  // 将字符串转换为Buffer
  stringToBuffer(str) {
    if (str.startsWith('0x')) {
      return Buffer.from(str.slice(2), 'hex');
    }
    return Buffer.from(str, 'hex');
  }
  
  // 检测加密方法
  detectEncryptionMethod(keyInfo) {
    if (!keyInfo || !keyInfo.method) {
      return null;
    }
    
    const method = keyInfo.method.toUpperCase();
    
    switch (method) {
      case 'AES-128':
      case 'AES-128-CBC':
        return 'aes-128-cbc';
      case 'AES-128-CTR':
        return 'aes-128-ctr';
      default:
        throw new Error(`不支持的加密方法: ${method}`);
    }
  }
}

module.exports = AESDecryptor;
