import json
import sys
from pathlib import Path

# 允许作为脚本直接运行：把项目根目录加入 sys.path，便于使用 inference.* 绝对导入
try:
    _CUR_DIR = Path(__file__).resolve().parent
    _ROOT_DIR = _CUR_DIR.parent
    if str(_ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(_ROOT_DIR))
except Exception:
    pass


DOC_PATH = r"C:/Users/cassi/Desktop/bisai/word-master/豫洛阳-兰郑长干线-CPY-0790-BFGDGS-ZZSYQFGS.docx"


def main():
    p = Path(DOC_PATH)
    if not p.exists() or not p.is_file():
        print(json.dumps({"error": f"文档不存在或无效: {DOC_PATH}"}, ensure_ascii=False))
        return

    # 调用 qianzi 的函数（优先同包导入，失败再用绝对导入）
    qianzi_build = None
    try:
        from .qianzi import build_vlm_messages_from_document as qianzi_build  # type: ignore
    except Exception:
        try:
            from inference.qianzi import build_vlm_messages_from_document as qianzi_build  # type: ignore
        except Exception:
            qianzi_build = None

    qianzi_messages = []
    if qianzi_build is not None:
        try:
            qianzi_messages = qianzi_build(str(p), first_only=False)
        except Exception as e:
            qianzi_messages = [{"error": f"qianzi 调用失败: {e}"}]
    else:
        # 若项目中无该函数，可退化为处理器摘要（如需）。这里保持空结果以符合需求“仅调用并打印返回值”。
        qianzi_messages = []

    # 调用 yingxiangtu 的函数
    yx_build = None
    try:
        from .yingxiangtu import build_vlm_messages_from_docx as yx_build  # type: ignore
    except Exception:
        try:
            from inference.yingxiangtu import build_vlm_messages_from_docx as yx_build  # type: ignore
        except Exception:
            yx_build = None

    yingxiangtu_messages = []
    if yx_build is not None:
        try:
            yingxiangtu_messages = yx_build(str(p), first_only=False)
        except Exception as e:
            yingxiangtu_messages = [{"error": f"yingxiangtu 调用失败: {e}"}]
    else:
        yingxiangtu_messages = []

    # 调用 ruchangluxian 的函数
    rclx_build = None
    try:
        from .ruchangluxian import build_vlm_messages_from_docx as rclx_build  # type: ignore
    except Exception:
        try:
            from inference.ruchangluxian import build_vlm_messages_from_docx as rclx_build  # type: ignore
        except Exception:
            rclx_build = None

    ruchangluxian_messages = []
    if rclx_build is not None:
        try:
            ruchangluxian_messages = rclx_build(str(p), first_only=False)
        except Exception as e:
            ruchangluxian_messages = [{"error": f"ruchangluxian 调用失败: {e}"}]
    else:
        ruchangluxian_messages = []

    # 调用 luxian_extract 的两个函数（分别生成两个键值对）
    lx_evac_build = lx_assembly_build = None
    try:
        from .luxian_extract import (
            build_vlm_messages_for_evac_route as lx_evac_build,  # type: ignore
            build_vlm_messages_for_assembly_point as lx_assembly_build,  # type: ignore
        )
    except Exception:
        try:
            from inference.luxian_extract import (
                build_vlm_messages_for_evac_route as lx_evac_build,  # type: ignore
                build_vlm_messages_for_assembly_point as lx_assembly_build,  # type: ignore
            )
        except Exception:
            lx_evac_build = lx_assembly_build = None

    luxian_evac_messages = []
    luxian_assembly_messages = []
    if lx_evac_build is not None:
        try:
            luxian_evac_messages = lx_evac_build(str(p), first_only=False)
        except Exception as e:
            luxian_evac_messages = [{"error": f"luxian_extract.evac 调用失败: {e}"}]
    if lx_assembly_build is not None:
        try:
            luxian_assembly_messages = lx_assembly_build(str(p), first_only=False)
        except Exception as e:
            luxian_assembly_messages = [{"error": f"luxian_extract.assembly 调用失败: {e}"}]

    # 调用 content_consistency_check 的函数（不走 VLM，仅返回结果）
    cc_build = None
    try:
        from .content_consistency_check import build_content_consistency_from_docx as cc_build  # type: ignore
    except Exception:
        try:
            from inference.content_consistency_check import build_content_consistency_from_docx as cc_build  # type: ignore
        except Exception:
            cc_build = None

    content_consistency_result = None
    if cc_build is not None:
        try:
            content_consistency_result = cc_build(str(p))  # 返回纯文本
        except Exception as e:
            content_consistency_result = f"content_consistency_check 调用失败: {e}"
    else:
        content_consistency_result = "content_consistency_check 函数不可用"

    # 调用 cross_reference_check 的函数（上下文一致性，不走 VLM，仅返回结果）
    cr_build = None
    try:
        from .cross_reference_check import build_cross_reference_from_docx as cr_build  # type: ignore
    except Exception:
        try:
            from inference.cross_reference_check import build_cross_reference_from_docx as cr_build  # type: ignore
        except Exception:
            cr_build = None

    context_consistency_result = None
    if cr_build is not None:
        try:
            context_consistency_result = cr_build(str(p))  # 返回纯文本
        except Exception as e:
            context_consistency_result = f"cross_reference_check 调用失败: {e}"
    else:
        context_consistency_result = "cross_reference_check 函数不可用"

    # 调用 temporal_logic_check 的函数（时间逻辑检查，不走 VLM，仅返回结果文本）
    tl_extract_text = tl_extract_info = tl_check_logic = tl_build_report = None
    try:
        try:
            from .temporal_logic_check import (
                extract_text_from_docx as tl_extract_text,  # type: ignore
                extract_time_information as tl_extract_info,  # type: ignore
                check_temporal_logic as tl_check_logic,  # type: ignore
                build_temporal_report as tl_build_report,  # type: ignore
            )
        except Exception:
            from inference.temporal_logic_check import (
                extract_text_from_docx as tl_extract_text,  # type: ignore
                extract_time_information as tl_extract_info,  # type: ignore
                check_temporal_logic as tl_check_logic,  # type: ignore
                build_temporal_report as tl_build_report,  # type: ignore
            )
    except Exception:
        tl_extract_text = tl_extract_info = tl_check_logic = tl_build_report = None

    temporal_logic_result = None
    if tl_extract_text and tl_extract_info and tl_check_logic and tl_build_report:
        try:
            _txt = tl_extract_text(str(p))
            _info = tl_extract_info(_txt)
            _logic = tl_check_logic(_info)
            temporal_logic_result = tl_build_report(_info, _logic)
        except Exception as e:
            temporal_logic_result = f"temporal_logic_check 调用失败: {e}"
    else:
        temporal_logic_result = "temporal_logic_check 函数不可用"

    # 调用 tupian_yizhixing 的函数（影像图与特征描述一致性，可能返回字符串或消息数组）
    tyx_build = None
    try:
        from .tupian_yizhixing import build_vlm_messages_from_docx as tyx_build  # type: ignore
    except Exception:
        try:
            from inference.tupian_yizhixing import build_vlm_messages_from_docx as tyx_build  # type: ignore
        except Exception:
            tyx_build = None

    tupian_yizhixing_messages = None
    if tyx_build is not None:
        try:
            tupian_yizhixing_messages = tyx_build(str(p), first_only=False)
        except Exception as e:
            tupian_yizhixing_messages = {"error": f"tupian_yizhixing 调用失败: {e}"}
    else:
        tupian_yizhixing_messages = "tupian_yizhixing 函数不可用"

    # 调用 standard_compliance 的 VLM 消息生成函数
    sc_vlm_build = None
    try:
        from .standard_compliance import build_vlm_messages_from_docx as sc_vlm_build  # type: ignore
    except Exception:
        try:
            from inference.standard_compliance import build_vlm_messages_from_docx as sc_vlm_build  # type: ignore
        except Exception:
            sc_vlm_build = None

    standard_compliance_messages = []
    if sc_vlm_build is not None:
        try:
            standard_compliance_messages = sc_vlm_build(str(p), first_only=False)
        except Exception as e:
            standard_compliance_messages = [{"error": f"standard_compliance VLM 调用失败: {e}"}]
    else:
        standard_compliance_messages = []

    # 调用 data_logic_correctness 的两个函数（电位和风险，分别返回 JSON 字典）
    dl_potential_build = dl_risk_build = None
    try:
        from .data_logic_correctness import (
            build_potential_json as dl_potential_build,  # type: ignore
            build_risk_json as dl_risk_build,  # type: ignore
        )
    except Exception:
        try:
            from inference.data_logic_correctness import (
                build_potential_json as dl_potential_build,  # type: ignore
                build_risk_json as dl_risk_build,  # type: ignore
            )
        except Exception:
            dl_potential_build = dl_risk_build = None

    data_logic_correctness_result = {
        "potential": None,
        "risk": None,
    }
    
    if dl_potential_build is not None:
        try:
            data_logic_correctness_result["potential"] = dl_potential_build(str(p))
        except Exception as e:
            data_logic_correctness_result["potential"] = {"error": f"电位提取失败: {e}"}
    else:
        data_logic_correctness_result["potential"] = {"error": "build_potential_json 函数不可用"}
    
    if dl_risk_build is not None:
        try:
            data_logic_correctness_result["risk"] = dl_risk_build(str(p))
        except Exception as e:
            data_logic_correctness_result["risk"] = {"error": f"风险提取失败: {e}"}
    else:
        data_logic_correctness_result["risk"] = {"error": "build_risk_json 函数不可用"}

    # luxian_messages：两种情况
    # - 若类型中不含“人员密集型”，直接给出类型并声明无需审核（文本-only，且不调用模型）
    # - 否则，输出 evac/assembly 两类消息
    luxian_messages = None
    try:
        lx_get_types = None
        try:
            from .luxian_extract import get_hca_types_from_docx as lx_get_types  # type: ignore
        except Exception:
            try:
                from inference.luxian_extract import get_hca_types_from_docx as lx_get_types  # type: ignore
            except Exception:
                lx_get_types = None

        types_list = lx_get_types(str(p)) if lx_get_types else []
        if types_list and ("人员密集型" not in types_list):
            type_str = "、".join(types_list)
            luxian_messages = f"高后果区类型：{type_str or '未识别'}；非人员密集型，无需审核。"
        else:
            luxian_messages = {
                "evac": luxian_evac_messages,
                "assembly": luxian_assembly_messages,
            }
    except Exception:
        luxian_messages = {
            "evac": luxian_evac_messages,
            "assembly": luxian_assembly_messages,
        }

    # 构建原始 JSON 结果
    result_json = {
        "document": str(p),
        "qianzi_messages": qianzi_messages,
        "content_consistency_result": content_consistency_result,
        "yingxiangtu_messages": yingxiangtu_messages,
        "ruchangluxian_messages": ruchangluxian_messages,
        "luxian_messages": luxian_messages,
        "tupian_yizhixing_messages": tupian_yizhixing_messages,
        "context_consistency_result": context_consistency_result,
        "standard_compliance_messages": standard_compliance_messages,
        "data_logic_correctness_result": data_logic_correctness_result,
        "temporal_logic_result": temporal_logic_result,
    }
    
    # 尝试导入并调用 process_json_with_model 处理 JSON
    process_json_with_model = None
    
    # 方法1: 尝试绝对导入（适合直接运行脚本的情况）
    # 注意：导入 model.py 时会自动加载模型，这可能需要几分钟
    print("[INFO] 开始导入模型模块（将自动加载大模型，请耐心等待）...", file=sys.stderr, flush=True)
    try:
        from inference.model import process_json_with_model  # type: ignore
        print("[DEBUG] 成功通过绝对导入加载 process_json_with_model", file=sys.stderr, flush=True)
    except Exception as e1:
        error_msg = str(e1)
        print(f"[DEBUG] 绝对导入失败: {error_msg}", file=sys.stderr)
        # 检查是否是 PyTorch DLL 加载失败
        if "WinError 1114" in error_msg or "c10.dll" in error_msg or "DLL" in error_msg:
            print("[错误] PyTorch DLL 加载失败，这通常是环境配置问题", file=sys.stderr)
            print("[提示] 可能的解决方案：", file=sys.stderr)
            print("  1. 重新安装 PyTorch: pip uninstall torch torchvision && pip install torch torchvision", file=sys.stderr)
            print("  2. 安装 Visual C++ Redistributable（如果缺失）", file=sys.stderr)
            print("  3. 检查 CUDA 版本是否匹配", file=sys.stderr)
            print("  4. 尝试使用 CPU 版本的 PyTorch: pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu", file=sys.stderr)
        # 方法2: 尝试相对导入（适合作为模块导入的情况）
        try:
            from .model import process_json_with_model  # type: ignore
            print("[DEBUG] 成功通过相对导入加载 process_json_with_model", file=sys.stderr)
        except Exception as e2:
            print(f"[DEBUG] 相对导入也失败: {e2}", file=sys.stderr)
            # 方法3: 尝试直接导入 model 文件（使用 sys.path）
            try:
                import importlib.util
                model_path = Path(__file__).parent / "model.py"
                if model_path.exists():
                    spec = importlib.util.spec_from_file_location("model", model_path)
                    model_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(model_module)
                    process_json_with_model = getattr(model_module, "process_json_with_model", None)
                    if process_json_with_model:
                        print("[DEBUG] 成功通过直接导入文件加载 process_json_with_model", file=sys.stderr)
                    else:
                        print("[DEBUG] 导入文件成功但未找到 process_json_with_model 函数", file=sys.stderr)
                else:
                    print(f"[DEBUG] model.py 文件不存在: {model_path}", file=sys.stderr)
            except Exception as e3:
                print(f"[DEBUG] 直接导入文件也失败: {e3}", file=sys.stderr)
                # 检查是否是依赖缺失错误
                error_msg = str(e3)
                if "WinError 1114" in error_msg or "c10.dll" in error_msg or "DLL" in error_msg:
                    print("[错误] PyTorch DLL 加载失败", file=sys.stderr)
                    print("[提示] 请参考上面的解决方案修复 PyTorch 环境", file=sys.stderr)
                elif "No module named" in error_msg:
                    missing_module = error_msg.split("'")[1] if "'" in error_msg else "未知模块"
                    print(f"[错误] 缺少必需的 Python 模块: {missing_module}", file=sys.stderr)
                    print(f"[提示] 请在当前环境中安装缺失的依赖:", file=sys.stderr)
                    print(f"      pip install {missing_module}", file=sys.stderr)
                    if missing_module == "torchvision":
                        print(f"      或安装完整依赖: pip install torch torchvision transformers qwen-vl-utils bitsandbytes", file=sys.stderr)
                else:
                    import traceback
                    print(traceback.format_exc(), file=sys.stderr)
                process_json_with_model = None
    
    # 调用 process_json_with_model 处理 JSON，自动处理所有包含 role="user" 的消息
    if process_json_with_model is not None:
        print("开始处理 JSON，调用大模型...", file=sys.stderr)
        try:
            processed_result = process_json_with_model(result_json, max_new_tokens=128, replace_key=None)
            print("处理完成，输出结果...", file=sys.stderr)
            print(json.dumps(processed_result, ensure_ascii=False, indent=2))
        except Exception as e:
            import traceback
            print(f"处理 JSON 失败: {e}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            # 如果处理失败，打印原始结果
            print(json.dumps(result_json, ensure_ascii=False, indent=2))
    else:
        # 如果 process_json_with_model 不可用，打印原始结果
        print("process_json_with_model 不可用，输出原始结果", file=sys.stderr)
        print(json.dumps(result_json, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()


