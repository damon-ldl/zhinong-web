# 智慧农业病害诊疗系统 - API接口文档

## 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **认证方式**: 简单Session ID
- **数据格式**: JSON
- **字符编码**: UTF-8

## 认证相关接口

### 1. 用户登录

**接口地址**: `POST /auth/login`

**请求参数**:
```json
{
  "username": "string"      // 用户名，简单验证即可
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "user_id": 1,
    "username": "testuser",
    "session_id": "simple-session-123"
  }
}
```

### 2. 获取用户信息

**接口地址**: `GET /auth/user`

**请求头**:
```
X-Session-ID: <session_id>
```

**响应示例**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "user_id": 1,
    "username": "testuser",
    "login_time": "2024-01-01T00:00:00Z"
  }
}
```

## 图像上传与识别接口

### 4. 上传图像

**接口地址**: `POST /upload/image`

**请求头**:
```
X-Session-ID: <session_id>
Content-Type: multipart/form-data
```

**请求参数**:
```
file: File          // 图像文件，支持jpg、png、jpeg格式，最大10MB
description: string  // 图像描述，可选
```

**响应示例**:
```json
{
  "code": 200,
  "message": "图像上传成功",
  "data": {
    "file_id": "uuid-string",
    "file_path": "/uploads/images/2024/01/01/uuid.jpg",
    "file_size": 1024000,
    "upload_time": "2024-01-01T00:00:00Z"
  }
}
```

### 5. 病害识别

**接口地址**: `POST /diagnose`

**请求头**:
```
X-Session-ID: <session_id>
Content-Type: application/json
```

**请求参数**:
```json
{
  "file_id": "string",      // 上传的图像文件ID
  "crop_type": "string",    // 作物类型，可选
  "additional_info": "string" // 额外信息，可选
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "识别完成",
  "data": {}
}
```

## 智能诊疗接口

### 6. 生成诊疗方案

**接口地址**: `POST /treatment/generate`

**请求头**:
```
X-Session-ID: <session_id>
Content-Type: application/json
```

**请求参数**:
```json
{
  "record_id": 123,         // 识别记录ID
  "user_question": "string", // 用户问题，可选
  "treatment_type": "string" // 诊疗类型：prevention/control/cure
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "诊疗方案生成成功",
  "data": {
    "treatment_id": 456,
    "treatment_result": "string"  // 诊疗结果，具体内容以实际实现为准
  }
}
```

## 诊疗记录管理接口

### 7. 获取诊疗记录列表

**接口地址**: `GET /records`

**请求头**:
```
X-Session-ID: <session_id>
```

**查询参数**:
```
page: int = 1           // 页码，默认1
page_size: int = 10     // 每页数量，默认10
start_date: string      // 开始日期，格式：YYYY-MM-DD
end_date: string        // 结束日期，格式：YYYY-MM-DD
disease_name: string    // 病害名称筛选
```

**响应示例**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "records": [
      {
        "record_id": 123,
        "disease_name": "叶斑病",
        "confidence_score": 0.95,
        "image_path": "/uploads/images/2024/01/01/uuid.jpg",
        "created_at": "2024-01-01T00:00:00Z",
        "has_treatment": true
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 5,
      "total_records": 50,
      "page_size": 10
    }
  }
}
```

### 8. 获取记录详情

**接口地址**: `GET /records/{record_id}`

**请求头**:
```
X-Session-ID: <session_id>
```

**路径参数**:
```
record_id: int  // 记录ID
```

**响应示例**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "record_id": 123,
    "user_id": 1,
    "image_path": "/uploads/images/2024/01/01/uuid.jpg",
    "disease_name": "叶斑病",
    "confidence_score": 0.95,
    "disease_description": "叶片出现圆形或不规则形状的斑点...",
    "severity": "中等",
    "affected_area": "叶片",
    "treatment_plan": {
      "immediate_actions": ["立即移除受感染的叶片"],
      "chemical_treatment": {...},
      "prevention_measures": [...]
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### 9. 删除记录

**接口地址**: `DELETE /records/{record_id}`

**请求头**:
```
X-Session-ID: <session_id>
```

**路径参数**:
```
record_id: int  // 记录ID
```

**响应示例**:
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

## 系统设置接口

### 10. 获取系统设置

**接口地址**: `GET /settings`

**请求头**:
```
X-Session-ID: <session_id>
```

**响应示例**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "api_key": "sk-xxx...",
    "model_name": "gpt-3.5-turbo",
    "language": "zh-CN",
    "max_file_size": 10485760,
    "supported_formats": ["jpg", "png", "jpeg"],
    "recognition_confidence_threshold": 0.7
  }
}
```

### 11. 更新系统设置

**接口地址**: `PUT /settings`

**请求头**:
```
X-Session-ID: <session_id>
Content-Type: application/json
```

**请求参数**:
```json
{
  "api_key": "string",                    // API密钥
  "model_name": "string",                 // 模型名称
  "language": "string",                   // 语言设置
  "max_file_size": 10485760,             // 最大文件大小
  "recognition_confidence_threshold": 0.7 // 识别置信度阈值
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "设置更新成功",
  "data": {
    "updated_fields": ["api_key", "model_name"],
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

## 统计分析接口

### 12. 获取诊断统计

**接口地址**: `GET /statistics/diagnosis`

**请求头**:
```
X-Session-ID: <session_id>
```

**查询参数**:
```
period: string = "month"  // 统计周期：day/week/month/year
start_date: string        // 开始日期
end_date: string          // 结束日期
```

**响应示例**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "total_diagnoses": 150,
    "disease_distribution": [
      {
        "disease_name": "叶斑病",
        "count": 45,
        "percentage": 30.0
      },
      {
        "disease_name": "白粉病",
        "count": 30,
        "percentage": 20.0
      }
    ],
    "confidence_distribution": {
      "high": 120,    // >0.8
      "medium": 25,   // 0.6-0.8
      "low": 5        // <0.6
    },
    "period": "month"
  }
}
```

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权/Token无效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 413 | 文件过大 |
| 415 | 不支持的文件格式 |
| 422 | 数据验证失败 |
| 500 | 服务器内部错误 |

## 通用响应格式

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {},        // 响应数据，可能为null
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 注意事项

1. 所有需要认证的接口都需要在请求头中携带有效的Session ID
2. 文件上传接口支持的最大文件大小为10MB
3. 支持的图像格式：JPG、PNG、JPEG
4. 分页查询默认每页10条记录，最大100条
5. 所有时间格式均为ISO 8601标准格式
6. 图像识别结果置信度范围：0.0-1.0
