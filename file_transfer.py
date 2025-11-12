from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import os
import shutil
from typing import List

app = FastAPI()

# 创建上传目录
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """
    上传单个文件
    """
    try:
        # 检查文件大小（限制为10MB）
        file_size = 0
        for chunk in file.file:
            file_size += len(chunk)
            if file_size > 10 * 1024 * 1024:  # 10MB
                raise HTTPException(status_code=413, detail="文件大小超过10MB限制")
        
        # 重置文件指针
        file.file.seek(0)
        
        # 保存文件
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "filename": file.filename,
            "file_size": file_size,
            "message": "文件上传成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@app.post("/upload/multiple/")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """
    上传多个文件
    """
    uploaded_files = []
    total_size = 0
    
    try:
        for file in files:
            file_size = 0
            for chunk in file.file:
                file_size += len(chunk)
                if file_size > 10 * 1024 * 1024:  # 10MB per file
                    raise HTTPException(status_code=413, detail=f"文件 {file.filename} 大小超过10MB限制")
            
            file.file.seek(0)
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            print(file_path)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append({
                "filename": file.filename,
                "file_size": file_size
            })
            total_size += file_size
        
        return {
            "uploaded_files": uploaded_files,
            "total_files": len(files),
            "total_size": total_size,
            "message": f"成功上传 {len(files)} 个文件"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    下载文件
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

@app.get("/files/")
async def list_files():
    """
    列出所有已上传的文件
    """
    try:
        files = []
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                files.append({
                    "filename": filename,
                    "file_size": file_size
                })
        
        return {
            "files": files,
            "total_files": len(files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    """
    删除文件
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    try:
        os.remove(file_path)
        return {
            "message": f"文件 {filename} 删除成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件删除失败: {str(e)}")

@app.get("/")
async def root():
    """
    API信息
    """
    return {
        "message": "文件传输服务API",
        "endpoints": {
            "POST /upload/": "上传单个文件",
            "POST /upload/multiple/": "上传多个文件",
            "GET /download/{filename}": "下载文件",
            "GET /files/": "列出所有文件",
            "DELETE /files/{filename}": "删除文件"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("file_transfer:app", host="0.0.0.0", port=8001, reload=True)