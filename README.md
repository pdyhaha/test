# 文件传输服务API

这是一个基于FastAPI的文件传输服务，提供文件上传、下载、列表查看和删除功能。

## 功能特性

- ✅ 单文件上传
- ✅ 多文件上传
- ✅ 文件下载
- ✅ 文件列表查看
- ✅ 文件删除
- ✅ 文件大小限制（10MB）
- ✅ 错误处理

## 安装依赖

```bash
pip install -r requirements.txt
```

或者手动安装：

```bash
pip install fastapi uvicorn python-multipart
```

## 启动服务

```bash
python file_transfer.py
```

服务将在 `http://localhost:8001` 启动。

## API接口

### 1. 上传单个文件
- **URL**: `POST /upload/`
- **参数**: file (文件)
- **示例**:
  ```bash
  curl -X POST "http://localhost:8001/upload/" -F "file=@example.txt"
  ```

### 2. 上传多个文件
- **URL**: `POST /upload/multiple/`
- **参数**: files (多个文件)
- **示例**:
  ```bash
  curl -X POST "http://localhost:8001/upload/multiple/" -F "files=@file1.txt" -F "files=@file2.txt"
  ```

### 3. 下载文件
- **URL**: `GET /download/{filename}`
- **参数**: filename (文件名)
- **示例**:
  ```bash
  curl -O "http://localhost:8001/download/example.txt"
  ```

### 4. 列出所有文件
- **URL**: `GET /files/`
- **返回**: 文件列表和文件信息
- **示例**:
  ```bash
  curl "http://localhost:8001/files/"
  ```

### 5. 删除文件
- **URL**: `DELETE /files/{filename}`
- **参数**: filename (文件名)
- **示例**:
  ```bash
  curl -X DELETE "http://localhost:8001/files/example.txt"
  ```

### 6. API信息
- **URL**: `GET /`
- **返回**: API使用说明

## 测试页面

打开 `test_file_upload.html` 文件在浏览器中，可以使用图形界面测试所有功能。

## 文件存储

- 上传的文件存储在 `uploads/` 目录下
- 单个文件大小限制：10MB
- 支持所有文件类型

## 错误处理

- 400: 请求参数错误
- 404: 文件不存在
- 413: 文件大小超过限制
- 500: 服务器内部错误

## 使用示例

### Python客户端示例

```python
import requests

# 上传文件
with open('example.txt', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8001/upload/', files=files)
    print(response.json())

# 下载文件
response = requests.get('http://localhost:8001/download/example.txt')
with open('downloaded.txt', 'wb') as f:
    f.write(response.content)

# 获取文件列表
response = requests.get('http://localhost:8001/files/')
print(response.json())
```

### JavaScript客户端示例

```javascript
// 上传文件
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8001/upload/', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));

// 获取文件列表
fetch('http://localhost:8001/files/')
.then(response => response.json())
.then(data => console.log(data));
```

## 注意事项

1. 确保有足够的磁盘空间存储上传的文件
2. 大文件上传可能需要调整超时设置
3. 在生产环境中建议添加身份验证和授权
4. 定期清理uploads目录以避免磁盘空间不足

## 技术栈

- **FastAPI**: 现代化的Python Web框架
- **Uvicorn**: ASGI服务器
- **Python-Multipart**: 处理multipart/form-data请求