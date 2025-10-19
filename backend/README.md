# 智慧农业病害诊疗系统 - 后端

## 技术栈

- **框架**: FastAPI
- **数据库**: SQLite
- **ORM**: SQLAlchemy
- **认证**: JWT
- **AI模型**: 自定义训练模型

## 项目结构

```
backend/
├── app/
│   ├── api/               # API路由
│   │   └── v1/
│   │       └── endpoints/ # API端点
│   ├── core/             # 核心配置
│   ├── database/         # 数据库配置
│   ├── models/           # 数据模型
│   ├── services/         # 业务逻辑
│   └── utils/            # 工具函数
├── tests/                # 测试文件
├── docs/                 # 文档
└── README.md
```

## 功能模块

### 1. 用户管理模块
- 用户注册/登录
- JWT token 生成和验证
- 用户权限管理
- 密码加密存储

### 2. 图像识别模块
- 图像上传处理
- 图像格式验证和压缩
- 调用AI模型进行病害识别
- 识别结果返回

### 3. 智能诊疗模块
- 基于识别结果生成诊疗建议
- 调用大语言模型生成详细报告
- 结构化数据输出
- 报告模板化处理

### 4. 数据管理模块
- 诊疗记录存储
- 历史记录查询
- 数据导出功能
- 统计分析

### 5. 系统配置模块
- API Key 管理
- 模型配置
- 系统参数设置

## 数据库设计

### 用户表 (users)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 诊疗记录表 (records)
```sql
CREATE TABLE records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    image_path VARCHAR(255) NOT NULL,
    disease_name VARCHAR(100),
    diagnosis_result TEXT,
    treatment_plan TEXT,
    confidence_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

### 系统配置表 (settings)
```sql
CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_key VARCHAR(255),
    model_name VARCHAR(100),
    config JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API 接口

### 认证相关
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/refresh` - 刷新token

### 图像识别
- `POST /api/v1/upload/image` - 上传图像
- `POST /api/v1/diagnose` - 病害诊断

### 诊疗记录
- `GET /api/v1/records` - 获取诊疗记录列表
- `GET /api/v1/records/{record_id}` - 获取记录详情
- `DELETE /api/v1/records/{record_id}` - 删除记录

### 系统设置
- `GET /api/v1/settings` - 获取系统设置
- `PUT /api/v1/settings` - 更新系统设置

## 开发指南

### 环境要求
- Python >= 3.8
- pip >= 21.0

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行开发服务器
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 运行测试
```bash
pytest
```

### 生成API文档
```bash
# 访问 http://localhost:8000/docs 查看Swagger文档
# 访问 http://localhost:8000/redoc 查看ReDoc文档
```

## 主要依赖

- `fastapi@^0.100.0` - Web框架
- `uvicorn@^0.23.0` - ASGI服务器
- `sqlalchemy@^2.0.0` - ORM
- `python-jose@^3.3.0` - JWT处理
- `passlib@^1.7.4` - 密码加密
- `python-multipart@^0.0.6` - 文件上传

## 环境变量

创建 `.env` 文件：
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./app.db
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 开发规范

1. 使用类型注解
2. 遵循 PEP 8 代码风格
3. 使用 FastAPI 内置的数据验证
4. 编写单元测试
5. 使用异步编程模式
6. 错误处理和日志记录
