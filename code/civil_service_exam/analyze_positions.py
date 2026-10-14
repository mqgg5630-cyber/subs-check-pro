#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Transparent preliminary screening for a Chinese civil-service position sheet.

This tool does not decide whether someone is legally eligible or predict their
chance of being hired. It turns a public XLS/XLSX position table plus the
user's own stated preferences into an auditable shortlist and flags every
ambiguous requirement for manual verification against the official notice.

Examples
--------
# First copy profile.template.json to a LOCAL, ignored profile file.
python3 code/civil_service_exam/analyze_positions.py \
  --input 'results/civil_service_exam/source/中央机关及其直属机构2027年度考试录用公务员招考简章.xls' \
  --profile config/civil_service_profile.local.json

# Normalize the public table only (no personal profile required).
python3 code/civil_service_exam/analyze_positions.py --input path/to/notice.xls --no-profile

Dependencies: pandas, xlrd (for .xls), openpyxl (for .xlsx).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    import pandas as pd
except ModuleNotFoundError as exc:  # pragma: no cover - handled for end users
    raise SystemExit(
        "Missing spreadsheet dependencies. Install with:\n"
        "  python -m pip install -r code/civil_service_exam/requirements.txt"
    ) from exc

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "results" / "civil_service_exam" / "source"
DEFAULT_PROFILE = ROOT / "config" / "civil_service_profile.local.json"
DEFAULT_OUTPUT = ROOT / "results" / "civil_service_exam" / "local_analysis"

# Column aliases cover the usual national civil-service workbook wording, while
# preserving every original column in the normalized export. New wording is
# surfaced in the report rather than silently guessed.
COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "department_code": ("部门代码", "招录机关代码", "机关代码"),
    "department": ("部门名称", "招录机关名称", "招录机关", "部门"),
    "agency": ("用人司局", "招录单位", "机构名称", "用人单位"),
    "position_code": ("职位代码", "招考职位代码", "职位编号", "岗位代码"),
    "position": ("职位名称", "招考职位名称", "岗位名称"),
    "position_nature": ("职位属性", "职位性质", "岗位属性"),
    "position_intro": ("职位简介", "职位介绍", "工作内容", "职位说明"),
    "level": ("机构层级", "机构级别", "单位层级"),
    "exam_category": ("考试类别", "笔试类别", "专业科目"),
    "recruit_count": ("招考人数", "招录人数", "计划招录人数", "招考计划数"),
    "major_requirement": ("专业", "专业要求", "所学专业", "学科门类"),
    "education_requirement": ("学历", "学历要求"),
    "degree_requirement": ("学位", "学位要求"),
    "political_requirement": ("政治面貌", "政治面貌要求"),
    "grassroots_requirement": ("基层工作最低年限", "基层工作年限", "基层工作经历"),
    "service_requirement": ("服务基层项目工作经历", "服务基层项目", "基层服务项目"),
    "english_requirement": ("外语水平", "外语要求", "英语等级", "英语要求", "四六级要求"),
    "household_requirement": ("户籍", "户籍要求", "生源地"),
    "location": ("工作地点", "工作所在地", "工作地", "落户地点", "地点"),
    "remarks": ("备注", "其他条件", "说明", "补充说明"),
}

# A province preference should still match common city-level workplace strings.
# This is only a location-label expansion, not an inference about the applicant.
PROVINCE_ALIASES: dict[str, tuple[str, ...]] = {
    "福建": ("福建", "福州", "厦门", "泉州", "漳州", "莆田", "三明", "南平", "龙岩", "宁德"),
    "山东": ("山东", "济南", "青岛", "烟台", "潍坊", "威海", "淄博", "临沂", "济宁", "泰安", "日照", "东营", "滨州", "德州", "聊城", "菏泽", "枣庄"),
    "四川": ("四川", "成都", "绵阳", "德阳", "乐山", "宜宾", "泸州", "南充", "达州", "自贡", "攀枝花", "眉山", "资阳", "广元", "遂宁", "内江", "广安", "雅安", "巴中", "阿坝", "甘孜", "凉山"),
}

OPEN_REQUIREMENT = ("不限", "无限制", "不限制", "无", "无要求", "专业不限", "无基层工作经历", "没有要求")
SENSITIVE_RESTRICTION = ("限男性", "限女性", "性别", "民族", "残疾", "身高", "视力")

EDU_LEVELS = {
    "高中": 1,
    "中专": 1,
    "大专": 2,
    "专科": 2,
    "本科": 3,
    "学士": 3,
    "硕士": 4,
    "研究生": 4,
    "博士": 5,
}
CHINESE_NUMBERS = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5}

DEFAULT_WEIGHTS = {
    "location": 35,
    "department": 20,
    "position": 20,
    "major": 15,
    "eligibility_clarity": 10,
}


@dataclass
class Assessment:
    status: str  # match | review | mismatch
    message: str


def text(value: Any) -> str:
    """Convert Excel values to a stable, space-normalized string."""
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    value = str(value).replace("\r", " ").replace("\n", " ").replace("\u3000", " ")
    value = re.sub(r"\s+", " ", value).strip()
    return "" if value.lower() in {"nan", "none"} else value


def key(value: Any) -> str:
    return re.sub(r"[\s\-_（）()【】\[\]：:，,。．/]+", "", text(value)).lower()


def any_contains(haystack: str, needles: Iterable[str]) -> list[str]:
    source = text(haystack).lower()
    return [needle for needle in (text(x) for x in needles) if needle and needle.lower() in source]


def is_open_requirement(requirement: str) -> bool:
    value = text(requirement)
    if not value:
        return False
    return any(token in value for token in OPEN_REQUIREMENT)


def find_default_input() -> Path | None:
    candidates = sorted(
        [*SOURCE_DIR.glob("*.xls"), *SOURCE_DIR.glob("*.xlsx")],
        key=lambda item: item.stat().st_mtime if item.exists() else 0,
        reverse=True,
    )
    return candidates[0] if candidates else None


def score_header_row(frame: pd.DataFrame) -> int:
    aliases = [key(alias) for values in COLUMN_ALIASES.values() for alias in values]
    total = 0
    for cell in frame.tolist():
        label = key(cell)
        if not label:
            continue
        if any(alias == label or (len(alias) >= 3 and alias in label) for alias in aliases):
            total += 1
    return total


def load_position_table(input_path: Path, requested_sheet: str | None = None) -> tuple[pd.DataFrame, str, int]:
    """Locate a header row even when the workbook has title/merged rows first."""
    try:
        raw_book = pd.read_excel(input_path, sheet_name=None, header=None, dtype=str)
    except Exception as exc:
        suffix = input_path.suffix.lower()
        engine_hint = "xlrd" if suffix == ".xls" else "openpyxl"
        raise RuntimeError(
            f"Unable to read {input_path.name}. For {suffix or 'this'} files, "
            f"install the required Excel engine ({engine_hint}) from requirements.txt.\n{exc}"
        ) from exc

    if requested_sheet:
        if requested_sheet not in raw_book:
            raise ValueError(f"Sheet not found: {requested_sheet}. Available: {', '.join(map(str, raw_book))}")
        raw_book = {requested_sheet: raw_book[requested_sheet]}

    best: tuple[int, str, int] | None = None
    for sheet_name, raw in raw_book.items():
        for header_row in range(min(len(raw), 30)):
            score = score_header_row(raw.iloc[header_row])
            candidate = (score, str(sheet_name), header_row)
            if best is None or candidate[0] > best[0]:
                best = candidate
    if best is None or best[0] < 3:
        sheet_summary = ", ".join(f"{name}({len(frame)} rows)" for name, frame in raw_book.items())
        raise ValueError(
            "Could not confidently locate a position-table header row. "
            f"Sheets scanned: {sheet_summary}. Use --sheet or add aliases in COLUMN_ALIASES."
        )

    _, sheet_name, header_row = best
    try:
        table = pd.read_excel(input_path, sheet_name=sheet_name, header=header_row, dtype=str)
    except Exception as exc:
        raise RuntimeError(f"Failed to reopen selected sheet '{sheet_name}': {exc}") from exc
    table = table.dropna(axis=0, how="all").copy()
    table.columns = [text(column) for column in table.columns]
    table = table.loc[:, [column for column in table.columns if column and not column.lower().startswith("unnamed")]]
    table.insert(0, "_source_excel_row", range(header_row + 2, header_row + 2 + len(table)))
    table.insert(0, "_source_sheet", sheet_name)
    return table, sheet_name, header_row


def map_columns(columns: Iterable[str]) -> dict[str, str]:
    """Map canonical fields to the most specific available raw Excel column."""
    result: dict[str, str] = {}
    available = [text(column) for column in columns]
    for field, aliases in COLUMN_ALIASES.items():
        candidates: list[tuple[int, str]] = []
        for column in available:
            normalized = key(column)
            if not normalized:
                continue
            for alias in aliases:
                normalized_alias = key(alias)
                if normalized == normalized_alias:
                    candidates.append((1000 + len(normalized_alias), column))
                elif len(normalized_alias) >= 3 and normalized_alias in normalized:
                    candidates.append((len(normalized_alias), column))
        if candidates:
            result[field] = max(candidates, key=lambda item: item[0])[1]
    return result


def cell(row: pd.Series, column_map: dict[str, str], field: str) -> str:
    raw_column = column_map.get(field)
    return text(row[raw_column]) if raw_column and raw_column in row.index else ""


def highest_education(values: Iterable[str]) -> int | None:
    best: int | None = None
    for raw in values:
        normalized = text(raw)
        for label, level in EDU_LEVELS.items():
            if label in normalized:
                best = level if best is None else max(best, level)
    return best


def requested_min_education(requirement: str) -> int | None:
    normalized = text(requirement)
    hits = [level for label, level in EDU_LEVELS.items() if label in normalized]
    return max(hits) if hits else None


def assess_education(requirement: str, profile: dict[str, Any]) -> Assessment:
    requirement = text(requirement)
    supplied = [text(item) for item in profile.get("education", []) if text(item)]
    if not requirement:
        return Assessment("review", "Excel did not provide a recognizable education requirement")
    if is_open_requirement(requirement):
        return Assessment("match", "education requirement is open")
    if not supplied:
        return Assessment("review", f"education required: {requirement}; profile has no education value")
    candidate_level = highest_education(supplied)
    required_level = requested_min_education(requirement)
    if candidate_level is None or required_level is None:
        return Assessment("review", f"manual education comparison needed: profile={'; '.join(supplied)} / requirement={requirement}")
    if "及以上" in requirement and candidate_level >= required_level:
        return Assessment("match", f"education level appears to meet '{requirement}'")
    if any(item in requirement for item in supplied):
        return Assessment("match", f"profile education appears in requirement '{requirement}'")
    # A higher degree is often acceptable, but wording such as "仅限本科" must
    # be read literally. Keep such cases for human confirmation rather than deny.
    if candidate_level >= required_level:
        return Assessment("review", f"candidate level is higher/equal, but wording needs manual check: {requirement}")
    return Assessment("mismatch", f"profile education {'/'.join(supplied)} is below or absent from '{requirement}'")


def assess_degree(requirement: str, profile: dict[str, Any]) -> Assessment:
    requirement = text(requirement)
    supplied = [text(item) for item in profile.get("degree", []) if text(item)]
    if not requirement:
        return Assessment("review", "Excel did not provide a recognizable degree requirement")
    if is_open_requirement(requirement):
        return Assessment("match", "degree requirement is open")
    if not supplied:
        return Assessment("review", f"degree required: {requirement}; profile has no degree value")
    candidate_level = highest_education(supplied)
    required_level = requested_min_education(requirement)
    if candidate_level is None or required_level is None:
        return Assessment("review", f"manual degree comparison needed: profile={'; '.join(supplied)} / requirement={requirement}")
    if "及以上" in requirement and candidate_level >= required_level:
        return Assessment("match", f"degree level appears to meet '{requirement}'")
    if any(item in requirement for item in supplied):
        return Assessment("match", f"profile degree appears in requirement '{requirement}'")
    if candidate_level >= required_level:
        return Assessment("review", f"candidate degree is higher/equal, but wording needs manual check: {requirement}")
    return Assessment("mismatch", f"profile degree {'/'.join(supplied)} is below or absent from '{requirement}'")


def assess_major(requirement: str, profile: dict[str, Any]) -> Assessment:
    requirement = text(requirement)
    majors = [text(item) for item in profile.get("major_keywords", []) if text(item)]
    if not requirement:
        return Assessment("review", "Excel did not provide a recognizable major requirement")
    if is_open_requirement(requirement):
        return Assessment("match", "major requirement is open")
    if not majors:
        return Assessment("review", f"major required: {requirement}; profile has no major keywords")
    hits = any_contains(requirement, majors)
    if hits:
        return Assessment("match", f"major keyword match: {', '.join(hits)}")
    if any(token in requirement for token in ("相关专业", "专业目录", "学科门类")):
        return Assessment("review", f"no literal major keyword match; official catalogue needs review: {requirement}")
    return Assessment("mismatch", f"none of profile major keywords match: {requirement}")


def assess_political(requirement: str, profile: dict[str, Any]) -> Assessment:
    requirement = text(requirement)
    status = text(profile.get("political_status", ""))
    if not requirement or is_open_requirement(requirement):
        return Assessment("match", "political-status requirement is open")
    if not status:
        return Assessment("review", f"political-status requirement: {requirement}; profile omitted this optional field")
    if status in requirement:
        return Assessment("match", f"political status '{status}' appears to meet requirement")
    if status in {"群众", "无党派人士", "其他"} and ("党员" in requirement or "团员" in requirement):
        return Assessment("mismatch", f"requirement '{requirement}' conflicts with stated political status '{status}'")
    return Assessment("review", f"manual political-status comparison needed: profile={status} / requirement={requirement}")


def required_years(requirement: str) -> int | None:
    value = text(requirement)
    if not value or is_open_requirement(value):
        return 0
    match = re.search(r"(\d+)\s*年", value)
    if match:
        return int(match.group(1))
    for character, number in CHINESE_NUMBERS.items():
        if f"{character}年" in value:
            return number
    return None


def assess_grassroots(requirement: str, profile: dict[str, Any]) -> Assessment:
    requirement = text(requirement)
    required = required_years(requirement)
    years = profile.get("grassroots_years", None)
    if required == 0:
        return Assessment("match", "no minimum grassroots experience identified")
    if required is None:
        return Assessment("review", f"manual grassroots comparison needed: {requirement or 'missing requirement'}")
    if years is None or years == "":
        return Assessment("review", f"requires at least {required} grassroots year(s); profile omitted duration")
    try:
        supplied = float(years)
    except (TypeError, ValueError):
        return Assessment("review", f"profile grassroots_years is not numeric: {years!r}")
    if supplied >= required:
        return Assessment("match", f"profile has {supplied:g} year(s), requirement is {required}")
    return Assessment("mismatch", f"requires {required} grassroots year(s), profile has {supplied:g}")


def assess_service_project(requirement: str, profile: dict[str, Any]) -> Assessment:
    requirement = text(requirement)
    if not requirement or is_open_requirement(requirement):
        return Assessment("match", "no service-project restriction identified")
    restricted = any(token in requirement for token in ("服务基层项目", "三支一扶", "大学生村官", "特岗教师", "西部计划"))
    if not restricted:
        return Assessment("review", f"manual service-project comparison needed: {requirement}")
    supplied = profile.get("has_service_project_experience", None)
    if supplied is None:
        return Assessment("review", f"service-project requirement: {requirement}; profile omitted this field")
    if bool(supplied):
        return Assessment("match", "profile states service-project experience")
    return Assessment("mismatch", f"requires service-project experience: {requirement}")


def assess_english(all_text: str, profile: dict[str, Any]) -> Assessment:
    requirement = text(all_text)
    six_matches = list(re.finditer(r"(?:CET[- ]?6|大学英语六级|英语六级).{0,24}", requirement, flags=re.IGNORECASE))
    four_matches = list(re.finditer(r"(?:CET[- ]?4|大学英语四级|英语四级).{0,24}", requirement, flags=re.IGNORECASE))
    if not six_matches and not four_matches:
        return Assessment("match", "no explicit CET-4/CET-6 restriction found in mapped text")

    def score_threshold(matches: list[re.Match[str]]) -> int | None:
        for match in matches:
            score = re.search(r"([45]\d{2})\s*分", match.group(0))
            if score:
                return int(score.group(1))
        return None

    if six_matches:
        passed = profile.get("cet6_passed", None)
        if passed is None:
            return Assessment("review", "position appears to require CET-6; profile omitted CET-6 status")
        if not bool(passed):
            return Assessment("mismatch", "position appears to require CET-6, but profile states it was not passed")
        threshold = score_threshold(six_matches)
        exact = profile.get("cet6_score", None)
        upper_bound = profile.get("cet6_score_upper_bound", None)
        if threshold is None:
            return Assessment("match", "profile states CET-6 passed")
        if exact not in (None, ""):
            try:
                return Assessment("match" if float(exact) >= threshold else "mismatch", f"CET-6 score comparison: {exact} vs {threshold}")
            except (TypeError, ValueError):
                return Assessment("review", f"CET-6 score is not numeric: {exact!r}")
        if upper_bound not in (None, ""):
            try:
                if float(upper_bound) < threshold:
                    return Assessment("mismatch", f"profile CET-6 score is below {threshold}")
            except (TypeError, ValueError):
                return Assessment("review", f"CET-6 score upper bound is not numeric: {upper_bound!r}")
        if threshold <= 425:
            return Assessment("match", f"CET-6 pass is consistent with threshold {threshold}")
        return Assessment("review", f"CET-6 pass alone cannot confirm threshold {threshold}")

    passed = profile.get("cet4_passed", None)
    if passed is None:
        return Assessment("review", "position appears to require CET-4; profile omitted CET-4 status")
    if not bool(passed):
        return Assessment("mismatch", "position appears to require CET-4, but profile states it was not passed")
    threshold = score_threshold(four_matches)
    if threshold is None or threshold <= 425:
        return Assessment("match", "profile states CET-4 passed")
    return Assessment("review", f"CET-4 pass alone cannot confirm threshold {threshold}")


def assess_sex(all_text: str, profile: dict[str, Any]) -> Assessment:
    requirement = text(all_text)
    male_markers = ("限男性", "限男", "性别:男", "性别：男")
    female_markers = ("限女性", "限女", "性别:女", "性别：女")
    requires_male = any(marker in requirement for marker in male_markers)
    requires_female = any(marker in requirement for marker in female_markers)
    if not requires_male and not requires_female:
        return Assessment("match", "no explicit sex restriction found in mapped text")
    sex = text(profile.get("sex", ""))
    if sex not in {"男", "女"}:
        return Assessment("review", "position has an explicit sex restriction; profile omitted sex")
    if requires_male:
        return Assessment("match" if sex == "男" else "mismatch", "explicit male-only requirement")
    return Assessment("match" if sex == "女" else "mismatch", "explicit female-only requirement")


def assess_household(all_text: str, profile: dict[str, Any]) -> Assessment:
    requirement = text(all_text)
    if "户籍" not in requirement and "生源" not in requirement:
        return Assessment("match", "no explicit household-registration restriction found in mapped text")
    household = text(profile.get("hukou_province", ""))
    if not household:
        return Assessment("review", "position text mentions household registration; profile omitted household province")
    if household in requirement or (household + "省") in requirement:
        return Assessment("match", f"household province '{household}' appears in requirement")
    province_words = tuple(PROVINCE_ALIASES)
    if any(province in requirement for province in province_words):
        return Assessment("mismatch", f"household province '{household}' does not match stated requirement")
    return Assessment("review", f"manual household-registration comparison needed: {requirement}")


def assess_fresh_graduate(all_text: str, profile: dict[str, Any]) -> Assessment:
    requirement = text(all_text)
    if not any(token in requirement for token in ("应届毕业生", "2027年应届", "仅限应届")):
        return Assessment("match", "no explicit fresh-graduate restriction found in mapped text")
    supplied = profile.get("is_fresh_graduate", None)
    if supplied is None:
        return Assessment("review", "position text appears to restrict to fresh graduates; profile omitted this field")
    if bool(supplied):
        return Assessment("match", "profile states fresh-graduate status")
    return Assessment("mismatch", "position text appears to restrict to fresh graduates")


def location_preference_hits(location: str, profile: dict[str, Any]) -> list[tuple[str, float]]:
    preferences = profile.get("location_preferences", {})
    if not isinstance(preferences, dict):
        return []
    location = text(location)
    matches: list[tuple[str, float]] = []
    for region, raw_weight in preferences.items():
        region = text(region)
        if not region:
            continue
        aliases = PROVINCE_ALIASES.get(region, (region,))
        if any(alias in location for alias in aliases):
            try:
                weight = float(raw_weight)
            except (TypeError, ValueError):
                weight = 0.0
            matches.append((region, weight))
    return matches


def preference_score(row: pd.Series, profile: dict[str, Any], column_map: dict[str, str], assessments: dict[str, Assessment]) -> tuple[float, list[str]]:
    weights = DEFAULT_WEIGHTS.copy()
    weights.update({key: float(value) for key, value in profile.get("weights", {}).items() if key in weights})
    location = cell(row, column_map, "location")
    department_text = " ".join((cell(row, column_map, "department"), cell(row, column_map, "agency")))
    position_text = " ".join((cell(row, column_map, "position"), cell(row, column_map, "position_intro")))
    notes: list[str] = []
    score = 0.0

    weighted_locations = location_preference_hits(location, profile)
    if weighted_locations:
        best_region, best_weight = max(weighted_locations, key=lambda item: item[1])
        score += best_weight
        notes.append(f"location: {best_region} (weight {best_weight:g})")
    else:
        location_hits = any_contains(location, profile.get("target_locations", []))
        if location_hits:
            score += weights["location"]
            notes.append(f"location: {', '.join(location_hits)}")
    department_hits = any_contains(department_text, profile.get("department_keywords", []))
    if department_hits:
        score += weights["department"]
        notes.append(f"department: {', '.join(department_hits)}")
    position_hits = any_contains(position_text, profile.get("position_keywords", []))
    if position_hits:
        score += weights["position"]
        notes.append(f"position: {', '.join(position_hits)}")
    if assessments["major"].status == "match":
        score += weights["major"]
        notes.append("major: literal/open match")
    if all(item.status == "match" for item in assessments.values()):
        score += weights["eligibility_clarity"]
        notes.append("eligibility: no mapped ambiguity")

    full_text = " ".join(text(value) for value in row.tolist())
    avoid_hits = any_contains(full_text, profile.get("avoid_keywords", []))
    if avoid_hits:
        score -= 1000.0
        notes.append(f"avoid keyword: {', '.join(avoid_hits)}")
    return score, notes


def status_label(assessments: dict[str, Assessment]) -> str:
    if any(item.status == "mismatch" for item in assessments.values()):
        return "初筛不匹配"
    if any(item.status == "review" for item in assessments.values()):
        return "需人工核验"
    return "初筛可报（仍须按官方公告核验）"


def one_row(row: pd.Series, column_map: dict[str, str], profile: dict[str, Any]) -> dict[str, Any]:
    mapped_text = " ".join(
        cell(row, column_map, field)
        for field in ("position_intro", "remarks", "position", "position_nature", "service_requirement")
    )
    assessments = {
        "education": assess_education(cell(row, column_map, "education_requirement"), profile),
        "degree": assess_degree(cell(row, column_map, "degree_requirement"), profile),
        "major": assess_major(cell(row, column_map, "major_requirement"), profile),
        "political": assess_political(cell(row, column_map, "political_requirement"), profile),
        "grassroots": assess_grassroots(cell(row, column_map, "grassroots_requirement"), profile),
        "service_project": assess_service_project(cell(row, column_map, "service_requirement"), profile),
        "fresh_graduate": assess_fresh_graduate(mapped_text, profile),
    }
    score, score_notes = preference_score(row, profile, column_map, assessments)
    full_row_text = " ".join(text(value) for value in row.tolist())
    restrictions = [token for token in SENSITIVE_RESTRICTION if token in full_row_text]
    review_messages = [item.message for item in assessments.values() if item.status == "review"]
    mismatch_messages = [item.message for item in assessments.values() if item.status == "mismatch"]
    if restrictions:
        review_messages.append("Contains a potentially sensitive restriction; manually read the official wording: " + ", ".join(restrictions))

    result = {f"raw_{column}": text(row[column]) for column in row.index}
    result.update(
        {
            "department": cell(row, column_map, "department"),
            "agency": cell(row, column_map, "agency"),
            "position_code": cell(row, column_map, "position_code"),
            "position": cell(row, column_map, "position"),
            "location": cell(row, column_map, "location"),
            "recruit_count": cell(row, column_map, "recruit_count"),
            "major_requirement": cell(row, column_map, "major_requirement"),
            "education_requirement": cell(row, column_map, "education_requirement"),
            "degree_requirement": cell(row, column_map, "degree_requirement"),
            "political_requirement": cell(row, column_map, "political_requirement"),
            "grassroots_requirement": cell(row, column_map, "grassroots_requirement"),
            "service_requirement": cell(row, column_map, "service_requirement"),
            "remarks": cell(row, column_map, "remarks"),
            "preliminary_status": status_label(assessments),
            "preference_score": round(score, 2),
            "score_rationale": " | ".join(score_notes),
            "manual_review_items": " | ".join(review_messages),
            "mismatch_reasons": " | ".join(mismatch_messages),
            "education_check": assessments["education"].status,
            "degree_check": assessments["degree"].status,
            "major_check": assessments["major"].status,
            "political_check": assessments["political"].status,
            "grassroots_check": assessments["grassroots"].status,
            "service_project_check": assessments["service_project"].status,
            "fresh_graduate_check": assessments["fresh_graduate"].status,
        }
    )
    return result


def load_profile(path: Path | None, no_profile: bool) -> dict[str, Any]:
    if no_profile:
        return {}
    if path is None:
        path = DEFAULT_PROFILE
    if not path.exists():
        raise FileNotFoundError(
            f"Profile not found: {path}\n"
            f"Copy code/civil_service_exam/profile.template.json to {DEFAULT_PROFILE.relative_to(ROOT)} "
            "and edit only your own local copy, or use --no-profile to normalize the public table first."
        )
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid profile JSON: {path}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError("Profile JSON must be an object")
    return parsed


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8-sig")


def write_report(
    path: Path,
    *,
    input_path: Path,
    sheet: str,
    header_row: int,
    column_map: dict[str, str],
    frame: pd.DataFrame,
    profile_path: Path | None,
    no_profile: bool,
) -> None:
    counts = frame["preliminary_status"].value_counts().to_dict()
    top = frame[frame["preliminary_status"] != "初筛不匹配"].head(20)
    lines = [
        "# Civil-service position preliminary screening",
        "",
        f"- Source workbook: `{input_path}`",
        f"- Sheet/header: `{sheet}` / Excel row {header_row + 1}",
        f"- Profile: {'none (public-table normalization only)' if no_profile else str(profile_path)}",
        f"- Rows read: {len(frame)}",
        "",
        "## Important boundaries",
        "",
        "- This is a transparent preliminary filter, not an official eligibility determination.",
        "- It does not estimate admission probability or use inferred demographic traits.",
        "- Major catalogues, political-status wording, graduation status, service-project rules, and remarks must be checked against the official notice before applying.",
        "- A `初筛不匹配` result only reflects literal fields matched by this script; a `需人工核验` result is not a rejection.",
        "",
        "## Detected columns",
        "",
    ]
    for field, raw_column in column_map.items():
        lines.append(f"- `{field}` ← `{raw_column}`")
    lines += ["", "## Result counts", ""]
    for label in ("初筛可报（仍须按官方公告核验）", "需人工核验", "初筛不匹配"):
        lines.append(f"- {label}: {counts.get(label, 0)}")
    lines += ["", "## Top preliminary shortlist", ""]
    if top.empty:
        lines.append("No preliminarily usable rows were found. Review the profile and detected columns.")
    else:
        lines += ["| Status | Score | Department / agency | Position | Code | Location | Notes |", "|---|---:|---|---|---|---|---|"]
        for _, item in top.iterrows():
            safe = lambda field: text(item.get(field, "")).replace("|", "/")
            lines.append(
                "| {status} | {score:.2f} | {department} {agency} | {position} | {code} | {location} | {notes} |".format(
                    status=safe("preliminary_status"),
                    score=float(item.get("preference_score", 0.0)),
                    department=safe("department"),
                    agency=safe("agency"),
                    position=safe("position"),
                    code=safe("position_code"),
                    location=safe("location"),
                    notes=safe("score_rationale") or safe("manual_review_items"),
                )
            )
    lines += [
        "",
        "## Files",
        "",
        "- `all_positions_normalized.csv`: public-table rows plus normalized fields and audit columns.",
        "- `shortlist.csv`: sorted non-mismatch rows; it is a review queue, not a final application list.",
        "- `manual_review.csv`: every row that needs human rule interpretation.",
        "- `preliminary_ineligible.csv`: literal mismatches for review; do not discard without checking the official wording.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Input .xls or .xlsx position workbook")
    parser.add_argument("--profile", type=Path, help="Local JSON preferences/eligibility profile")
    parser.add_argument("--no-profile", action="store_true", help="Normalize only; do not use personal preferences")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT, help=f"Output directory (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--sheet", help="Optional exact sheet name")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = args.input or find_default_input()
    if input_path is None:
        raise FileNotFoundError(
            f"No .xls/.xlsx file found under {SOURCE_DIR}. "
            "Wait for the local watched upload or pass --input explicitly."
        )
    input_path = input_path.expanduser().resolve()
    if not input_path.is_file():
        raise FileNotFoundError(input_path)
    profile = load_profile(args.profile, args.no_profile)
    profile_path = None if args.no_profile else (args.profile or DEFAULT_PROFILE)

    table, sheet, header_row = load_position_table(input_path, args.sheet)
    column_map = map_columns(table.columns)
    if len(column_map) < 3:
        raise ValueError(f"Only {len(column_map)} recognizable columns found: {column_map}")
    rows = [one_row(row, column_map, profile) for _, row in table.iterrows()]
    output = pd.DataFrame(rows)
    status_order = {"初筛可报（仍须按官方公告核验）": 0, "需人工核验": 1, "初筛不匹配": 2}
    output["_status_order"] = output["preliminary_status"].map(status_order).fillna(9)
    output = output.sort_values(["_status_order", "preference_score", "position_code"], ascending=[True, False, True], kind="stable").drop(columns="_status_order")

    out = args.out.expanduser().resolve()
    write_csv(output, out / "all_positions_normalized.csv")
    shortlist = output[output["preliminary_status"] != "初筛不匹配"].copy()
    review = output[output["preliminary_status"] == "需人工核验"].copy()
    mismatch = output[output["preliminary_status"] == "初筛不匹配"].copy()
    write_csv(shortlist, out / "shortlist.csv")
    write_csv(review, out / "manual_review.csv")
    write_csv(mismatch, out / "preliminary_ineligible.csv")
    write_report(
        out / "selection_report.md",
        input_path=input_path,
        sheet=sheet,
        header_row=header_row,
        column_map=column_map,
        frame=output,
        profile_path=profile_path,
        no_profile=args.no_profile,
    )
    print(f"Read {len(output)} position rows from {input_path.name} ({sheet}, header row {header_row + 1})")
    print(f"Wrote shortlist and audit files to {out}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
