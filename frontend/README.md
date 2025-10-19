# 智慧农业病害诊疗系统 - 前端

## 技术栈

- **框架**: Vue 3
- **构建工具**: Vite
- **UI组件库**: Element Plus
- **HTTP客户端**: Axios
- **状态管理**: Pinia
- **路由**: Vue Router

## 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── api/               # API接口封装
│   ├── assets/            # 静态资源（图片、字体等）
│   ├── components/        # 公共组件
│   ├── router/           # 路由配置
│   ├── store/            # 状态管理
│   ├── styles/           # 全局样式
│   ├── utils/            # 工具函数
│   └── views/            # 页面组件
└── README.md
```

## 功能模块

### 1. 用户管理模块
- 登录/注册页面
- 用户信息管理
- JWT token 处理

### 2. 图像上传模块
- 图像上传组件
- 图像预览
- 上传进度显示
- 图像格式验证

### 3. 病害识别模块
- 图像识别结果展示
- 识别进度显示
- 错误处理

### 4. 智能诊疗模块
- 诊疗报告生成
- 结果展示（Markdown渲染）
- 报告导出功能

### 5. 历史记录模块
- 诊疗记录列表
- 记录详情查看
- 记录搜索和筛选

### 6. 系统设置模块
- API Key 配置
- 模型选择
- 界面设置

## 开发指南

### 环境要求
- Node.js >= 16.0.0
- npm >= 8.0.0

### 安装依赖
```bash
npm install
```

### 开发模式
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

### 代码检查
```bash
npm run lint
```

## 主要依赖

- `vue@^3.3.0` - Vue 3 框架
- `vite@^4.4.0` - 构建工具
- `element-plus@^2.3.0` - UI组件库
- `axios@^1.4.0` - HTTP客户端
- `pinia@^2.1.0` - 状态管理
- `vue-router@^4.2.0` - 路由管理
- `@element-plus/icons-vue` - Element Plus 图标

## 开发规范

1. 使用 Composition API 编写组件
2. 遵循 Vue 3 官方风格指南
3. 使用 TypeScript 进行类型检查（可选）
4. 组件命名采用 PascalCase
5. 文件命名采用 kebab-case
6. 使用 ESLint + Prettier 进行代码格式化
