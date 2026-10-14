# 12 条 AChE 对接肽｜促 Aβ 聚集 / PC12 神经毒性序列特异性加注（v2）

**定位：独立研究备忘，不属于 SCI 主文。**

本目录原有的“初版”文献包以 Aβ 聚集抑制 / 神经保护为问题背景。此次新增的 v2 不替换初版，而是依据用户粘贴的 12 条肽、对接、MD 和拟议实验，专门复核相反的假说：外源短肽是否会经 AChE（尤其 PAS）影响 Aβ 聚集与 PC12 损伤。

## 新增文件

- `Aβ促聚集_AChE-PAS_12条对接肽_序列特异性复核与湿实验计划_v2.md` — 可搜索的完整中文备忘；含逻辑校正、12 条逐条分层、模型适用性、可证伪实验和文献。
- `Aβ促聚集_AChE-PAS_12条对接肽_序列特异性复核与湿实验计划_v2.docx` — 用于转发、批注的 Word 版本。
- `12条AChE对接肽_序列特异性复核矩阵_v2.csv` — 12 条序列的结构接触、Cys/自聚集旗标、角色和判读限制；含的粗略净电荷是“游离 N 端 / C 端酰胺”假设下的近似值，非实验测量。
- `AChE_PAS_Aβ_PC12_关键文献索引_v2.csv` — 对本 v2 关键机制判断的可审计文献索引。

## 核心修正

1. PAS docking 不可直接推导为 AChE 介导的促 Aβ 聚集；它也可能竞争 / 阻断 AChE–Aβ。
2. NTxPred2 阳性不等价于 PC12 神经毒性；CANYA/PALM/AggBERT 等自身聚集工具不等价于促 Aβ。
3. 4EY6 是 galantamine 共晶；受体预处理、末端酰胺和 Cys 氧化态必须与真实合成肽一致。
4. FLLHTTR、YLSLLQR、ALLLHRC 是“PAS 主候选 1/2 + 峡内/催化区相关比较肽”的实用三肽配置；ALLLHRC 同时触及 Tyr124 和 Ser203，因而不是严格的 PAS 阴性或催化位点专一对照。
5. 只有配对的 Aβ、AChE、PAS 阻断、肽-alone 和正交聚集物/细胞控制才能区分促进、竞争、ThT 干扰和直接毒性。

## 重建

```bash
PYTHONPATH=/tmp/accio-deps python3 code/build_abeta_pas_12_peptide_addendum.py
```

脚本需要 `python-docx`。它只生成 v2 的 DOCX、参考索引和 README；不修改初版文献包。
