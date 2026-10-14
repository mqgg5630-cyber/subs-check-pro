#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Focused regression tests for civil-service position screening rules."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_positions as screen  # noqa: E402


class RequirementParsingTests(unittest.TestCase):
    def test_open_requirement_is_a_complete_cell_match(self) -> None:
        self.assertTrue(screen.is_open_requirement("无限制"))
        self.assertTrue(screen.is_open_requirement("无"))
        self.assertFalse(screen.is_open_requirement("无机化学"))
        self.assertFalse(screen.is_open_requirement("无人驾驶航空器系统工程"))

    def test_unrelated_related_major_wording_is_not_a_false_review(self) -> None:
        result = screen.assess_major(
            "法学类、中国语言文学类、英语相关专业",
            {"major_keywords": ["生物科学", "生物学"]},
        )
        self.assertEqual(result.status, "mismatch")

    def test_generic_related_major_wording_remains_manual_review(self) -> None:
        result = screen.assess_major("生物相关专业", {"major_keywords": ["生物科学"]})
        self.assertEqual(result.status, "review")

    def test_standalone_sex_wording_is_checked(self) -> None:
        female_only = "限2027届高校毕业生，女性，在本单位最低服务年限为5年"
        male_only = "限2027届高校毕业生，男性，在本单位最低服务年限为5年"
        self.assertEqual(screen.assess_sex(female_only, {"sex": "男"}).status, "mismatch")
        self.assertEqual(screen.assess_sex(male_only, {"sex": "男"}).status, "match")

    def test_party_member_only_conflicts_with_cyl_member(self) -> None:
        self.assertEqual(
            screen.assess_political("中共党员", {"political_status": "共青团员"}).status,
            "mismatch",
        )
        self.assertEqual(
            screen.assess_political("中共党员或共青团员", {"political_status": "共青团员"}).status,
            "match",
        )

    def test_2027_fresh_graduate_wording_is_checked(self) -> None:
        requirement = "限2027届高校毕业生"
        self.assertEqual(screen.assess_fresh_graduate(requirement, {"is_fresh_graduate": True}).status, "match")
        self.assertEqual(screen.assess_fresh_graduate(requirement, {"is_fresh_graduate": False}).status, "mismatch")

    def test_degree_pairing_wording_matches_supplied_degree(self) -> None:
        self.assertEqual(
            screen.assess_degree("与最高学历相对应的学位", {"degree": ["硕士"]}).status,
            "match",
        )


if __name__ == "__main__":
    unittest.main()
