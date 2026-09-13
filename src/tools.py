"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer phục vụ cho MCP Server.
"""

import json
import os
from typing import Dict, Any, List, Optional

# ==============================================================================
# 0. NẠP DỮ LIỆU MÔ PHỎNG CHƯƠNG TRÌNH ĐÀO TẠO (dùng cho 'program_recommend')
# ==============================================================================

def _load_config_json(filename: str) -> Dict[str, Any]:
    """Đọc file dữ liệu mô phỏng trong thư mục config/"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(base_dir, "config", filename), "r", encoding="utf-8") as f:
        return json.load(f)


PROGRAM_CATALOG = _load_config_json("mock_programs_info.json")
INTEREST_VOCABULARY = PROGRAM_CATALOG["metadata"]["interest_vocabulary"]
APTITUDE_KEYS = PROGRAM_CATALOG["metadata"]["aptitude_keys"]

# Mô tả tiếng Việt cho từng trục năng lực, phục vụ LLM trích xuất tham số
_APTITUDE_LABELS = {
    "math_intensity": "Mức độ yêu thích/khả năng Toán học",
    "coding_intensity": "Mức độ yêu thích/khả năng Lập trình",
    "lab_work": "Mức độ yêu thích làm việc trong phòng thí nghiệm/thực hành",
    "people_interaction": "Mức độ yêu thích giao tiếp, làm việc với con người",
    "creativity": "Mức độ sáng tạo, thiết kế ý tưởng mới",
    "business_acumen": "Mức độ nhạy bén kinh doanh, quản trị"
}
APTITUDE_DESCRIPTIONS: Dict[str, str] = {str(k): str(_APTITUDE_LABELS.get(k, k)) for k in APTITUDE_KEYS}

# Nhãn rút gọn dùng khi diễn giải lý do gợi ý
_APTITUDE_SHORT_LABELS = {
    "math_intensity": "Toán học",
    "coding_intensity": "Lập trình",
    "lab_work": "Thực hành phòng lab",
    "people_interaction": "Giao tiếp với con người",
    "creativity": "Sáng tạo",
    "business_acumen": "Nhạy bén kinh doanh"
}
APTITUDE_SHORT_LABELS: Dict[str, str] = {str(k): str(_APTITUDE_SHORT_LABELS.get(k, k)) for k in APTITUDE_KEYS}

# Trọng số chấm điểm gợi ý ngành (tổng = 1.0, tự động chuẩn hóa lại nếu thiếu dữ liệu)
RECOMMEND_WEIGHTS = {
    "interest": 0.55,   # Độ trùng khớp lĩnh vực quan tâm
    "aptitude": 0.35,   # Độ tương thích năng lực
    "outcome": 0.10     # Triển vọng việc làm của chương trình
}

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA (TASK 1.2)
# ==============================================================================

TOOLS_SCHEMA = [
    # Tool 1: Đã được định nghĩa mẫu sẵn cho Học viên tham khảo
    {
        "name": "academic_query",
        "description": "Tra cứu hồ sơ và thông tin học vụ của sinh viên VinUni bằng mã sinh viên.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {
                    "type": "string",
                    "description": "Mã sinh viên cần tra cứu (ví dụ: 'SV2026001')"
                }
            },
            "required": ["student_id"]
        }
    },
    
    # --------------------------------------------------------------------------
    # TODO 1.2: HỌC VIÊN HOÀN THIỆN TOOL SCHEMA CHO 'schedule_appointment'
    # 🎯 YÊU CẦU THIẾT KẾ SCHEMA (JSON SCHEMA STANDARD):
    # 1. Tool dùng để đặt lịch hẹn tư vấn học vụ với Cố vấn học tập VinUni.
    # 2. Thiết kế các tham số (properties) để LLM trích xuất:
    #    - student_id (string): Mã sinh viên cần đặt lịch (ví dụ: 'SV2026001')
    #    - datetime_str (string): Thời gian hẹn (ví dụ: '14:00 15/09/2026')
    #    - advisor_name (string): Tên cố vấn học tập
    # 3. Khai báo danh sách các trường bắt buộc (required).
    # --------------------------------------------------------------------------
    {
        "name": "schedule_appointment",
        "description": "Đặt lịch hẹn tư vấn học vụ với Cố vấn học tập VinUni.",
        "parameters": {
            "type": "object",
            "properties": {
                # TODO 1.2: Khai báo các thuộc tính tham số cho Tool tại đây...
                "student_id": {
                    "type": "string",
                    "description": "Mã sinh viên cần đặt lịch (ví dụ: 'SV2026001')"
                },
                "datetime_str": {
                    "type": "string",
                    "description": "Thời gian hẹn (ví dụ: '14:00 15/09/2026')"
                },
                "advisor_name": {
                    "type": "string",
                    "description": "Tên cố vấn học tập"
                }
            },
            "required": ["student_id", "datetime_str", "advisor_name"] # TODO 1.2: Khai báo danh sách các trường bắt buộc tại đây...
        }
    },
    # SCHEMA cho 'course_lookup' giúp sinh viên tra cứu thông tin môn học (không bắt buộc triển khai, chỉ để tham khảo)
    {
    "name": "course_lookup",
    "description": "Tra cứu thông tin học phần VinUni theo mã học phần, từ khóa tên môn, hoặc tên giảng viên.",
    "parameters": {
        "type": "object",
        "properties": {
            "course_id":  {"type": "string", "description": "Mã học phần (ví dụ: 'COMP3050')"},
            "keyword":    {"type": "string", "description": "Từ khóa tên môn học (ví dụ: 'học máy')"},
            "instructor": {"type": "string", "description": "Tên giảng viên phụ trách"}
        },
        "required": []
    }
    },
    # SCHEMA cho 'program_recommend': gợi ý ngành học cho thí sinh tiềm năng (prospective students)
    {
        "name": "program_recommend",
        "description": (
            "Gợi ý các chương trình đào tạo VinUni phù hợp nhất với thí sinh tiềm năng, "
            "dựa trên sở thích, năng lực, học lực và ngân sách. "
            "Càng nhiều thông tin về thí sinh thì kết quả càng chính xác."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "interests": {
                    "type": "array",
                    "description": "Danh sách lĩnh vực thí sinh quan tâm (chọn từ bộ từ khóa chuẩn).",
                    "items": {"type": "string", "enum": INTEREST_VOCABULARY}
                },
                "aptitude_profile": {
                    "type": "object",
                    "description": "Tự đánh giá năng lực của thí sinh theo thang điểm 1 (rất thấp) đến 5 (rất cao). Bỏ trống nếu không rõ.",
                    "properties": {
                        key: {"type": "integer", "minimum": 1, "maximum": 5, "description": desc}
                        for key, desc in APTITUDE_DESCRIPTIONS.items()
                    }
                },
                "entry_level": {
                    "type": "string",
                    "description": "Đối tượng tuyển sinh của thí sinh: tốt nghiệp THPT hay đã có bằng cử nhân.",
                    "enum": ["High School", "Bachelor"]
                },
                "high_school_gpa": {
                    "type": "number",
                    "description": "Điểm trung bình THPT theo thang 10 (ví dụ: 9.2)"
                },
                "bachelor_gpa": {
                    "type": "number",
                    "description": "Điểm trung bình đại học theo thang 4 (chỉ dùng khi ứng tuyển bậc sau đại học)"
                },
                "ielts": {
                    "type": "number",
                    "description": "Điểm IELTS của thí sinh (ví dụ: 7.5)"
                },
                "budget_per_year": {
                    "type": "number",
                    "description": "Ngân sách học phí tối đa mỗi năm, đơn vị VND (ví dụ: 900000000)"
                },
                "top_n": {
                    "type": "integer",
                    "description": "Số lượng chương trình muốn gợi ý (mặc định 3)",
                    "minimum": 1,
                    "maximum": 10
                }
            },
            "required": ["interests"]
        }
    }

    ]

# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU & HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================

# Cơ sở dữ liệu sinh viên mở rộng (23 hồ sơ) nạp từ config/mock_students_info.json.
# Dữ liệu đồng bộ với mock_courses_info.json (advisor, enrolled_courses)
# và mock_programs_info.json (program_id, college, scholarship_id).
STUDENT_CATALOG = _load_config_json("mock_students_info.json")
MOCK_DATABASE = STUDENT_CATALOG["students"]


def execute_academic_query(student_id: str) -> str:
    """Thực thi tra cứu học vụ theo mã sinh viên"""
    student = MOCK_DATABASE.get(student_id.strip().upper())
    if student:
        return json.dumps({
            "status": "SUCCESS",
            "student_id": student_id,
            "data": student
        }, ensure_ascii=False)
    else:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy dữ liệu sinh viên có mã '{student_id}'"
        }, ensure_ascii=False)


def execute_schedule_appointment(student_id: str, datetime_str: str, advisor_name: str = "PGS.TS Nguyễn Văn A") -> str:
    """Thực thi đặt lịch hẹn tư vấn học vụ"""
    return json.dumps({
        "status": "SUCCESS",
        "booking_id": f"BK-{student_id}-99",
        "student_id": student_id,
        "datetime": datetime_str,
        "advisor": advisor_name,
        "message": f"Đặt lịch thành công cho sinh viên {student_id} với {advisor_name} vào lúc {datetime_str}."
    }, ensure_ascii=False)

import os

def _load_courses():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(base_dir, "config", "mock_courses_info.json"), "r", encoding="utf-8") as f:
        return json.load(f)

COURSE_CATALOG = _load_courses()

def execute_course_lookup(course_id: str = "", keyword: str = "", instructor: str = "") -> str:
    """Thực thi tra cứu thông tin môn học (không bắt buộc triển khai)"""
    # Mô phỏng dữ liệu môn học
    MOCK_COURSES = COURSE_CATALOG["courses"]
    
    results = MOCK_COURSES
    if course_id:
        results = [c for c in results if c["course_id"].upper() == course_id.strip().upper()]
    if keyword:
        k = keyword.strip().lower()
        results = [c for c in results if k in c["name_vi"].lower() or k in c["name_en"].lower()]
    if instructor:
        ins = instructor.strip().lower()
        results = [c for c in results if ins in c["instructor"].lower()]

    if not results:
        return json.dumps({"status": "NOT_FOUND",
                           "message": "Không tìm thấy học phần phù hợp với tiêu chí tra cứu."},
                          ensure_ascii=False)
    return json.dumps({
        "status": "SUCCESS",
        "count": len(results),
        "message": "Tìm thấy {} học phần: {}".format(
            len(results),
            "; ".join(f"{c['course_id']} - {c['name_vi']} ({c['credits']} tín chỉ, GV: {c['instructor']}, {c['status']})"
                      for c in results)),
        "courses": results
    }, ensure_ascii=False)


# ------------------------------------------------------------------------------
# TOOL: program_recommend - Gợi ý ngành học cho thí sinh tiềm năng
# Pipeline: Lọc điều kiện đầu vào -> Chấm điểm có trọng số -> Xếp hạng Top-N kèm lý do
# ------------------------------------------------------------------------------

def _format_vnd(amount: float) -> str:
    """Định dạng số tiền VND cho dễ đọc (ví dụ: 940 triệu, 1.50 tỷ)"""
    if amount >= 1_000_000_000:
        return f"{amount / 1_000_000_000:.2f} tỷ VND"
    return f"{amount / 1_000_000:.0f} triệu VND"


def _normalize_interests(interests: Any) -> List[str]:
    """Chuẩn hóa danh sách sở thích (LLM đôi khi trả về chuỗi thay vì mảng)"""
    if isinstance(interests, str):
        interests = interests.split(",")
    if not isinstance(interests, (list, tuple)):
        return []
    return [str(i).strip().lower() for i in interests if str(i).strip()]


def _check_eligibility(program: Dict[str, Any], profile: Dict[str, Any]) -> List[str]:
    """Lọc điều kiện đầu vào. Trả về danh sách lý do KHÔNG đạt (rỗng = đủ điều kiện).
    Tiêu chí nào thí sinh chưa cung cấp thông tin thì bỏ qua, không loại chương trình."""
    fails = []
    adm = program["admission"]

    entry_level = profile.get("entry_level")
    if entry_level and program["entry_level"] != entry_level:
        fails.append(f"Chương trình tuyển sinh từ '{program['entry_level']}', không khớp đối tượng '{entry_level}'")

    ielts = profile.get("ielts")
    if ielts is not None and ielts < adm["ielts_min"]:
        fails.append(f"IELTS {ielts} chưa đạt yêu cầu tối thiểu {adm['ielts_min']}")

    hs_gpa = profile.get("high_school_gpa")
    if hs_gpa is not None and "high_school_gpa_min" in adm and hs_gpa < adm["high_school_gpa_min"]:
        fails.append(f"GPA THPT {hs_gpa} chưa đạt yêu cầu tối thiểu {adm['high_school_gpa_min']}")

    ba_gpa = profile.get("bachelor_gpa")
    if ba_gpa is not None and "bachelor_gpa_min" in adm and ba_gpa < adm["bachelor_gpa_min"]:
        fails.append(f"GPA đại học {ba_gpa} chưa đạt yêu cầu tối thiểu {adm['bachelor_gpa_min']}")

    budget = profile.get("budget_per_year")
    if budget is not None and budget < program["tuition_per_year"]:
        fails.append(
            f"Học phí {_format_vnd(program['tuition_per_year'])}/năm vượt ngân sách {_format_vnd(budget)}/năm"
        )

    return fails


def _score_program(program: Dict[str, Any], interests: List[str],
                   aptitude: Dict[str, Any]) -> Dict[str, Any]:
    """Chấm điểm mức độ phù hợp có trọng số. Trả về điểm tổng và các thành phần chi tiết."""
    # (1) Độ trùng khớp lĩnh vực quan tâm (hệ số Jaccard)
    prospect_tags = set(interests)
    program_tags = set(program["interest_tags"])
    matched_tags = sorted(prospect_tags & program_tags)
    union = prospect_tags | program_tags
    interest_score = len(matched_tags) / len(union) if union else 0.0

    # (2) Độ tương thích năng lực (khoảng cách Manhattan chuẩn hóa trên thang 1-5)
    shared_keys = [k for k in APTITUDE_KEYS if isinstance(aptitude.get(k), (int, float))]
    aptitude_score = None
    strong_axes = []
    if shared_keys:
        distance = sum(abs(program["aptitude_profile"][k] - aptitude[k]) for k in shared_keys)
        aptitude_score = 1 - distance / (4 * len(shared_keys))
        # Chỉ nêu bật những trục mà CẢ chương trình lẫn thí sinh đều ở mức cao (>= 4),
        # tránh hiểu nhầm khi hai bên cùng thấp (khoảng cách nhỏ nhưng không phải điểm mạnh)
        strong_axes = sorted(
            (k for k in shared_keys
             if program["aptitude_profile"][k] >= 4 and aptitude[k] >= 4),
            key=lambda k: (abs(program["aptitude_profile"][k] - aptitude[k]), -aptitude[k])
        )

    # (3) Triển vọng việc làm
    outcome_score = program["employment_rate_percent"] / 100

    # Chuẩn hóa lại trọng số khi thiếu dữ liệu năng lực
    components = {"interest": interest_score, "outcome": outcome_score}
    if aptitude_score is not None:
        components["aptitude"] = aptitude_score
    total_weight = sum(RECOMMEND_WEIGHTS[k] for k in components)
    match_score = sum(RECOMMEND_WEIGHTS[k] * v for k, v in components.items()) / total_weight

    return {
        "match_score": round(match_score, 3),
        "interest_score": round(interest_score, 3),
        "aptitude_score": round(aptitude_score, 3) if aptitude_score is not None else None,
        "outcome_score": round(outcome_score, 3),
        "matched_tags": matched_tags,
        "strong_axes": strong_axes[:2]
    }


def _build_reasons(program: Dict[str, Any], scoring: Dict[str, Any]) -> List[str]:
    """Sinh danh sách lý do dễ hiểu giải thích vì sao chương trình được gợi ý"""
    reasons = []

    if scoring["matched_tags"]:
        reasons.append(f"Khớp lĩnh vực quan tâm: {', '.join(scoring['matched_tags'])}")
    else:
        reasons.append(f"Lĩnh vực liên quan: {', '.join(program['interest_tags'])}")

    if scoring["aptitude_score"] is not None:
        fit_text = f"Năng lực tương thích {round(scoring['aptitude_score'] * 100)}% với yêu cầu của chương trình"
        if scoring["strong_axes"]:
            axes = ", ".join(APTITUDE_SHORT_LABELS[k] for k in scoring["strong_axes"])
            fit_text += f", nổi bật ở: {axes}"
        reasons.append(fit_text)

    reasons.append(
        f"Tỷ lệ có việc làm {program['employment_rate_percent']}%, "
        f"lương khởi điểm trung bình {_format_vnd(program['avg_starting_salary_month'])}/tháng"
    )
    reasons.append(
        f"Học phí {_format_vnd(program['tuition_per_year'])}/năm, thời gian đào tạo {program['duration_years']} năm"
    )

    if program.get("partner_university"):
        reasons.append(f"Hợp tác đào tạo với {program['partner_university']}")

    if program["status"] != "OPEN":
        reasons.append(f"⚠️ Lưu ý: chương trình đang ở trạng thái {program['status']}")

    return reasons


def execute_program_recommend(interests: Any, aptitude_profile: Optional[Dict[str, Any]] = None,
                              entry_level: str = "", high_school_gpa: Optional[float] = None,
                              bachelor_gpa: Optional[float] = None, ielts: Optional[float] = None,
                              budget_per_year: Optional[float] = None, top_n: int = 3) -> str:
    """Thực thi gợi ý chương trình đào tạo phù hợp cho thí sinh tiềm năng"""
    normalized_interests = _normalize_interests(interests)
    if not normalized_interests:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": ("Chưa đủ thông tin để gợi ý ngành học. "
                        f"Vui lòng cho biết lĩnh vực thí sinh quan tâm, ví dụ: {', '.join(INTEREST_VOCABULARY[:5])}.")
        }, ensure_ascii=False)

    profile = {
        "entry_level": entry_level.strip() if isinstance(entry_level, str) else "",
        "high_school_gpa": high_school_gpa,
        "bachelor_gpa": bachelor_gpa,
        "ielts": ielts,
        "budget_per_year": budget_per_year
    }
    aptitude = aptitude_profile if isinstance(aptitude_profile, dict) else {}
    top_n = max(1, min(int(top_n or 3), 10))

    # Bước 1: Lọc điều kiện đầu vào
    eligible, rejected = [], []
    for program in PROGRAM_CATALOG["programs"]:
        fails = _check_eligibility(program, profile)
        if not fails:
            eligible.append(program)
        else:
            rejected.append((program, fails))

    # Bước 2: Không có chương trình nào đạt -> nêu các lựa chọn gần đạt nhất và tiêu chí còn thiếu
    if not eligible:
        rejected.sort(key=lambda item: (len(item[1]), item[0]["program_id"]))
        min_fails = len(rejected[0][1]) if rejected else 0
        suggestions = [
            {
                "program_id": p["program_id"],
                "name_vi": p["name_vi"],
                "missing_criteria_count": len(fails),
                "blocking_reasons": fails
            }
            for p, fails in rejected if len(fails) == min_fails
        ][:3]

        message = "Rất tiếc, hiện chưa có chương trình nào khớp hoàn toàn với hồ sơ của thí sinh."
        if suggestions:
            message += (
                f" Các chương trình gần đạt nhất (còn thiếu {min_fails} tiêu chí): " + "; ".join(
                    f"{s['name_vi']} ({', '.join(s['blocking_reasons'])})" for s in suggestions
                ) + ". Thí sinh có thể cân nhắc cải thiện các tiêu chí này hoặc tìm hiểu chính sách học bổng của VinUni."
            )
        return json.dumps({
            "status": "NOT_FOUND",
            "message": message,
            "near_misses": suggestions
        }, ensure_ascii=False)

    # Bước 3: Chấm điểm có trọng số và xếp hạng Top-N
    ranked = []
    for program in eligible:
        scoring = _score_program(program, normalized_interests, aptitude)
        ranked.append({
            "program_id": program["program_id"],
            "name_vi": program["name_vi"],
            "name_en": program["name_en"],
            "college": program["college"],
            "degree_level": program["degree_level"],
            "duration_years": program["duration_years"],
            "tuition_per_year": program["tuition_per_year"],
            "application_deadline": program["application_deadline"],
            "career_outcomes": program["career_outcomes"],
            "program_status": program["status"],
            "match_score": scoring["match_score"],
            "score_breakdown": {
                "interest": scoring["interest_score"],
                "aptitude": scoring["aptitude_score"],
                "outcome": scoring["outcome_score"]
            },
            "reasons": _build_reasons(program, scoring)
        })

    ranked.sort(key=lambda r: (r["match_score"], r["program_id"]), reverse=True)
    results = ranked[:top_n]

    summary = "; ".join(
        f"#{i} {r['name_vi']} ({r['program_id']}, độ phù hợp {round(r['match_score'] * 100)}%) - {r['reasons'][0]}"
        for i, r in enumerate(results, start=1)
    )
    return json.dumps({
        "status": "SUCCESS",
        "count": len(results),
        "eligible_count": len(eligible),
        "message": f"Gợi ý {len(results)} chương trình phù hợp nhất: {summary}.",
        "programs": results
    }, ensure_ascii=False)


# Router gọi tool thực tế
TOOL_ROUTER = {
    "academic_query": execute_academic_query,
    "schedule_appointment": execute_schedule_appointment,
    "course_lookup": execute_course_lookup,
    "program_recommend": execute_program_recommend
}

def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Hàm trung chuyển thực thi tool
    Khi tool_name == "academic_query": Gọi execute_academic_query(**arguments).
    Khi tool_name == "schedule_appointment": Gọi execute_schedule_appointment(**arguments)"""

    if tool_name in TOOL_ROUTER:
        try:
            return TOOL_ROUTER[tool_name](**arguments)
        except Exception as e:
            return json.dumps({"status": "EXECUTION_ERROR", "error": str(e)}, ensure_ascii=False)
    return json.dumps({"status": "UNKNOWN_TOOL", "error": f"Tool '{tool_name}' không tồn tại!"}, ensure_ascii=False)

if __name__ == "__main__":
    # Test nhanh
    print(execute_academic_query("SV2026001"))
    print(execute_schedule_appointment("SV2026001", "14:00 15/09/2026", "PGS.TS Nguyễn Văn A"))
