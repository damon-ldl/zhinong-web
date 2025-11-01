# Inference 模块说明

本模块是一个用于处理高后果区管理文档的推理系统，提供了文档内容提取、图片处理、逻辑检查和标准符合性验证等功能。

## 📁 目录结构

```
inference/
├── __init__.py                    # 模块初始化文件
├── main.py                        # 单文档处理入口
├── main_all.py                    # 批量处理入口
├── model.py                       # Qwen2.5-VL 视觉语言模型封装
│
├── 图片提取与处理模块/
│   ├── qianzi.py                  # 签字检测（编制/校对/审核）
│   ├── yingxiangtu.py             # 影像图提取
│   ├── ruchangluxian.py           # 入场线路图提取
│   ├── luxian_extract.py          # 逃生路线图和应急疏散集合点位置提取
│   └── tupian_yizhixing.py        # 影像图与特征描述一致性检查
│
└── 内容检查模块/
    ├── content_consistency_check.py    # 内容一致性检查
    ├── cross_reference_check.py        # 交叉引用/上下文一致性检查
    ├── temporal_logic_check.py         # 时间逻辑检查
    ├── standard_compliance.py          # 标准符合性检查
    └── data_logic_correctness.py       # 数据逻辑正确性检查（电位、风险）
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 依赖库见项目根目录 `requirements.txt`

### 主要依赖

- `python-docx` - Word 文档处理
- `PyMuPDF` (fitz) - PDF 处理
- `transformers` - Qwen2.5-VL 模型
- `qwen_vl_utils` - 视觉处理工具
- `torch` - 深度学习框架

### 使用方法

#### 1. 单文档处理

```bash
python inference/main.py
```

处理单个文档，输出 JSON 格式的结果到标准输出。

#### 2. 批量处理

```bash
python inference/main_all.py
```

批量处理指定目录下的所有文档（支持 `.docx`, `.doc`, `.pdf`），结果保存到 `batch_results.json`。

**注意**：使用前需要修改 `main.py` 和 `main_all.py` 中的文档路径配置。

## 📋 功能模块详解

### 1. 图片提取与处理模块

#### `qianzi.py` - 签字检测
- **功能**：检测文档中的编制、校对、审核签字
- **输入**：Word/PDF 文档路径
- **输出**：VLM 消息列表，用于视觉语言模型分析签字

#### `yingxiangtu.py` - 影像图提取
- **功能**：提取文档中的影像图
- **输入**：Word 文档路径
- **输出**：VLM 消息列表，包含提取的影像图

#### `ruchangluxian.py` - 入场线路图提取
- **功能**：提取入场线路图
- **输入**：Word 文档路径
- **输出**：VLM 消息列表

#### `luxian_extract.py` - 路线提取
- **功能**：提取逃生路线图和应急疏散集合点位置
- **主要函数**：
  - `build_vlm_messages_for_evac_route()` - 逃生路线图
  - `build_vlm_messages_for_assembly_point()` - 应急疏散集合点
  - `get_hca_types_from_docx()` - 获取高后果区类型
- **输出**：根据高后果区类型返回相应的 VLM 消息或文本说明

#### `tupian_yizhixing.py` - 图片一致性检查
- **功能**：检查影像图与特征描述的一致性
- **输入**：Word 文档路径
- **输出**：VLM 消息或字符串结果

### 2. 内容检查模块

#### `content_consistency_check.py` - 内容一致性检查
- **功能**：检查文档内容的一致性
- **输入**：Word 文档路径
- **输出**：纯文本检查报告

#### `cross_reference_check.py` - 交叉引用检查
- **功能**：检查文档中的交叉引用和上下文一致性
- **输入**：Word 文档路径
- **输出**：纯文本检查报告

#### `temporal_logic_check.py` - 时间逻辑检查
- **功能**：提取时间信息并检查时间逻辑
- **主要函数**：
  - `extract_text_from_docx()` - 提取文档文本
  - `extract_time_information()` - 提取时间信息
  - `check_temporal_logic()` - 检查时间逻辑
  - `build_temporal_report()` - 生成时间逻辑报告
- **输出**：时间逻辑检查报告文本

#### `standard_compliance.py` - 标准符合性检查
- **功能**：检查文档是否符合高后果区识别标准（GB/T 27512）
- **支持标准**：
  - 输油管道高后果区识别分级（Ⅲ级、Ⅱ级、Ⅰ级）
  - 输气管道高后果区识别分级（Ⅲ级、Ⅱ级、Ⅰ级）
- **主要函数**：
  - `build_standard_compliance_from_docx()` - 标准符合性检查（返回文本）
  - `build_vlm_messages_from_docx()` - 生成 VLM 消息用于视觉分析
- **输出**：文本检查报告或 VLM 消息列表

#### `data_logic_correctness.py` - 数据逻辑正确性检查
- **功能**：检查电位范围和风险字段的逻辑正确性
- **主要函数**：
  - `build_potential_json()` - 提取并检查电位数据，返回 JSON
  - `build_risk_json()` - 提取并检查风险数据，返回 JSON
- **输出**：
  - 电位检查结果 JSON（包含电位范围、有效性等）
  - 风险检查结果 JSON（包含风险等级、数值有效性等）

### 3. 模型封装

#### `model.py` - 视觉语言模型
- **功能**：封装 Qwen2.5-VL-3B-Instruct 模型
- **主要函数**：
  - `make_messages()` - 构建消息结构（支持单图/多图/纯文本）
  - `generate()` - 统一生成接口（支持单样本和批量）
- **配置**：使用本地模型路径，支持 CUDA/CPU

## 📊 输出格式

### 单文档处理输出（main.py）

```json
{
  "document": "文档路径",
  "qianzi_messages": [...],                    // 签字检测 VLM 消息
  "content_consistency_result": "...",         // 内容一致性检查结果（文本）
  "yingxiangtu_messages": [...],               // 影像图 VLM 消息
  "ruchangluxian_messages": [...],             // 入场线路图 VLM 消息
  "luxian_messages": {...},                    // 路线消息（逃生路线/集合点）
  "tupian_yizhixing_messages": {...},         // 图片一致性消息
  "context_consistency_result": "...",         // 上下文一致性检查结果（文本）
  "standard_compliance_messages": [...],       // 标准符合性 VLM 消息
  "data_logic_correctness_result": {          // 数据逻辑检查结果
    "potential": {...},                        // 电位检查 JSON
    "risk": {...}                              // 风险检查 JSON
  },
  "temporal_logic_result": "..."               // 时间逻辑检查结果（文本）
}
```

### 批量处理输出（main_all.py）

保存到 `batch_results.json`，包含：
- 处理元信息（目录、处理时间、统计信息）
- 每个文档的处理结果数组

## 🔧 配置说明

### 模型配置（model.py）
- `LOCAL_DIR`: 本地 Qwen2.5-VL 模型路径
- 自动检测 CUDA 可用性

### 文档路径配置
- `main.py`: 修改 `DOC_PATH` 变量
- `main_all.py`: 修改 `DOC_PATH` 和 `OUTPUT_JSON` 变量

### API 配置（部分模块）
- `standard_compliance.py`: 包含 Spark API 配置（可选）

## 📝 使用示例

### 示例 1：处理单个文档

```python
from inference.main import main
main()
```

### 示例 2：使用单独的模块

```python
from inference.qianzi import build_vlm_messages_from_document
from inference.data_logic_correctness import build_potential_json, build_risk_json

# 签字检测
messages = build_vlm_messages_from_document("path/to/doc.docx")

# 数据逻辑检查
potential_result = build_potential_json("path/to/doc.docx")
risk_result = build_risk_json("path/to/doc.docx")
```

### 示例 3：使用模型生成

```python
from inference.model import make_messages, generate

# 创建消息
messages = make_messages(
    images=["path/to/image1.png", "path/to/image2.png"],
    text="请分析这些图片的一致性。"
)

# 生成结果
result = generate(messages, max_new_tokens=256)
print(result)
```

## ⚠️ 注意事项

1. **路径配置**：使用前请确保修改各文件中的硬编码路径
2. **模型路径**：确保 `model.py` 中的本地模型路径正确
3. **依赖安装**：部分功能需要额外的依赖（如 `pdfplumber` 用于 PDF 处理）
4. **错误处理**：各模块都包含异常处理，失败时会返回错误信息而非抛出异常
5. **输出目录**：部分图片提取功能会自动创建输出目录

## 🐛 故障排除

- **导入错误**：确保项目根目录在 `sys.path` 中，或使用绝对导入
- **模型加载失败**：检查模型路径和 PyTorch 版本兼容性
- **文档读取失败**：检查文档格式和路径是否正确
- **VLM 消息格式错误**：确保传入的图像路径有效

## 📌 模块调用关系

```
main.py / main_all.py
  ├── qianzi.py
  ├── yingxiangtu.py
  ├── ruchangluxian.py
  ├── luxian_extract.py
  ├── content_consistency_check.py
  ├── cross_reference_check.py
  ├── temporal_logic_check.py
  ├── tupian_yizhixing.py
  ├── standard_compliance.py
  └── data_logic_correctness.py
        (所有模块可通过 model.py 进行 VLM 推理)
```

## 📚 相关文档

- 项目根目录 `README.md` - 项目整体说明
- `requirements.txt` - 依赖列表

