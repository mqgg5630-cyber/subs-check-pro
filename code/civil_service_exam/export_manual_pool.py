#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export a redacted, all-positions manual-review pool from normalized output.

This utility is deliberately *not* an eligibility override.  It keeps rows
whose professional requirement does not textually match a private profile when
the applicant asks to inspect every regional position, while preserving the
original public requirements and separating non-major conflicts from items that
only need manual confirmation.

Example
-------
python3 code/civil_service_exam/export_manual_pool.py \
  --input results/civil_service_exam/local_analysis/all_positions_normalized.csv \
  --region 福建 \
  --out deliverables/civil_service_exam_2027/福建_全岗位人工复核池.csv

The normalized input is local-only because it may contain personal screening
signals.  This export intentionally omits profile values and free-text reasons
that could disclose them.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import pandas as pd

NON_MAJOR_CHECKS: tuple[tuple[str, str], ...] = (
    ("education_check", "学历"),
    ("degree_check", "学位"),
    ("political_check", "政治面貌"),
    ("grassroots_check", "基层工作经历"),
    ("service_project_check", "服务基层项目"),
    ("english_check", "外语"),
    ("sex_check", "性别"),
    ("household_check", "户籍/生源"),
    ("fresh_graduate_check", "应届身份"),
)

REMARK_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("专业名称/目录", "具体专业名称|专业目录|最高学历对应专业"),
    ("资格或证书", "资格证|资格考试|司法考试|适任考试|适任证书|证书编号"),
    ("体检/体能", "体检|体能测评|体能测试"),
    ("服务期", "最低服务年限|最低服务期"),
    ("专项/定向", "定向招录|服务基层项目|大学生村官|三支一扶|西部计划|特岗教师|退役士兵"),
    ("户籍/生源", "户籍|生源"),
    ("工作经历", "工作经历|从业经历"),
    ("专业能力测试", "专业能力测试|专业科目"),
)


def text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return re.sub(r"\s+", " ", str(value)).strip()


def field(row: pd.Series, *names: str) -> str:
    """Get the first populated canonical or raw-normalized CSV field."""
    for name in names:
        if name in row.index:
            value = text(row[name])
            if value:
                return value
    return ""


def remark_flags(remarks: str) -> str:
    return "；".join(label for label, pattern in REMARK_KEYWORDS if re.search(pattern, remarks))


def professional_status(status: str) -> str:
    if status == "match":
        return "专业文字直接匹配（仍须以目录/证书复核）"
    if status == "review":
        return "专业关系需按官方目录人工确认"
    return "专业文字未匹配；仅因要求查看全池而保留"


def non_major_status(mismatches: list[str], reviews: list[str]) -> tuple[str, int]:
    if mismatches:
        return "C：非专业条件有明确冲突", 2
    if reviews:
        return "B：非专业条件需人工核验", 1
    return "A：非专业条件未见机械冲突", 0


def build_pool(frame: pd.DataFrame, region: str) -> pd.DataFrame:
    required = {"location", "major_check", "major_requirement", "position_code"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Input is not a normalized position export; missing columns: {', '.join(missing)}")
    missing_checks = [column for column, _ in NON_MAJOR_CHECKS if column not in frame.columns]
    if missing_checks:
        raise ValueError(f"Input is missing screening checks: {', '.join(missing_checks)}")

    regional = frame[frame["location"].fillna("").astype(str).str.contains(region, regex=False)].copy()
    if regional.empty:
        raise ValueError(f"No normalized rows have a work location containing: {region}")

    rows: list[dict[str, Any]] = []
    for _, row in regional.iterrows():
        mismatches = [label for column, label in NON_MAJOR_CHECKS if text(row[column]) == "mismatch"]
        reviews = [label for column, label in NON_MAJOR_CHECKS if text(row[column]) == "review"]
        non_major, non_major_order = non_major_status(mismatches, reviews)
        major = text(row["major_check"])
        major_order = {"match": 0, "review": 1, "mismatch": 2}.get(major, 3)
        remarks = field(row, "remarks", "raw_备注")
        rows.append(
            {
                "人工复核分类": non_major,
                "专业文字比对": professional_status(major),
                "非专业明确冲突字段": "；".join(mismatches),
                "非专业需人工核验字段": "；".join(reviews),
                "备注提示": remark_flags(remarks),
                "来源工作表": field(row, "raw__source_sheet"),
                "Excel行号": field(row, "raw__source_excel_row"),
                "部门名称": field(row, "department", "raw_部门名称"),
                "用人司局": field(row, "agency", "raw_用人司局"),
                "招考职位": field(row, "position", "raw_招考职位"),
                "职位代码": field(row, "position_code", "raw_职位代码"),
                "招考人数": field(row, "recruit_count", "raw_招考人数"),
                "工作地点": field(row, "location", "raw_工作地点"),
                "职位属性": field(row, "raw_职位属性"),
                "机构层级": field(row, "raw_机构层级"),
                "考试类别": field(row, "raw_考试类别"),
                "专业": field(row, "major_requirement", "raw_专业"),
                "学历": field(row, "education_requirement", "raw_学历"),
                "学位": field(row, "degree_requirement", "raw_学位"),
                "政治面貌": field(row, "political_requirement", "raw_政治面貌"),
                "基层工作最低年限": field(row, "grassroots_requirement", "raw_基层工作最低年限"),
                "服务基层项目工作经历": field(row, "service_requirement", "raw_服务基层项目工作经历"),
                "职位简介": field(row, "raw_职位简介"),
                "备注（原文）": remarks,
                "_non_major_order": non_major_order,
                "_major_order": major_order,
            }
        )

    output = pd.DataFrame(rows)
    return output.sort_values(
        ["_non_major_order", "_major_order", "部门名称", "职位代码", "Excel行号"],
        kind="stable",
    ).drop(columns=["_non_major_order", "_major_order"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Local all_positions_normalized.csv from analyze_positions.py")
    parser.add_argument("--region", required=True, help="Literal work-location text to retain, for example 福建")
    parser.add_argument("--out", required=True, type=Path, help="Destination CSV path")
    parser.add_argument(
        "--exclude-non-major-mismatch",
        action="store_true",
        help="Keep only rows without a mechanical mismatch outside the professional field",
    )
    args = parser.parse_args()

    source = args.input.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    frame = pd.read_csv(source, dtype=str, keep_default_na=False)
    output = build_pool(frame, args.region)
    if args.exclude_non_major_mismatch:
        output = output[output["非专业明确冲突字段"] == ""].copy()
    destination = args.out.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(destination, index=False, encoding="utf-8-sig")
    print(f"Wrote {len(output)} {args.region} manual-review row(s) to {destination}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(2)
