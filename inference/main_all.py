import json
import sys
from pathlib import Path
from datetime import datetime

# 允许作为脚本直接运行：把项目根目录加入 sys.path，便于使用 inference.* 绝对导入
try:
    _CUR_DIR = Path(__file__).resolve().parent
    _ROOT_DIR = _CUR_DIR.parent
    if str(_ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(_ROOT_DIR))
except Exception:
    pass


DOC_PATH = r"C:/Users/cassi/Desktop/bisai/word-master"  # 改为目录路径
OUTPUT_JSON = r"C:/Users/cassi/Desktop/bisai/inference/batch_results.json"  # 输出 JSON 文件路径


def process_single_document(doc_path: Path) -> dict:
    """处理单个文档并返回结果字典"""
    if not doc_path.exists() or not doc_path.is_file():
        return {"error": f"文档不存在或无效: {doc_path}"}

    p = doc_path

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

    # 调用 standard_compliance 的类型判定函数
    sc_type = None
    try:
        from .standard_compliance import build_standard_compliance_from_docx as sc_type_build  # type: ignore
    except Exception:
        try:
            from inference.standard_compliance import build_standard_compliance_from_docx as sc_type_build  # type: ignore
        except Exception:
            sc_type_build = None

    standard_compliance_result = None
    if sc_type_build is not None:
        try:
            standard_compliance_result = sc_type_build(str(p))  # 返回纯文本
        except Exception as e:
            standard_compliance_result = f"standard_compliance 调用失败: {e}"
    else:
        standard_compliance_result = "standard_compliance 函数不可用"

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

    # 返回结果字典
    return {
        "document": str(p),
        "qianzi_messages": qianzi_messages,
        "content_consistency_result": content_consistency_result,
        "yingxiangtu_messages": yingxiangtu_messages,
        "ruchangluxian_messages": ruchangluxian_messages,
        "luxian_messages": luxian_messages,
        "tupian_yizhixing_messages": tupian_yizhixing_messages,
        "context_consistency_result": context_consistency_result,
        "standard_compliance_result": standard_compliance_result,
        "data_logic_correctness_result": data_logic_correctness_result,
        "temporal_logic_result": temporal_logic_result,
    }


def main():
    """处理目录下的所有文档并保存结果到 JSON"""
    doc_dir = Path(DOC_PATH)
    if not doc_dir.exists() or not doc_dir.is_dir():
        error_msg = {"error": f"目录不存在或无效: {DOC_PATH}"}
        print(json.dumps(error_msg, ensure_ascii=False))
        return

    # 查找所有支持的文档文件
    supported_extensions = [".docx", ".doc", ".pdf"]
    all_files = []
    for ext in supported_extensions:
        all_files.extend(doc_dir.rglob(f"*{ext}"))
    
    # 去重并排序
    all_files = sorted(set(all_files))
    
    if not all_files:
        error_msg = {"error": f"在目录 {DOC_PATH} 中未找到支持的文档文件 (.docx, .doc, .pdf)"}
        print(json.dumps(error_msg, ensure_ascii=False))
        return

    print(f"找到 {len(all_files)} 个文档文件，开始处理...")
    
    # 处理所有文件
    results = []
    for idx, file_path in enumerate(all_files, 1):
        print(f"[{idx}/{len(all_files)}] 处理: {file_path.name}")
        try:
            result = process_single_document(file_path)
            results.append(result)
        except Exception as e:
            results.append({
                "document": str(file_path),
                "error": f"处理过程中发生异常: {e}"
            })

    # 构建最终输出
    output_data = {
        "batch_processing": True,
        "directory": str(doc_dir),
        "processed_at": datetime.now().isoformat(),
        "total_documents": len(all_files),
        "successful_count": len([r for r in results if "error" not in r]),
        "failed_count": len([r for r in results if "error" in r]),
        "results": results
    }

    # 保存到 JSON 文件
    output_path = Path(OUTPUT_JSON)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n处理完成！结果已保存到: {output_path}")
    print(f"成功: {output_data['successful_count']}, 失败: {output_data['failed_count']}")


if __name__ == "__main__":
    main()


