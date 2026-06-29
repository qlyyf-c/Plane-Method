"""锚固计算引擎单元测试

依据 22G101-1 第 57-58 页验证计算结果
"""
import pytest
import sys
sys.path.insert(0, '.')

from app.core.anchor_calc import (
    calculate_anchor,
    get_lab_from_table,
    get_seismic_factor,
    calculate_modifiers,
)


class TestAnchorCalculation:
    """锚固计算测试类"""

    def test_get_lab_from_table(self):
        """测试查表法获取 lab 值"""
        # C30/HRB400 -> lab_d = 35 (22G101-1 p.58)
        lab_d = get_lab_from_table("C30", "HRB400")
        assert lab_d == 35

        # C25/HPB300 -> lab_d = 34
        lab_d = get_lab_from_table("C25", "HPB300")
        assert lab_d == 34

        # C60/HRB500 -> lab_d = 30
        lab_d = get_lab_from_table("C60", "HRB500")
        assert lab_d == 30

    def test_get_seismic_factor(self):
        """测试抗震系数"""
        assert get_seismic_factor("一级") == 1.15
        assert get_seismic_factor("二级") == 1.15
        assert get_seismic_factor("三级") == 1.05
        assert get_seismic_factor("四级") == 1.00
        assert get_seismic_factor("非抗震") == 1.00

    def test_calculate_modifiers_no_diameter(self):
        """测试修正系数（直径<=25mm，无自动修正）"""
        factor, names = calculate_modifiers(diameter=20, modifier_ids=None)
        assert factor == 1.0
        assert names == []

    def test_calculate_modifiers_with_diameter(self):
        """测试修正系数（直径>25mm，自动应用直径修正）"""
        factor, names = calculate_modifiers(diameter=28, modifier_ids=None)
        assert factor == 1.10
        assert "直径>25mm" in names

    def test_calculate_anchor_basic(self):
        """测试基本锚固计算 C30/HRB400/25mm/二级"""
        result = calculate_anchor(
            concrete_grade="C30",
            rebar_type="HRB400",
            diameter=25,
            seismic_grade="二级",
        )
        # lab = 35d (查表)
        assert result.lab_d == 35
        assert result.lab_mm == 875  # 35 * 25
        # la = 35d (无修正)
        assert result.la_d == 35.0
        assert result.la_mm == 875
        # laE = 35d * 1.15 = 40.25d
        assert result.laE_d == 40.25
        assert result.laE_mm == 1006  # 875 * 1.15 = 1006.25 -> 1006
        assert result.seismic_factor == 1.15

    def test_calculate_anchor_c25_hpb300(self):
        """测试 C25/HPB300/20mm/非抗震"""
        result = calculate_anchor(
            concrete_grade="C25",
            rebar_type="HPB300",
            diameter=20,
            seismic_grade="非抗震",
        )
        # lab = 34d (查表)
        assert result.lab_d == 34
        assert result.lab_mm == 680  # 34 * 20
        # la = 34d (无修正)
        assert result.la_d == 34.0
        # laE = 34d * 1.0 = 34d
        assert result.laE_mm == 680

    def test_calculate_anchor_large_diameter(self):
        """测试大直径钢筋修正（>25mm）"""
        result = calculate_anchor(
            concrete_grade="C30",
            rebar_type="HRB400",
            diameter=28,  # >25mm，应自动应用 1.10 修正
            seismic_grade="二级",
        )
        # lab = 35d
        assert result.lab_d == 35
        # la = 35d * 1.10 = 38.5d
        assert result.la_d == 38.5
        # laE = 38.5d * 1.15 = 44.275d -> 44.27 (round 到 2 位)
        assert result.laE_d == 44.27

    def test_calculate_anchor_c50_hrb500(self):
        """测试 C50/HRB500/32mm/一级抗震"""
        result = calculate_anchor(
            concrete_grade="C50",
            rebar_type="HRB500",
            diameter=32,
            seismic_grade="一级",
        )
        # lab = 32d (查表 C50/HRB500)
        assert result.lab_d == 32
        assert result.lab_mm == 1024  # 32 * 32
        # la = 32d * 1.10 (直径修正) = 35.2d
        assert result.la_d == 35.2
        # laE = 35.2d * 1.15 = 40.48d
        assert result.laE_d == 40.48

    def test_invalid_concrete_grade(self):
        """测试无效混凝土等级"""
        with pytest.raises(ValueError):
            calculate_anchor(
                concrete_grade="C99",
                rebar_type="HRB400",
                diameter=25,
                seismic_grade="二级",
            )

    def test_invalid_rebar_type(self):
        """测试无效钢筋类型"""
        with pytest.raises(ValueError):
            calculate_anchor(
                concrete_grade="C30",
                rebar_type="INVALID",
                diameter=25,
                seismic_grade="二级",
            )

    def test_reference_info(self):
        """测试引用信息"""
        result = calculate_anchor(
            concrete_grade="C30",
            rebar_type="HRB400",
            diameter=25,
            seismic_grade="二级",
        )
        assert result.reference["standard"] == "22G101-1"
        assert result.reference["page"] == 58
        assert result.reference["clause"] == "表 2.2.1"

    # ============================================================
    #   10组对照验证用例（22G101-1 第58页锚固表）
    #   验证 lab_d（查表值）、la（受拉锚固长度）、laE（抗震锚固长度）
    # ============================================================

    def test_case_01_c25_hpb300_no_seismic(self):
        """用例01: C25/HPB300/14mm/非抗震
        查表 lab=34d, 无修正, laE=34d
        """
        r = calculate_anchor("C25", "HPB300", 14, "非抗震")
        assert r.lab_d == 34
        assert r.lab_mm == 476          # 34×14
        assert r.la_d == 34.0
        assert r.la_mm == 476
        assert r.laE_d == 34.0
        assert r.laE_mm == 476

    def test_case_02_c30_hpb300_level3(self):
        """用例02: C30/HPB300/12mm/三级抗震
        查表 lab=30d, 三级 ζaE=1.05
        """
        r = calculate_anchor("C30", "HPB300", 12, "三级")
        assert r.lab_d == 30
        assert r.lab_mm == 360          # 30×12
        assert r.seismic_factor == 1.05
        assert r.laE_d == 31.5          # 30×1.05
        assert r.laE_mm == 378          # 360×1.05=378

    def test_case_03_c35_hrb400_level1(self):
        """用例03: C35/HRB400/25mm/一级抗震
        查表 lab=32d, 一级 ζaE=1.15, 四舍五入导致 laE_mm 为 919 且 int 截断
        """
        r = calculate_anchor("C35", "HRB400", 25, "一级")
        assert r.lab_d == 32
        assert r.lab_mm == 800          # 32×25
        assert r.seismic_factor == 1.15
        assert r.laE_d == 36.8          # 32×1.15
        # 800×1.15=920.0, 但 Python int(920.0)=920，此处验证实际值
        assert r.laE_mm == 920

    def test_case_04_c40_hrb400_level4(self):
        """用例04: C40/HRB400/18mm/四级抗震
        查表 lab=29d, 四级 ζaE=1.0
        """
        r = calculate_anchor("C40", "HRB400", 18, "四级")
        assert r.lab_d == 29
        assert r.lab_mm == 522          # 29×18
        assert r.seismic_factor == 1.0
        assert r.laE_d == 29.0
        assert r.laE_mm == 522

    def test_case_05_c25_hrb400_level3(self):
        """用例05: C25/HRB400/22mm/三级抗震
        查表 lab=40d, 三级 ζaE=1.05
        """
        r = calculate_anchor("C25", "HRB400", 22, "三级")
        assert r.lab_d == 40
        assert r.lab_mm == 880          # 40×22
        assert r.seismic_factor == 1.05
        assert r.laE_d == 42.0          # 40×1.05
        assert r.laE_mm == 924          # 880×1.05=924

    def test_case_06_c50_hrb400_level2(self):
        """用例06: C50/HRB400/20mm/二级抗震
        查表 lab=27d, 二级 ζaE=1.15
        """
        r = calculate_anchor("C50", "HRB400", 20, "二级")
        assert r.lab_d == 27
        assert r.lab_mm == 540          # 27×20
        assert r.seismic_factor == 1.15
        assert r.laE_d == 31.05         # 27×1.15
        assert r.laE_mm == 621          # 540×1.15=621

    def test_case_07_c25_hrb500_level1(self):
        """用例07: C25/HRB500/16mm/一级抗震
        查表 lab=48d, 一级 ζaE=1.15
        """
        r = calculate_anchor("C25", "HRB500", 16, "一级")
        assert r.lab_d == 48
        assert r.lab_mm == 768          # 48×16
        assert r.seismic_factor == 1.15
        # 768×1.15=883.2 → int截断 883
        assert r.laE_d == 55.2          # 48×1.15
        assert r.laE_mm == 883

    def test_case_08_c40_hrb500_level4(self):
        """用例08: C40/HRB500/25mm/四级抗震
        查表 lab=36d, 四级 ζaE=1.0
        """
        r = calculate_anchor("C40", "HRB500", 25, "四级")
        assert r.lab_d == 36
        assert r.lab_mm == 900          # 36×25
        assert r.seismic_factor == 1.0
        assert r.laE_d == 36.0
        assert r.laE_mm == 900

    def test_case_09_c60_hrb500_level3(self):
        """用例09: C60/HRB500/28mm/三级抗震（直径>25mm自动修正1.10）
        查表 lab=30d, 直径修正后 la=33d, 三级 ζaE=1.05
        """
        r = calculate_anchor("C60", "HRB500", 28, "三级")
        assert r.lab_d == 30
        assert r.lab_mm == 840          # 30×28
        # 直径修正 1.10
        assert r.la_d == 33.0           # 30×1.10
        assert r.la_mm == 924           # 840×1.10=924
        assert "直径>25mm" in r.modifiers_applied
        assert r.seismic_factor == 1.05
        assert r.laE_d == 34.65         # 33.0×1.05
        assert r.laE_mm == 970          # 924×1.05=970.2→970

    def test_case_10_c30_hrb400_d32_level2(self):
        """用例10: C30/HRB400/32mm/二级抗震（直径>25mm自动修正1.10）
        查表 lab=35d, 直径修正后 la=38.5d, 二级 ζaE=1.15
        """
        r = calculate_anchor("C30", "HRB400", 32, "二级")
        assert r.lab_d == 35
        assert r.lab_mm == 1120         # 35×32
        assert r.la_d == 38.5           # 35×1.10
        assert r.la_mm == 1232          # 1120×1.10=1232
        assert "直径>25mm" in r.modifiers_applied
        assert r.seismic_factor == 1.15
        assert r.laE_d == 44.27         # 38.5×1.15=44.275→44.27
        assert r.laE_mm == 1416         # 1232×1.15=1416.8→1416
