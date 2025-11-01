from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor, BitsAndBytesConfig
from qwen_vl_utils import process_vision_info
import torch, os
import gc
import json

# 本地模型目录（用 r"" 或把 \ 换成 /）
LOCAL_DIR = r"C:\Users\cassi\Desktop\Qwen2.5-VL-3B-Instruct"

# 可选：先做下存在性检查，避免路径写错
assert os.path.isdir(LOCAL_DIR), f"路径不存在: {LOCAL_DIR}"

# 只从本地读，不联网
device_map = "cuda" if torch.cuda.is_available() else "cpu"

# 配置量化以降低内存占用（可选：4bit 或 8bit）
# 注意：量化只支持 CUDA，CPU 模式会自动禁用量化
USE_QUANTIZATION = True  # 设置为 False 可禁用量化
QUANTIZATION_BITS = 4   # 4 或 8，4bit 更省内存但可能损失精度（已改为4bit以解决页面文件不足问题）

# CPU 模式自动禁用量化（bitsandbytes 不支持 CPU）
if device_map == "cpu":
    USE_QUANTIZATION = False
    print("CPU 模式：自动禁用量化（量化仅支持 CUDA）", flush=True)

# 清理内存，为模型加载做准备
gc.collect()
if torch.cuda.is_available():
    torch.cuda.empty_cache()

print(f"正在加载模型，使用设备: {device_map}", flush=True)
print(f"量化设置: {QUANTIZATION_BITS}bit" if USE_QUANTIZATION else "不使用量化（float16）", flush=True)

if USE_QUANTIZATION and device_map == "cuda":
    try:
        if QUANTIZATION_BITS == 4:
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
        else:  # 8bit
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True
            )
        print(f"使用 {QUANTIZATION_BITS}bit 量化加载模型，可大幅降低内存占用...", flush=True)
        print("开始从本地目录加载模型，这可能需要几分钟...", flush=True)
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            LOCAL_DIR,
            quantization_config=quantization_config,
            device_map=device_map,
            local_files_only=True,
            low_cpu_mem_usage=True,
            max_memory=None,  # 让系统自动管理
            torch_dtype=torch.float16,  # 恢复使用 torch_dtype（兼容性更好）
        )
    except Exception as e:
        print(f"量化加载失败（可能需要安装 bitsandbytes），改用 float16: {e}", flush=True)
        gc.collect()
        print("使用 float16 模式重新加载模型...", flush=True)
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            LOCAL_DIR,
            torch_dtype=torch.float16 if device_map == "cuda" else torch.float32,
            device_map=device_map,
            local_files_only=True,
            low_cpu_mem_usage=True,
            max_memory=None,
        )
elif device_map == "cpu":
    # CPU 模式下使用更激进的优化
    print("CPU 模式：使用 float32，启用低内存模式...", flush=True)
    print("开始从本地目录加载模型，这可能需要几分钟...", flush=True)
    print("注意：CPU 模式推理速度较慢，建议减少 max_new_tokens 以提高速度", flush=True)
    try:
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            LOCAL_DIR,
            torch_dtype=torch.float32,
            device_map="cpu",
            local_files_only=True,
            low_cpu_mem_usage=True,
            max_memory=None,
        )
    except Exception as e:
        print(f"CPU 模式加载失败: {e}", flush=True)
        print("尝试使用 auto 设备映射...", flush=True)
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            LOCAL_DIR,
            torch_dtype=torch.float32,
            device_map="auto",
            local_files_only=True,
            low_cpu_mem_usage=True,
            max_memory=None,
        )
else:
    # 不使用量化时，使用 float16 降低内存（比 float32 节省约一半）
    print("开始从本地目录加载模型，这可能需要几分钟...", flush=True)
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        LOCAL_DIR,
        torch_dtype=torch.float16 if device_map == "cuda" else torch.float32,
        device_map=device_map,
        local_files_only=True,
        low_cpu_mem_usage=True,
        max_memory=None,
    )

# 加载完成后再次清理
print("模型权重加载完成，正在初始化...", flush=True)
gc.collect()
if torch.cuda.is_available():
    torch.cuda.empty_cache()
print("模型加载完成！", flush=True)

print("正在加载处理器（processor）...", flush=True)
processor = AutoProcessor.from_pretrained(
    LOCAL_DIR,
    local_files_only=True,
    use_fast=False
)
print("处理器加载完成！", flush=True)

def make_messages(images, text):
    """构建单样本 messages 结构。

    images 可以是：
    - None 或空列表：纯文本
    - str（本地路径或 URL）：单图
    - list[str]：多图
    """
    content = []
    if images:
        if isinstance(images, str):
            content.append({"type": "image", "image": images})
        elif isinstance(images, (list, tuple)):
            for img in images:
                content.append({"type": "image", "image": img})
        else:
            raise TypeError("images 需为 None/str/list[str]")
    content.append({"type": "text", "text": text})
    return [
        {
            "role": "user",
            "content": content,
        }
    ]


def generate_single(messages, max_new_tokens=128):
    """对单样本 messages 生成答案，返回字符串。
    
    优化参数：
    - max_new_tokens: 降低可减少内存占用和生成时间
    - do_sample=False: 使用贪心解码，更快更省内存
    - num_beams=1: 不使用 beam search，降低计算量
    """
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(text=[text], images=image_inputs, videos=video_inputs, padding=True, return_tensors="pt")

    device = next(model.parameters()).device
    # 确保所有输入都移动到正确的设备
    inputs = {k: (v.to(device) if hasattr(v, "to") and isinstance(v, torch.Tensor) else v) for k, v in inputs.items()}
    
    # CPU 模式下添加提示并优化参数
    if device.type == "cpu":
        print(f"[INFO] 使用 CPU 推理（速度较慢，请耐心等待）...", flush=True)
        # CPU 模式下进一步降低 max_new_tokens 以提高速度
        if max_new_tokens > 64:
            print(f"[INFO] CPU 模式下将 max_new_tokens 从 {max_new_tokens} 降低到 64 以提高速度", flush=True)
            max_new_tokens = 64

    with torch.no_grad():
        # 使用优化的生成参数，降低内存和计算量
        out_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,  # 贪心解码，更快更省内存
            num_beams=1,      # 不使用 beam search
            pad_token_id=processor.tokenizer.pad_token_id if processor.tokenizer.pad_token_id else processor.tokenizer.eos_token_id,
        )

    trimmed = [o[len(i):] for i, o in zip(inputs["input_ids"], out_ids)]
    texts = processor.batch_decode(trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)
    return texts[0] if texts else ""


def generate_batch(batch_messages, max_new_tokens=64):
    """对多样本批量 messages 逐个生成，返回字符串列表。
    
    注意：默认 max_new_tokens 已降低到 64 以减少内存占用
    """
    results = []
    for sample_messages in batch_messages:
        result = generate_single(sample_messages, max_new_tokens=max_new_tokens)
        results.append(result)
    return results


def generate(messages_or_batch, max_new_tokens=64):
    """统一入口：
    - 传入单样本 messages（list[dict]）=> 返回 str
    - 传入 batch_messages（list[list[dict]]）=> 返回 list[str]
    
    注意：默认 max_new_tokens 已降低到 64 以减少内存占用
    """
    if not isinstance(messages_or_batch, list) or len(messages_or_batch) == 0:
        raise ValueError("输入需为非空 list")

    first = messages_or_batch[0]
    if isinstance(first, dict):
        return generate_single(messages_or_batch, max_new_tokens=max_new_tokens)
    elif isinstance(first, list):
        return generate_batch(messages_or_batch, max_new_tokens=max_new_tokens)
    else:
        raise TypeError("不支持的输入结构：请传入 messages 或 batch_messages")


def generate_from_json(json_input, max_new_tokens=64):
    """从 JSON 数组或 JSON 字符串生成回答。
    
    参数:
        json_input: 可以是：
            - list[dict]: JSON 数组，每个元素包含 "images"（可选）和 "text"
            - str: JSON 字符串，会被解析为上述格式
        max_new_tokens: 最大生成 token 数，默认 64
    
    返回:
        - 如果输入是单个对象（dict），返回 str（单个回答）
        - 如果输入是数组（list），返回 list[str]（多个回答）
    
    JSON 格式示例:
        单个对象:
        {"images": "path/to/image.png", "text": "描述这张图片"}
        
        多个对象:
        [
            {"images": "path/to/image1.png", "text": "描述图片1"},
            {"images": ["path/to/image2.png", "path/to/image3.png"], "text": "比较这两张图"},
            {"text": "纯文本问题"}
        ]
    """
    # 如果是字符串，先解析为 JSON
    if isinstance(json_input, str):
        try:
            json_input = json.loads(json_input)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 解析失败: {e}")
    
    # 验证输入类型
    if not isinstance(json_input, (list, dict)):
        raise TypeError("输入需为 list 或 dict")
    
    # 处理单个对象的情况
    if isinstance(json_input, dict):
        messages = make_messages(
            images=json_input.get("images"),
            text=json_input.get("text", "")
        )
        return generate_single(messages, max_new_tokens=max_new_tokens)
    
    # 处理数组的情况
    if len(json_input) == 0:
        raise ValueError("JSON 数组不能为空")
    
    batch_messages = []
    for item in json_input:
        if not isinstance(item, dict):
            raise TypeError(f"数组元素需为 dict，当前类型: {type(item)}")
        
        if "text" not in item:
            raise ValueError("每个 JSON 对象必须包含 'text' 字段")
        
        messages = make_messages(
            images=item.get("images"),
            text=item["text"]
        )
        batch_messages.append(messages)
    
    return generate_batch(batch_messages, max_new_tokens=max_new_tokens)


def _is_user_message_list(obj):
    """检查对象是否是包含 role="user" 消息的列表"""
    if not isinstance(obj, list) or len(obj) == 0:
        return False
    
    # 检查第一个元素是否是包含 role="user" 的字典
    first_item = obj[0]
    if isinstance(first_item, dict) and first_item.get("role") == "user":
        return True
    
    return False


def process_json_with_model(json_obj, max_new_tokens=128, replace_key=None):
    """递归处理 JSON 对象，自动查找并处理所有包含 role="user" 的消息。
    
    参数:
        json_obj: 可以是 dict、list 或 JSON 字符串
        max_new_tokens: 最大生成 token 数，默认 128
        replace_key: 替换模式
            - None（默认）: 直接替换整个消息列表的值为生成的字符串结果
            - "assistant": 在消息列表中添加 assistant 响应，保留原消息
            - 其他字符串: 在包含 messages 的 dict 中添加该键，值为生成结果
    
    返回:
        处理后的 JSON 对象（与输入类型相同）
    
    功能:
        - 自动递归遍历 JSON 结构
        - 识别所有包含 {"role": "user"} 的消息列表
        - 调用大模型生成回答
        - 将结果替换原值或添加为 assistant 响应
    
    示例:
        输入:
        {
            "qianzi_messages": [{"role": "user", "content": [...]}],
            "yingxiangtu_messages": [{"role": "user", "content": [...]}],
            "data_logic_correctness_result": {
                "potential": {
                    "messages": [{"role": "user", "content": [...]}]
                }
            }
        }
        
        输出（replace_key=None，默认）:
        {
            "qianzi_messages": "生成的回答",
            "yingxiangtu_messages": "生成的回答",
            "data_logic_correctness_result": {
                "potential": {
                    "messages": "生成的回答"
                }
            }
        }
        
        输出（replace_key="assistant"）:
        {
            "qianzi_messages": [
                {"role": "user", "content": [...]},
                {"role": "assistant", "content": "生成的回答"}
            ],
            ...
        }
    """
    # 如果是字符串，先解析为 JSON
    if isinstance(json_obj, str):
        try:
            json_obj = json.loads(json_obj)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 解析失败: {e}")
    
    # 处理列表
    if isinstance(json_obj, list):
        # 检查是否是包含 role="user" 的消息列表
        if _is_user_message_list(json_obj):
            # 找到所有 user 消息
            user_messages = [msg for msg in json_obj if isinstance(msg, dict) and msg.get("role") == "user"]
            
            if user_messages:
                # 调用大模型生成回答（使用第一个 user 消息，因为通常只有一个）
                user_msg = user_messages[0]
                try:
                    result = generate_single([user_msg], max_new_tokens=max_new_tokens)
                    
                    if replace_key == "assistant":
                        # 添加 assistant 响应到消息列表
                        result_list = json_obj.copy()
                        result_list.append({
                            "role": "assistant",
                            "content": result
                        })
                        return result_list
                    else:
                        # 默认：直接替换整个列表为字符串结果
                        return result
                except Exception as e:
                    print(f"生成失败: {e}")
                    # 失败时添加错误信息
                    if replace_key == "assistant":
                        result_list = json_obj.copy()
                        result_list.append({
                            "role": "assistant",
                            "content": f"处理失败: {str(e)}"
                        })
                        return result_list
                    else:
                        return f"处理失败: {str(e)}"
            else:
                return json_obj
        else:
            # 普通列表，不处理，直接返回
            return json_obj
    
    # 处理字典
    elif isinstance(json_obj, dict):
        result = {}
        for key, value in json_obj.items():
            # 情况1: value 本身就是一个包含 role="user" 的消息列表
            if _is_user_message_list(value):
                user_msg = value[0]  # 取第一个 user 消息
                try:
                    generated_result = generate_single([user_msg], max_new_tokens=max_new_tokens)
                    if replace_key == "assistant":
                        # 添加 assistant 响应
                        new_messages = value.copy()
                        new_messages.append({
                            "role": "assistant",
                            "content": generated_result
                        })
                        result[key] = new_messages
                    else:
                        # 默认：直接替换为字符串结果
                        result[key] = generated_result
                except Exception as e:
                    print(f"生成失败 ({key}): {e}")
                    if replace_key == "assistant":
                        new_messages = value.copy()
                        new_messages.append({
                            "role": "assistant",
                            "content": f"处理失败: {str(e)}"
                        })
                        result[key] = new_messages
                    else:
                        result[key] = f"处理失败: {str(e)}"
            # 情况2: value 是包含 messages 字段的字典
            elif isinstance(value, dict) and "messages" in value:
                messages_value = value["messages"]
                if _is_user_message_list(messages_value):
                    user_msg = messages_value[0]  # 取第一个 user 消息
                    try:
                        generated_result = generate_single([user_msg], max_new_tokens=max_new_tokens)
                        if replace_key == "assistant":
                            # 更新 messages，添加 assistant 响应
                            new_messages = messages_value.copy()
                            new_messages.append({
                                "role": "assistant",
                                "content": generated_result
                            })
                            result[key] = {**value, "messages": new_messages}
                        elif replace_key is None:
                            # 直接替换 messages 字段为字符串结果
                            result[key] = {**value, "messages": generated_result}
                        else:
                            # 添加新键
                            result[key] = {**value, replace_key: generated_result}
                    except Exception as e:
                        print(f"生成失败 ({key}): {e}")
                        error_msg = f"处理失败: {str(e)}"
                        if replace_key == "assistant":
                            new_messages = messages_value.copy()
                            new_messages.append({
                                "role": "assistant",
                                "content": error_msg
                            })
                            result[key] = {**value, "messages": new_messages}
                        elif replace_key is None:
                            result[key] = {**value, "messages": error_msg}
                        else:
                            result[key] = {**value, replace_key: error_msg}
                else:
                    # messages 不是 user 消息列表，不处理，直接返回原值
                    result[key] = value
            else:
                # 其他值（字符串、数字、普通字典等），不处理，直接返回原值
                result[key] = value
        return result
    
    # 其他类型（字符串、数字等），直接返回
    else:
        return json_obj

if __name__ == "__main__":
    # 使用示例：单张图片 + 提问
    sample_messages = make_messages(
        images=r"C:\Users\cassi\Desktop\bisai\影像图输出\豫洛阳-兰郑长干线-CPY-0790-BFGDGS-ZZSYQFGS_影像图_1.png",
        text="请用英文描述这张图片的主要内容。",
    )
    print(generate(sample_messages))

    # 使用示例：多张图片对比
    compare_messages = make_messages(
        images=[
            r"C:\Users\cassi\Desktop\bisai\影像图输出\豫洛阳-兰郑长干线-CPY-0790-BFGDGS-ZZSYQFGS_影像图_1.png",
            r"C:\Users\cassi\Desktop\bisai\影像图输出\豫洛阳-兰郑长干线-CPY-0790-BFGDGS-ZZSYQFGS_影像图_2.png",
            r"C:\Users\cassi\Desktop\bisai\影像图输出\豫洛阳-兰郑长干线-CPY-0790-BFGDGS-ZZSYQFGS_影像图_3.png"
        ],
        text="对比这些图片，说明共同点与差异，并给出结论。",
    )
    print(generate(compare_messages))

    # 使用示例：无图片（纯文本）
    text_only_messages = make_messages(
        images=None,
        text="没有图片时，也请回答这个问题：什么是图像标注？",
    )
    print(generate(text_only_messages))

    # 使用示例：批量多样本
    batch_messages = [
        make_messages(
            images=r"C:\Users\cassi\Desktop\bisai\影像图输出\豫郑州-兰郑长干线-CPY-0700-BFGDGS-ZZSYQFGS_影像图_1.png",
            text="简要描述这张图片。"
        ),
        make_messages(
            images=[
                r"C:\Users\cassi\Desktop\bisai\影像图输出\豫郑州-兰郑长干线-CPY-0710-BFGDGS-ZZSYQFGS_影像图_1.png",
                r"C:\Users\cassi\Desktop\bisai\影像图输出\豫郑州-兰郑长干线-CPY-0720-BFGDGS-ZZSYQFGS_影像图_1.png"
            ],
            text="比较这两张图。"
        ),
    ]
    print(generate(batch_messages))
    
    # 使用示例：从 JSON 数组生成回答
    print("\n=== 使用 generate_from_json 函数 ===")
    
    # 示例1：JSON 数组（Python list）
    json_array = [
        {
            "images": r"C:\Users\cassi\Desktop\bisai\影像图输出\豫洛阳-兰郑长干线-CPY-0790-BFGDGS-ZZSYQFGS_影像图_1.png",
            "text": "请用英文描述这张图片的主要内容。"
        },
        {
            "images": [
                r"C:\Users\cassi\Desktop\bisai\影像图输出\豫洛阳-兰郑长干线-CPY-0790-BFGDGS-ZZSYQFGS_影像图_1.png",
                r"C:\Users\cassi\Desktop\bisai\影像图输出\豫洛阳-兰郑长干线-CPY-0790-BFGDGS-ZZSYQFGS_影像图_2.png"
            ],
            "text": "比较这两张图片的差异。"
        },
        {
            "text": "什么是图像标注？"
        }
    ]
    results = generate_from_json(json_array)
    for i, result in enumerate(results, 1):
        print(f"回答 {i}: {result}")
    
    # 示例2：JSON 字符串
    json_string = '''[
        {"images": "path/to/image.png", "text": "描述图片"},
        {"text": "纯文本问题"}
    ]'''
    # 注意：实际使用时需要替换为真实路径
    # results = generate_from_json(json_string)
    
    # 使用示例：处理包含 role="user" 的复杂 JSON 结构
    print("\n=== 使用 process_json_with_model 函数 ===")
    
    # 示例：类似 main.py 输出的 JSON 格式
    complex_json = {
        "document": "example.docx",
        "qianzi_messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": "path/to/image.png"
                    },
                    {
                        "type": "text",
                        "text": "请判断图中是否存在手写痕迹：是/否。"
                    }
                ]
            }
        ],
        "yingxiangtu_messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": "path/to/image1.png"
                    },
                    {
                        "type": "text",
                        "text": "请基于给定影像图进行核查。"
                    }
                ]
            }
        ],
        "data_logic_correctness_result": {
            "potential": {
                "messages": [
                    {
                        "role": "user",
                        "content": "帮我审核电位测试结果部分是否超出-0.85V~-1.2V"
                    }
                ]
            },
            "risk": {
                "messages": [
                    {
                        "role": "user",
                        "content": "帮我审核风险评价结果中的数据。"
                    }
                ]
            }
        },
        "content_consistency_result": "已处理结果",
        "ruchangluxian_messages": "无入场线路图，无需审核。"
    }
    
    # 处理 JSON，默认替换外层键的值（replace_key=None）
    print("\n--- 模式1: 直接替换为字符串结果（默认）---")
    result1 = process_json_with_model(complex_json.copy(), max_new_tokens=64)
    print(json.dumps(result1, ensure_ascii=False, indent=2))
    
    # 处理 JSON，保留消息格式，添加 assistant 响应（replace_key="assistant"）
    print("\n--- 模式2: 保留消息格式，添加 assistant 响应 ---")
    result2 = process_json_with_model(complex_json.copy(), max_new_tokens=64, replace_key="assistant")
    print(json.dumps(result2, ensure_ascii=False, indent=2))
