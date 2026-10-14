# 从 12 条 AChE 对接肽筛选促 Aβ 聚集 / PC12 神经毒性候选：序列特异性复核与湿实验计划（v2）

**版本**：2026-10-14（Asia/Shanghai）<br>
**定位**：基于用户提供的 12 条序列、AutoDock Vina/MD 摘要及研究目标形成的独立研究备忘；不写入 SCI 主文，不把任何计算结果写成已证实的促 Aβ 聚集或 PC12 神经毒性。<br>
**方向校正**：此前的泛用文献包讨论的是“抑制 Aβ 聚集 / 神经保护”。本文件专门处理相反问题：**外源短肽是否通过 AChE，尤其 PAS，促进 Aβ 聚集并改变 PC12 损伤**。

---

## 结论先行

### 可执行的三肽配置

| 角色 | 肽 | 结论 | 为什么 |
|---|---|---|---|
| **PAS 主候选 1** | **YLSLLQR** | **优先进入 Aβ–AChE 动力学与细胞前验证。** | 三次 Vina 平均值为全组最优（−9.44），最优分与均值差仅 0.05，包含 Tyr72 / Thr75 的峡口侧接触；无 Cys，低于多数候选的自聚集风险旗标。它仍只是“PAS 相容假说”，不是 PAS 已被占据。 |
| **PAS 主候选 2** | **FLLHTTR** | **进入，但列为“需复核 pose 稳健性”的主候选。** | 最优单次分数最高（−9.60），并接触两个经典 PAS 核心残基 Asp74、Tyr72；但最优分与三次均值（−8.77）相差 0.83，提示最佳 pose 不能单独代表稳健排序。已有单条 MD 只能生成假说，需重复。 |
| **机制比较肽** | **ALLLHRC** | **可保留为峡内 / 催化区相关的比较肽，不应称作严格阴性或“纯催化位点”对照。** | 平均分高（−9.18），报告 pose 同时触及 Ser203 与核心 PAS Tyr124，故更准确是“混合峡内几何”的比较；它可问“不同 AChE 沟槽几何是否也有表型”，但不能隔离 PAS。Cys、最高 GRAVY（1.14）和较高 a3v（0.39）还会增加自身聚集/氧化二聚体的混杂。 |

**若只做两条**：YLSLLQR + FLLHTTR；机制控制由 **Aβ±AChE 无肽**、**AChE–Aβ + PAS 阻断剂** 和（条件允许时）**BChE–Aβ**承担。若保留 ALLLHRC，结果应解释为“不同沟槽几何的比较”，而不是 PAS 阴性或催化位点专一对照。

**若第三条的目标是提高“PAS hit”命中率，而不是机制比较**：可将 ALLLHRC 换为 **LLHPLRL**。其与 Trp286、Tyr341 两个经典 PAS 核心残基接触更直接，但 GRAVY 0.84 / a3v 0.45 提示更高自聚集与 ThT 混杂风险。不能把它与 ALLLHRC 放进同一层级比较后称为“PAS 特异性”。

### 最重要的机制修正

“短肽占据 PAS”**不等于**“短肽会通过 PAS 促进 Aβ 聚集”。已有经典工作显示 AChE 的 PAS 参与 Aβ 促聚集，且 PAS 配体 propidium 可削弱 AChE 带来的促聚集效应，而催化位点抑制剂 edrophonium 没有同样作用。这意味着一个 PAS 结合肽至少有两种相反的可检验结果：

1. **竞争 / 阻断** AChE–Aβ 相互作用，使 `AChE + Aβ + 肽 < AChE + Aβ`；
2. **正向协同**（桥接、稳定三元复合物或改变 PAS 表面），使 `AChE + Aβ + 肽 > AChE + Aβ`。

因此，在看到三元体系的动力学和机制控制以前，只能称为 **“AChE–PAS 相关促聚集假说”**，不能把 PAS docking 本身解释为促聚集证据。Inestrosa 等的原始数据支持 AChE–Aβ 促纤维化与 PAS 参与，但并不自动预测任意外源 PAS 肽的作用方向。[Inestrosa et al., 1996](https://doi.org/10.1016/S0896-6273(00)80108-7)

---

## 1. 已给数据的审查边界

### 1.1 可以使用的证据

- 12 条肽均为 7–9 aa、目录支持、NTxPred2 阳性；
- 人源 AChE 的 PDB **4EY6** 是合理的受体起点：它是重组人 AChE 与 (−)-galantamine 的复合物；
- 表中 Vina 分、三次均值、接触残基、GRAVY、a3v，以及三条肽的单次最佳 pose MD 摘要，可以作为**同一工作流内的候选排序资料**；
- AChE–Aβ 的 PAS 假说有实验证据：人 AChE 的典型 PAS 核心包括 Tyr72、Asp74、Tyr124、Trp286、Tyr341；AChE 可促 Aβ 成纤，而 propidium 影响这一增强效应。[4EY6](https://www.rcsb.org/structure/4EY6)；[PAS 残基综述](https://pmc.ncbi.nlm.nih.gov/articles/PMC12447245/)

### 1.2 不能从现有数据直接推出的结论

- Vina kcal/mol 不是 Kd，也不适合跨不同长度/柔性短肽作为绝对亲和力；
- 三次本地 Vina 运行是随机种子 / 搜索重复，不是蛋白构象、溶剂、电荷、肽末端状态或真实结合模式的独立验证；
- 只有“最佳 pose 的单条 MD”时，不能写“该肽稳定占据 PAS”或“氢键网络被证明维持”；
- NTxPred2 阳性是**一般序列神经毒性分类**，不是 PC12 存活率、LDH、突起长度或 Aβ 协同毒性的预测；
- a3v / CANYA / PALM / AggBERT 的自身聚集预测不能替代 `Aβ ± 肽` 的 ThT 动力学，更不能证明“促进 Aβ 聚集”。

### 1.3 4EY6 预处理必须被写清

4EY6 为 galantamine 复合物。对接 / MD 记录中应明确：

- galantamine、结晶缓冲组分、非必要水和糖基是否移除 / 如何处理；
- 受体链、质子化状态、网格位置和大小、肽的柔性键设置；
- **计划湿实验的真实化学实体**（游离 N 端、C 端酰胺、Cys 游离 / 氧化态）是否与 docked ligand 一致；
- 是否比较另一个 apo / 不同构象的人 AChE 起点，至少说明为什么没有比较。

若 wet peptide 使用 **C 端酰胺化**，而 docking 使用自由羧基末端，肽的净电荷、H-bond donor/acceptor 和 PAS 静电互补都会改变；该差异必须在复核版 docking/MD 中修正，而不是在方法段略过。

---

## 2. 12 条肽的序列特异性分层

### 2.1 PAS 判定标准

为避免把“峡内某个接触”都称为 PAS，本备忘将人 AChE 的 **核心 PAS**限定为：**Tyr72、Asp74、Tyr124、Trp286、Tyr341**。Thr75/Ser125 可记作邻近峡口，Ser203/His447/Glu334 为催化三联体相关，Trp86 为催化阴离子位点，不应混入 PAS 核心计数。

| 肽 | aa | Vina 最优 / 三次均值 | 原表关键接触 | 核心 PAS 证据 | 序列风险旗标 | 建议角色 |
|---|---:|---|---|---|---|---|
| **FLLHTTR** | 7 | −9.60 / −8.77 | Asp74, Tyr72, His287 | **2 个核心 PAS**：D74、Y72 | His 质子化、最佳/均值差大；无 Cys | **PAS 主候选 2**；先做 pose/MD 重复 |
| **YLSLLQR** | 7 | −9.49 / −9.44 | Tyr72, Thr75, Glu202 | **1 个核心 PAS**：Y72；T75 邻近 | 无 Cys；GRAVY 0.04；稳定排序最强 | **PAS 主候选 1** |
| **ALLLHRC** | 7 | −9.29 / −9.18 | Ser125, Ser203, Tyr124 | **Y124 为 1 个核心 PAS**，同时有 Ser203 峡底接触；是混合几何 | **Cys**、GRAVY 1.14、a3v 0.39 | **峡内 / 催化区相关比较肽**，非严格阴性或纯催化对照 |
| FCLHLQLR | 8 | −9.27 / −8.96 | Ser203, Thr75, Tyr341 | **Y341** + T75，但与 Ser203 混合 | **Cys**、a3v 0.41 | 备选；不优先于无 Cys 主候选 |
| YHHLLCRR | 8 | −9.03 / −8.62 | Trp86, Ser203 | 无核心 PAS | **Cys**、双 His、低 GRAVY | 若需低自聚集非 PAS 比较可考虑；与 PAS 肽理化不匹配 |
| LLHLPKRTT | 9 | −9.01 / −8.89 | Ser203, Val340 | 无核心 PAS | 多碱性 / His；a3v 0.06 | 非 PAS 比较备选 |
| **LLHPLRL** | 7 | −8.94 / −8.91 | Trp286, Tyr341, His447 | **2 个核心 PAS**：W286、Y341 | GRAVY 0.84、a3v 0.45，高自身聚集风险 | **PAS hit-rate 备选**；需强自聚集对照 |
| WLLVHLKK | 8 | −8.94 / −8.64 | Asn283, Gln279 | 无核心 PAS | a3v 0.49 最高、疏水/碱性 | 低优先级；强混杂风险 |
| LLHPLRC | 7 | −8.91 / −8.78 | Ser125, Ser293 | 无核心 PAS | **Cys**、GRAVY 0.66 | 低优先级 |
| HLLTLKKHV | 9 | −8.88 / −8.69 | Tyr72, Phe346 | **Y72** 单一核心 PAS | 多 Lys / His，a3v 0.19 | PAS 备选；证据弱于前二 |
| HLPLLHRCC | 9 | −8.35 / −8.28 | Ser125, Tyr124, Tyr337 | **Y124** 单一核心 PAS | **双 Cys**，氧化/二聚体风险最高 | 不建议首轮 |
| HVLLLRQCA | 9 | −8.25 / −8.07 | Thr75 | 无核心 PAS（T75 邻近） | **Cys**、GRAVY 0.97 | 不建议首轮 |

### 2.2 关于 Cys、末端和净电荷的特别提醒

6/12 条候选肽含 Cys；其中 HLPLLHRCC 有两个 Cys。游离 Cys 在空气、金属痕量、温度、搅拌和培养基环境中可能氧化 / 形成二硫键。这样会改变实际分子量、有效浓度、肽–肽聚集、ThT 信号和 AChE 结合。**“TFA 换成醋酸盐 + HPLC ≥95%”仍不足以保证工作液中的单体状态。**

首轮执行前，至少应以 LC–MS 或等效的游离巯基/二硫键检查确认每批工作液的状态；对 Cys 候选需要把“还原单体”与“自然氧化混合物”区分，不能在结果中合并。该问题尤其影响把 ALLLHRC 当机制对照的解释。

若按“游离 N 端 + C 端酰胺”估计，含 Lys/Arg 的候选在 pH 7.4 应为明显正电；His 只部分质子化，Cys 也可能部分去质子化。绝对净电荷受端基 pKa、微环境和实际盐型影响，故应记录为**制剂假设**而非一个固定事实。所有 docking / MD 与湿实验均应使用相同的端基定义。

---

## 3. 对接与 MD 的最低复核门槛

### 3.1 为什么优先 YLSLLQR 而不是只看 FLLHTTR 的 −9.60

- YLSLLQR 的最优单次 −9.49 与三次均值 −9.44 接近，说明在当前 Vina 工作流中的重复稳定性更好；
- FLLHTTR 虽有更高的最优分和两个 PAS 核心接触，但 −9.60 与 −8.77 的差距提示“顶级 pose”可能是偶然搜索到的构象；
- 这不淘汰 FLLHTTR，而是把它的优先级定义为“**必须先确认 pose cluster 与重复 MD**”，而不是“分数第一所以机制最强”。

### 3.2 湿实验前建议补的最小计算复核

对 **YLSLLQR / FLLHTTR / ALLLHRC**（或 LLHPLRL）进行：

1. 报告每条肽前若干 pose 的空间 cluster、cluster population 和核心 PAS 接触，不只报第一名；
2. 对每条主候选从至少两个合理的 pose cluster 出发，进行独立随机初速度的 MD 重复；
3. 报告核心 PAS 接触占有率、肽–AChE 距离 / SASA、肽本身团簇或二级结构变化、关键 H-bond 的 occupancy，而不是单帧图；
4. 对游离 N 端 / C 端酰胺的版本保持一致；对 Cys 候选至少说明采用了何种氧化态；
5. 将结论限定为“与 PAS / 催化区结合相容的结构假说”。除非有竞争实验或直接结合数据，不使用“占据 PAS”这一确定性措辞。

AChE 的 PAS 具有柔性；人 AChE PAS 的关键残基为 Tyr72、Asp74、Tyr124、Trp286、Tyr341。因而用单一刚性 4EY6 构象给 7–9 aa 肽排名尤其需要慎重；应以 pose cluster、重复 MD 和竞争实验来检验该结构假说，而不是把刚性 docking 当作位点确证。[PAS 残基综述](https://pmc.ncbi.nlm.nih.gov/articles/PMC12447245/)

---

## 4. 预测模型：可以做什么，不能做什么

| 工具 / 文献 | 实际训练任务 | 对本 12 条肽的合理用途 | 关键外推限制 | 本项目结论 |
|---|---|---|---|---|
| **NTxPred2**，Rathore et al. 2025，DOI [10.1002/pro.70200](https://doi.org/10.1002/pro.70200) | 一般“neurotoxic peptide / non-toxic peptide”分类；877+877 肽集；其 peptide ESM2-t30 独立集 AUC 0.984。 | 作为目录支持 / 一般神经毒性风险旗标。 | 不是 PC12、不是 Aβ 共暴露、不是剂量/时间回归；当前 12 条全阳性，无排序增益；训练数据和短肽组成特征可放大 Cys/Leu 偏差。 | **保留为已有标签，不再用于筛掉候选。** |
| **CANYA**，Thompson et al. 2025，DOI [10.1126/sciadv.adt5111](https://doi.org/10.1126/sciadv.adt5111) | >10 万条随机 **20 aa** 序列，以 Sup35N 融合体系测核化/聚集并训练。 | 若软件允许，可探索“候选自身聚集”的敏感性分析。 | 7–9 aa 裸肽与 20 aa Sup35N 融合序列不在相同实验域；不预测 Aβ40/42 加速。论文也强调旧预测器在更宽序列空间的外推有限。 | **不应写成 7–9 aa 的可靠定量促 Aβ 分数。** |
| **PALM**，Eschbach et al. 2026，DOI [10.1021/acs.jcim.6c00577](https://doi.org/10.1021/acs.jcim.6c00577) | ESM2 embedding 的自身聚集 / APR 预测。 | 检查候选肽自身聚集倾向和局部 APR。 | 不是 Aβ 抑制/促聚集模型；基础模型曾难以预测 Aβ 单突变致聚效应，重训更大数据后才改善。 | **可作负向风险旗标，不作入选依据。** |
| **AggBERT / PATH / AmyloGram** | 主要是 hexapeptide 或短窗口 amyloidogenicity。 | 对 7–9 aa 做滑动 6-mer 的自身聚集敏感性检查。 | 滑窗高分不代表整条肽会促 Aβ，也可能只是自身成纤。 | **只做注释。** |
| **Amylo-IC50Pred**，Bansal et al. 2025，DOI [10.1021/acschemneuro.5c00649](https://doi.org/10.1021/acschemneuro.5c00649) | 584 个小分子 Aβ aggregation inhibitor/decoy 与 IC50 任务。 | 无。 | 小分子描述符、抑制方向、训练标签均不适用于 7–9 aa 促聚集肽。 | **不使用。** |
| **ToxinPred / ToxinPred2** | 一般毒性 / 蛋白毒性。 | 附加的非特异性毒性旗标。 | 不是神经元/PC12，也不描述 Aβ 协同。 | 不增加候选优先级。 |

**模型审查结论**：用户原先的结论成立——目前没有一个公开的序列模型能够直接区分：

- 肽单独使 Aβ 成纤 / 共聚集；
- 仅在 AChE 存在下加速 Aβ；
- 占据 PAS 后反而阻断 AChE–Aβ；
- 增强 PC12 损伤而非仅影响自身毒性。

这些是**实验机制标签**，不是可由现成单序列分类器替代的标签。

---

## 5. 将“促聚集”和“神经毒性”拆为可证伪实验

### 5.1 必须预先区分的四个假说

| 假说 | 动力学预期 | 细胞解释 | 需要的关键控制 |
|---|---|---|---|
| H1：肽自身聚集 / 干扰 ThT | 肽-alone 也改变 ThT、浊度或形貌 | 肽-alone 可能有直接细胞作用 | 肽-alone + ThT、肽-alone + PC12、形貌/LC–MS |
| H2：AChE 非依赖共聚集 / 种子 | `Aβ + 肽` 已相对 Aβ 改变 lag/rate | 只有预形成混合物增加损伤才可联系 Aβ 物种 | Aβ+肽，无 AChE；正交聚集物表征 |
| H3：AChE–PAS 正向协同 | `AChE+Aβ+肽 > AChE+Aβ`，且 PAS 阻断减弱这一差异 | 三元形成物而非肽单独可加重 PC12 损伤 | propidium / 其他合适 PAS 控制，AChE 无肽，BChE 比较（如可行） |
| H4：PAS 竞争 / 抑制 | `AChE+Aβ+肽 < AChE+Aβ` | 肽可能是 AChE 相关 anti-aggregation hit，而非促毒肽 | 同上；不可因 docking PAS 而硬解释为失败 |

### 5.2 实验 A：Aβ 聚集动力学（必须）

**核心目标不是仅问“终点 ThT 高不高”，而是区分 H1–H4。**

建议将 Aβ40 与 Aβ42 的目的分开：

- 若目的是**复现 AChE–PAS 促纤维文献**，Aβ1–40 与 AChE 动力学更容易同经典 Inestrosa 框架对应；
- 若目的是**与 PC12 毒性连接**，应另用定义明确的 Aβ1–42 寡聚体 / 预纤维状态，而不是把成熟 ThT 高纤维直接等同于“最毒”。Aβ1–42 可溶寡聚体通常比成熟纤维更常被视为高毒性物种，且 PC12 对聚集状态敏感。[Aβ42/PC12 例证](https://doi.org/10.1007/s10930-023-10138-0)

**最低组别框架**：

- Aβ-alone；
- Aβ + 每条肽；
- AChE + Aβ；
- AChE + Aβ + 每条肽；
- 肽-alone；
- vehicle；
- AChE + 肽（不含 Aβ）；
- AChE + Aβ + PAS 阻断控制（机制控制）；
- 可行时：BChE + Aβ ± 肽，作为 cholinesterase/PAS 架构差异控制。

**首轮必要读出**：lag time、表观增长速率、终点信号、肽-alone 的空白信号、以及至少一种正交聚集物读出（TEM/AFM、SEC/DLS、CD/FTIR 或适合的寡聚体读出）。ThT 的变化必须与“候选肽是否直接发光 / 淬灭 / 吸附染料”区分。

经典 AChE–Aβ 工作显示 propidium 会影响 AChE 介导的促聚集，而 edrophonium 的催化位点抑制不产生同样结果；这使 PAS 阻断对照比“只做 Ellman”更直接地检验你的机制问题。[原始结果](https://www.sciencedirect.com/science/article/pii/S0896627300801087)

### 5.3 实验 B：PC12 神经毒性（必须，但应在聚集物状态定义后做）

**不要用“ThT 更高 → PC12 必更毒”作为前提。**成熟纤维与寡聚体可产生不同的细胞表型；许多体系中寡聚体更强，但并非所有制备、浓度和细胞状态都相同。

建议采用以下判读逻辑：

1. **肽-alone 剂量–时间矩阵**：这是 NTxPred2 阳性的真正实验校验；若肽本身有直接毒性，则不能把 Aβ+肽导致的下降全归因于 Aβ；
2. **预先定义 Aβ 物种**：以经过物理化学表征的 Aβ 寡聚体/预纤维或纤维作为细胞输入；不要仅靠“培养了 x 小时”命名状态；
3. **在细胞外预孵育后再上细胞**：将“形成的 Aβ–肽 / Aβ–AChE–肽物种”与“肽实时直接作用 PC12”尽量拆开；同步保留同加组作为辅助，而不能作为唯一组；
4. **最低细胞终点**：CCK-8 或 MTT + LDH；若使用 NGF 分化 PC12，再加入突起长度 / 形态。MTT/CCK-8 主要反映代谢/氧化还原，不能独立证明死亡；
5. **AChE 控制**：AChE-alone、AChE+肽、AChE+Aβ、AChE+Aβ+肽；只有前述 A 实验出现 AChE 依赖模式时，才将三元体系放到 PC12 的主验证层。

### 5.4 实验 C：AChE 酶活（建议，但其回答有限）

Ellman 法可以回答“肽是否改变 AChE 的水解功能”；它**不能单独证明 PAS 占据**。可能结果的正确表述：

- 肽抑制酶活：说明它影响催化功能或产生变构影响，但不等于定位 PAS；
- 肽不抑制酶活：也不排除 PAS 结合，因为 PAS–Aβ 促聚集可独立于催化活性；
- 若要主张 PAS 竞争，需要把酶活和 PAS 阻断 / Aβ 动力学竞争模式连起来，或者以后增加直接结合 / 竞争实验证据。

### 5.5 可直接执行的首轮最小矩阵（在用户原草案上加固）

以下是为节约样品又避免“只测一个终点”的最小可证伪设计；数值沿用原草案的级别，但任何最终浓度都应根据 Aβ 制备、酶批次与光学线性预实验锁定后预注册。

**A. 聚集动力学首轮（每条肽独立运行）**

- 固定一套 Aβ 批次和制备 SOP；若把 AChE–PAS 作为主要机制问题，优先以 **Aβ1–40** 建基准；若以 PC12 毒性为主要终点，则把 **Aβ1–42** 的定义寡聚体实验另立，不把两者混成一个“总 Aβ”结果；
- 可从原草案的 `Aβ 10 μM`、肽:Aβ `0.25:1 / 1:1 / 4:1` 开始，但必须先确认肽-alone 在该范围不产生不可解释的荧光、浊度或沉淀；
- hAChE 以**摩尔浓度/活性位点浓度**而不是只报 U/mL 记录；湿实验酶种尽量使用与 docking 一致的人 AChE。若改用电鳗 AChE，必须把物种差异写成新的外推限制；
- 每板至少包括 `Aβ`、`肽`、`Aβ+肽`、`AChE+Aβ`、`AChE+Aβ+肽`、vehicle、`AChE+肽`；PAS 阻断条件须同时配有“阻断剂+ThT、无 Aβ”的光学控制；
- 预先导出 lag time、最大斜率与终点，而不是只挑某一个时间点；不同 Aβ 制备日应作为独立生物学重复，而不是一板内技术重复的替代。

**B. PC12 首轮**

- 先按原草案做肽-alone `0.5 / 5 / 20 / 100 μM`，`24 / 48 h` 的剂量–时间矩阵，并记录目视沉淀；对于 Cys 肽需同时记录制剂/氧化状态；
- 选定一种 PC12 状态后保持到底：若要讨论神经元样形态，使用 NGF 分化 PC12 并加入突起长度；若先做未分化筛选，则不要把其单一 CCK-8 结果命名为“神经元毒性”；
- 首批混合物以细胞外预孵育、已定义状态的 Aβ / Aβ–肽 / AChE–Aβ / AChE–Aβ–肽为主，并保留“同加细胞”的辅助组以识别肽直接效应；
- 对每个可能的促毒结论，至少要求 `CCK-8 或 MTT` 与 `LDH` 同向，且肽-alone 不能解释全部效应。对 NGF-PC12 可增加突起形态作为第三读出。

**C. 用 PAS 控制决定下一步，而不是用 docking 决定**

若 `AChE+Aβ+肽` 的效应高于 `AChE+Aβ`，下一步是检测该差异是否被合适 PAS 阻断设计削弱；若低于，优先检验 PAS 竞争/阻断假说。两种结果都对机制有信息量。**“没有促聚集”不是失败；它可能是对接所提示的 PAS 竞争发挥作用。**

---

## 6. 推荐的 Go / No-go 决策门

| 门 | 通过条件 | 不通过时的正确处理 |
|---|---|---|
| G0：制剂 | 肽身份、端基、盐型、Cys 氧化态确认；Aβ 状态定义 | 不进入任何机制结论；先解决化学实体问题 |
| G1：ThT 可解释性 | 肽-alone / 染料干扰被量化；Aβ kinetics 可重复 | 不能称促聚集，只报告信号干扰或自身聚集 |
| G2：聚集物身份 | 至少一个正交读出支持动力学结果 | 暂不进入 PC12 的机制验证层 |
| G3：PAS 依赖性 | 相对 AChE+Aβ 的差异被 PAS 阻断 / 适当酶对照支持 | 降级为 AChE 相关或 AChE 非依赖现象 |
| G4：PC12 特异性 | 肽-alone、Aβ-alone、预孵育复合物与三元体系被拆开；至少两个细胞读出同向 | 不称“增强 Aβ 神经毒性”；只报告代谢读出变化 |

---

## 7. 写作与命名建议

### 可使用的措辞

- “与人 AChE PAS 接触的 docking pose 相容”；
- “在当前 Vina 设置中，YLSLLQR 显示更一致的重复排序”；
- “FLLHTTR 对核心 PAS 残基的接触值得实验检验”；
- “ALLLHRC 被设为催化区结合的机制比较肽”；
- “NTxPred2 阳性提供一般神经毒性序列先验，但不替代 PC12 实验”。

### 不应使用的措辞

- “三条肽已通过 PAS 促进 Aβ 聚集”；
- “Vina −9.x 证明高亲和力 / Kd”；
- “NTxPred2 阳性证明 PC12 神经毒性”；
- “a3v / CANYA / PALM 高分预测促进 Aβ”；
- “ALLLHRC 是 PAS 阴性对照”（它是不同位点、不同疏水性和含 Cys 的比较肽）。

---

## 8. 关键参考文献

1. Inestrosa NC, Alvarez A, Pérez CA, et al. **Acetylcholinesterase Accelerates Assembly of Amyloid-β-Peptides into Alzheimer's Fibrils: Possible Role of the Peripheral Site of the Enzyme.** *Neuron* 1996;16:881–891. DOI: [10.1016/S0896-6273(00)80108-7](https://doi.org/10.1016/S0896-6273(00)80108-7).
2. De Ferrari GV, Canales MA, Shin I, et al. **A structural motif of acetylcholinesterase that promotes amyloid beta-peptide fibril formation.** *Biochemistry* 2001;40:10447–10457. DOI: [10.1021/bi0101392](https://doi.org/10.1021/bi0101392). PMID: 11523986.
3. Alvarez A, Alarcón R, Opazo C, et al. **Stable Complexes Involving Acetylcholinesterase and Amyloid-β Peptide Change the Biochemical Properties of the Enzyme and Increase the Neurotoxicity of Alzheimer's Fibrils.** *J Neurosci* 1998;18:3213–3223.
4. Muñoz FJ, Inestrosa NC. **Neurotoxicity of acetylcholinesterase amyloid β-peptide aggregates is dependent on the type of Aβ peptide and the AChE concentration present in the complexes.** *FEBS Lett* 1999. DOI: [10.1016/S0014-5793(99)00468-8](https://doi.org/10.1016/S0014-5793(99)00468-8).
5. Inestrosa NC. **Amyloid–cholinesterase interactions.** *FEBS J* 2008. DOI: [10.1111/j.1742-4658.2007.06238.x](https://doi.org/10.1111/j.1742-4658.2007.06238.x).
6. Rathore AS, Jain S, Choudhury S, Raghava GPS. **A large language model for predicting neurotoxic peptides and neurotoxins.** *Protein Science* 2025;34:e70200. DOI: [10.1002/pro.70200](https://doi.org/10.1002/pro.70200).
7. Thompson M, Martín M, Olmo TS, et al. **Massive experimental quantification allows interpretable deep learning of protein aggregation.** *Sci Adv* 2025;11:eadt5111. DOI: [10.1126/sciadv.adt5111](https://doi.org/10.1126/sciadv.adt5111).
8. Eschbach E, Deibler K, Korani D, Swanson S. **Predicting Peptide Aggregation with Protein Language Model Embeddings.** *J Chem Inf Model* 2026;66:5206–5216. DOI: [10.1021/acs.jcim.6c00577](https://doi.org/10.1021/acs.jcim.6c00577).
9. Perez R, Li X, Giannakoulias S, Petersson EJ. **AggBERT: Best in Class Prediction of Hexapeptide Amyloidogenesis with a Semi-Supervised ProtBERT Model.** *J Chem Inf Model* 2023;63:5727–5733. DOI: [10.1021/acs.jcim.3c00817](https://doi.org/10.1021/acs.jcim.3c00817).
10. Bansal A, et al. **Machine Learning–Based Bioactivity Prediction and Descriptor-Guided Rational Design of Amyloid-β Aggregation Inhibitors.** *ACS Chem Neurosci* 2025;16:4351–4363. DOI: [10.1021/acschemneuro.5c00649](https://doi.org/10.1021/acschemneuro.5c00649).
11. Walsh I, Seno F, Tosatto SCE, Trovato A. **PASTA 2.0: an improved server for protein aggregation prediction.** *Nucleic Acids Res* 2014;42:W301–W307. DOI: [10.1093/nar/gku399](https://doi.org/10.1093/nar/gku399).
12. Shearman MS, Ragan CI, Iversen LL. **Inhibition of PC12 cell redox activity is a specific, early indicator of the mechanism of beta-amyloid-mediated cell death.** *PNAS* 1994;91:1470–1474. DOI: [10.1073/pnas.91.4.1470](https://doi.org/10.1073/pnas.91.4.1470).

---

## 一句话版本

**建议先做 YLSLLQR、FLLHTTR 与 ALLLHRC（比较肽），但把核心命题改成可证伪的“PAS 相关协同 / 竞争”而不是预设促聚集。以 AChE+Aβ 无肽、PAS 阻断控制、肽-alone 控制和定义明确的 Aβ 物种，才能把对接、ThT 与 PC12 数据串成可信的机制证据链。**
