# 从 12 条 AChE 对接肽筛选促 Aβ 聚集 / PC12 神经毒性候选：机制与深度学习补充（v2.1）

**版本**：2026-10-17（Asia/Shanghai）

**定位**：按既有 v2 的“序列特异性复核 → 计算/模型适用性 → 可证伪湿实验 → Go/No-go”格式重做的独立补充包。它不覆盖 `Aβ促聚集_AChE-PAS_12条对接肽_序列特异性复核与湿实验计划_v2`，也不把计算分数、文献中的别的肽或通用毒性模型写成当前 12 条肽已经促 Aβ 聚集或损伤 PC12 的证明。
**检索重点与截止**：定向补充 2023–2026 年 Aβ 交叉成核/病理性促聚集、AChE–PAS、Aβ 变体深度学习、短肽 amyloidogenicity 与神经毒性模型；并保留最直接的机制奠基实验证据。检索截止为 2026-10-17，不等同于预注册系统综述。

---

## 结论先行

### 可执行的机制结论

1. **“外源肽促进 Aβ 聚集”存在可验证的病理机制，不是没有先例。**最直接的已验证类别包括：
   - **AChE 来源促聚集基序**：AChE 附近 PAS 的疏水 35 aa 肽能模拟完整 AChE、被纳入生长中的 Aβ 纤维并加速成纤；AChE N 端的 **AChE7–20** β-hairpin 肽也可触发 Aβ 聚集/沉积。[De Ferrari 2001](https://doi.org/10.1021/bi0101392)；[Hou 2014](https://doi.org/10.1111/cns.12161)
   - **Aβ 相关短变体的同源交叉成核**：2025 年 p3（Aβ17–40/42）研究显示其可快速成纤，并在 C 端长度匹配时显著交叉成核全长 Aβ；2023 年研究显示 pyroE3/ΔE3-Aβ40 种子可加速 wt-Aβ40 的细胞内外聚集并在特定神经细胞体系中伴随更快的毒性升高。[Tian 2025](https://doi.org/10.1038/s41467-025-57341-4)；[Cruceta et al. 2023](https://doi.org/10.1016/j.jbc.2023.105196)
   - **异源交叉成核/共聚集**：hIAPP、AMP 或其他 amyloidogenic 肽可改变 Aβ 动力学、聚集物结构和细胞毒性，但方向高度依赖序列、种子状态、末端、缓冲液与比例；不能把“自身易聚集”自动翻译成“促 Aβ”。[综述](https://doi.org/10.1039/D3CS00878A)；[hIAPP–Aβ 计算研究](https://doi.org/10.1021/acsomega.4c00500)
2. **当前 12 条 7–9 aa AChE docking 肽仍只是待检验的假说。**它们与上述 AChE 长肽或 Aβ 变体不同。PAS docking 可能产生两种相反效应：正向桥接/模板化，或竞争性占据 PAS 从而抑制 AChE–Aβ 作用。只有三元体系 `AChE + Aβ + 肽` 对照 `AChE + Aβ`，再加 PAS 阻断/竞争控制，才能判定方向。
3. **最接近“省事”的 Aβ 深度学习工具是“自身 amyloidogenicity / APR”模型，而非“促 Aβ”模型。**PALM、CANYA、AggBERT、AggNet/AggreProt 等可标注候选肽自身的 β-聚集风险或局部 APR；Wang 等的深度学习模型可预测**Aβ42 单点变体**的成核表型。它们均不能直接预测“外源 7–9 aa 肽会不会加速 Aβ40/42”或“会不会经 AChE–PAS 促聚集”。
4. **没有检到可直接替代 PC12 实验的公开深度学习模型。**NTxPred2、ToxinPred3、BiToxNet、NToxSEM、PeptiTox 等预测的是一般肽毒性或一般神经毒性，不以 `Aβ + 候选肽 + PC12` 的 CCK-8/LDH/ROS/凋亡标签训练。它们可用作肽-alone 风险排序，不能预测 PC12 中 Aβ 协同损伤。ToxMSRC 虽有公开代码/预训练模型，但其报告的适用长度为 11–50 aa，因此对当前 7–9 aa 12 肽属于域外，不能靠补零或延长序列强行使用。
5. **首轮最实用的计算—实验组合**：
   - 对当前 12 条：`PALM/AggBERT（自身成纤旗标） + NTxPred2 + ToxinPred3（肽-alone 神经毒性/一般毒性旗标） + PAS pose/MD 重复（结构假说）`；
   - 对 Aβ 病理促聚集命题：采用 `AChE + Aβ`、`AChE + Aβ + 肽`、PAS 阻断、肽-alone、Aβ+肽、正交形貌/组分与 PC12 双终点；
   - 把 p3 或 pyroE3/ΔE3-Aβ 作为**文献型阳性机制对照概念**，而不是把它们与当前短肽混作同类 lead。

### 最重要的机制修正

**“ThT 更高 / β-sheet 更多 / 纤维更多”不等于“PC12 更毒”。**Aβ 的可溶寡聚体、原纤维、成熟纤维和非特异沉淀可以有不同毒性。已有 Aβ25–35/PC12 与 Aβ 寡聚体研究都提示，聚集状态、膜结合、制备时间和缓冲体系可改变细胞终点。因此，本项目需同时回答：

- 肽是否改变 Aβ 装配动力学？
- 改变的是否是 AChE–PAS 依赖的过程？
- 形成的是何种 Aβ 物种？
- 这些物种是否在排除肽-alone 直接毒性后，真正增加 PC12 损伤？

---

## 1. 已给数据与新增检索的审查边界

### 1.1 可以使用的证据

- 12 条肽为 7–9 aa；已有同一流程内的 Vina 重复分数、接触残基、GRAVY、a3v 和部分 MD 摘要；
- 4EY6 是人源重组 AChE–(−)-galantamine 复合物，可作为 PAS/峡内对接起点，但不是 apo AChE，也不是 Aβ–AChE 三元复合物；
- AChE–Aβ 促聚集的经典证据：AChE 可缩短 Aβ 成纤的 lag phase；PAS 配体 propidium 可影响该效应，而催化位点抑制剂 edrophonium 不呈相同模式。[Inestrosa et al. 1996](https://doi.org/10.1016/S0896-6273(00)80108-7)
- 新近的病理性交叉成核证据：p3–Aβ 的 C 端长度匹配交叉成核；pyroE3/ΔE3-Aβ–wt-Aβ 的细胞环境加速聚集/毒性相关结果。

### 1.2 不能从现有数据直接推出的结论

- 不能因某条候选肽结合 Tyr72/Asp74/Trp286/Tyr341，就说它已经“通过 PAS 促聚集”；
- 不能因 PALM、CANYA、AggBERT 或 AggNet 给出高自身聚集风险，就说它会加速另一条 Aβ 肽；
- 不能因 NTxPred2、BiToxNet 或 NToxSEM 标为神经毒性，就说它会降低 PC12 CCK-8、升高 LDH，或会与 Aβ 协同；
- 不能因 Aβ25–35、p3 或 pyroE3 的文献中存在促聚集/毒性，便把 7–9 aa 的无关短肽当作同一机制；
- 不能用单一 ThT 终点区分真实成纤、肽自聚集、染料吸附/淬灭、无定形沉淀与有毒寡聚体增加。

### 1.3 4EY6、肽末端与 AChE–PAS 假说的最低记录要求

- galantamine、杂原子、水、糖基、受体链、质子化、网格与柔性键如何处理；
- 实验肽的 N/C 端、盐型、D/L、酰胺化、环化和 Cys 氧化态是否与 docking 一致；
- 至少报告多个 pose cluster 和独立随机初速度 MD 中核心 PAS 接触的占有率；
- 结论只写“与 PAS/峡内接触相容”，直到有竞争、直接结合或三元体系动力学证据。

---

## 2. 12 条肽的序列特异性分层：新增“促聚集机制”解释列

### 2.1 PAS 判定标准

本文件继续把人 AChE 的核心 PAS 限定为 **Tyr72、Asp74、Tyr124、Trp286、Tyr341**。Thr75/Ser125 仅作邻近峡口环境；Ser203/His447/Glu334 为催化三联体相关；Trp86 为催化阴离子位点。此定义防止把任一峡内 docking pose 都误称为 PAS 命中。

| 肽 | Vina 最优 / 三次均值 | 已报告关键接触 | 促聚集的可检验假说 | 首要反向/混杂解释 | 建议角色 |
|---|---|---|---|---|---|
| **YLSLLQR** | −9.49 / −9.44 | Tyr72、Thr75、Glu202 | 若稳定改变峡口表面，可能促进 AChE–Aβ 模板化或三元复合物；只是待检验假说。 | PAS 竞争并抑制 AChE–Aβ；疏水自聚集或 ThT 影响。 | **PAS 主候选 1**：最先进入三元动力学。 |
| **FLLHTTR** | −9.60 / −8.77 | Asp74、Tyr72、His287 | 两个核心 PAS 接触使其值得测试正向协同。 | 最优分与均值差大；His 质子化/pose 不稳；可能竞争。 | **PAS 主候选 2**：必须先做 pose/MD 重复。 |
| **ALLLHRC** | −9.29 / −9.18 | Ser125、Ser203、Tyr124 | 不同峡内几何是否改变 AChE–Aβ 表型。 | Cys 氧化二聚、强疏水自身聚集；并非纯催化位点或 PAS 阴性。 | **机制比较肽**。 |
| **LLHPLRL** | −8.94 / −8.91 | Trp286、Tyr341、His447 | 若要增加 PAS 命中率，可检验其是否有正向或竞争性 PAS 效应。 | GRAVY/a3v 高，最先排除自聚集和 ThT 混杂。 | PAS hit-rate 备选。 |
| FCLHLQLR | −9.27 / −8.96 | Ser203、Thr75、Tyr341 | 混合 PAS/峡内假说。 | Cys 氧化/二聚；不能从 Tyr341 单点接触推方向。 | 备选。 |
| HLLTLKKHV | −8.88 / −8.69 | Tyr72、Phe346 | 单 PAS 触点的替代假说。 | 多 Lys/His 的端基与盐效应。 | 备选。 |
| YHHLLCRR | −9.03 / −8.62 | Trp86、Ser203 | 用于非 PAS/峡内比较。 | Cys 与双 His 造成化学实体和 pH 混杂。 | 非 PAS 比较备选。 |
| LLHLPKRTT | −9.01 / −8.89 | Ser203、Val340 | 用于检验非 PAS 峡内结合是否也改变量。 | 多碱性肽的膜/细胞直接效应。 | 非 PAS 比较备选。 |
| WLLVHLKK | −8.94 / −8.64 | Asn283、Gln279 | 无足够 PAS 证据。 | a3v 高、疏水/碱性自聚集和细胞直接效应。 | 低优先级。 |
| LLHPLRC | −8.91 / −8.78 | Ser125、Ser293 | 无明确 PAS 证据。 | Cys、GRAVY 0.66。 | 低优先级。 |
| HLPLLHRCC | −8.35 / −8.28 | Ser125、Tyr124、Tyr337 | 不作为首轮机制肽。 | 双 Cys 二硫键/聚集混杂极强。 | 不建议首轮。 |
| HVLLLRQCA | −8.25 / −8.07 | Thr75 | 只有 PAS 邻近接触。 | Cys、GRAVY 0.97，无核心 PAS 支持。 | 不建议首轮。 |

### 2.2 机制阳性对照的正确用法

| 文献型机制对照 | 已知机制 | 对本项目的价值 | 不能做的事 |
|---|---|---|---|
| AChE 的 35 aa 疏水基序 | 被纳入 Aβ 生长纤维，模拟完整 AChE 的促成纤作用。 | 证明“肽本身可通过 AChE 相关表面促进 Aβ”并非不可能。 | 不能代替当前 7–9 aa 候选，也不能据此把 PAS docking 判为阳性。 |
| AChE7–20 | 结构相似 β-hairpin，文献中接近完整 AChE 触发 Aβ 聚集/沉积。 | 是目前比“任意短肽”更贴近的 AChE 肽机制先例。 | 不能证明当前序列具备相同 β-hairpin 或功能。 |
| p3（Aβ17–40/42）种子 | 长度匹配时同源交叉成核，快速二级成核；有膜/细胞毒性证据。 | 为“短的 Aβ 相关肽作为种子”的阳性机制框架。 | 不是与 7–9 aa 无关短肽可直接类比的对照。 |
| pyroE3/ΔE3-Aβ40 种子 | 在细胞环境加速 wt-Aβ40 聚集并伴随毒性升高。 | 为“种子 → Aβ物种 → 细胞表型”全链条提供近期参考。 | 使用神经母细胞瘤体系，不是 PC12 直接替代。 |

---

## 3. 对接、MD 与新近交叉成核文献如何结合

### 3.1 三种不同的“促聚集”机制，必须分开建模

1. **直接同/异源模板化**：候选肽本身形成/暴露 β-compatible 表面，招募 Aβ 单体并降低成核屏障；最类似 p3、pyroE3/ΔE3 和某些 cross-seed 文献。
2. **AChE–PAS 介导的异质成核**：肽先改变 AChE PAS/峡口的 Aβ 接触表面，增强或减少 AChE–Aβ 复合物形成；最符合当前 docking 项目，但方向未知。
3. **非特异物理化学假象**：候选肽自聚、氧化二聚、盐析、表面吸附、ThT 发光/淬灭或改变 pH/离子强度。这一类必须在任何“促聚集”主张之前排除。

### 3.2 MD 的最低问题表述

- **不只模拟 AChE+肽**：至少将 `AChE + 肽` 的稳定接触视为第一层假说；若条件允许，再建模/实验验证 `AChE + Aβ + 肽` 是否显示可重复的 Aβ 招募、疏水接触或关键区域暴露变化。
- **不只看 MM-PBSA**：报告 pose cluster、核心 PAS 接触占有率、肽–AChE SASA、肽自聚趋势、Aβ 中心疏水/自识别区暴露与重复间不确定性。
- **Aβ 模型分工**：AChE 经典促纤维可先用 Aβ40 动力学建立机制；PC12 毒性应另用状态定义明确的 Aβ42 寡聚/预纤维体系。不要把 Aβ40 成纤和 Aβ42 毒性混为同一个终点。
- **p3/pyroE3 的启示**：匹配 C 端长度、种子状态和聚集物结构会决定交叉成核，故不要凭“序列有疏水残基”作方向性外推。

### 3.3 负向先例同样重要

并非任何 amyloid-like 肽/纤维都会加速 Aβ。公开研究发现一组食源蛋白来源纤维没有加速 Aβ 聚集。[Klement et al. 2023](https://doi.org/10.1038/s41598-023-28147-5) 因而对当前短肽的最安全工作假设不是“高 APR = 促 Aβ”，而是“高 APR = 先做自聚集和交叉成核实验”。

---

## 4. 预测模型：可以做什么，不能做什么

### 4.1 是否存在“直接预测促 Aβ 聚集”的深度学习模型？

**结论：在本轮定向检索的公开模型中，没有找到训练标签为“外源短肽 + Aβ（可含 AChE）→ 聚集速率/lag time/毒性增加”的可直接使用模型。**也没有找到以 `Aβ–候选肽复合物 → PC12 CCK-8/LDH/ROS/凋亡` 为训练终点的公开深度学习模型。

最接近的模型分为三类，不能混用：

| 模型/文献 | 真正预测的标签 | 对本项目最快的合法用途 | 关键限制 |
|---|---|---|---|
| **Wang et al. 2023**，Aβ42 DMS + CNN/RNN/GCN，[DOI](https://doi.org/10.1016/j.csbj.2023.03.051) | Aβ42 **单点变体**的成核、溶解性等 DMS 表型。 | 若问题是“改哪个 Aβ 残基会提高成核”，这是最贴近 Aβ 病理成核的模型文献。 | 不接受一条外源 7–9 aa 肽作为输入；不预测 AChE、交叉成核或 PC12。 |
| **PALM**，2026，[DOI](https://doi.org/10.1021/acs.jcim.6c00577) | 肽/蛋白自身 amyloidogenicity 与 APR。 | 首选的自身聚集/局部 APR 注释器；可用于 12 条排序前的风险旗标。 | 论文报告原始 PALM 对 Aβ 聚集增强单突变并不可靠，需更大 CANYA 数据再训练后改善；非促 Aβ 模型。 |
| **CANYA**，2025，[DOI](https://doi.org/10.1126/sciadv.adt5111) | 随机 20 aa、Sup35N 融合体系的内禀聚集/核化。 | 作为宽序列空间的敏感性注释或再训练数据来源。 | 7–9 aa 游离肽、Aβ、AChE 和 PC12 都是实质性域外推。 |
| **AggBERT**，2023，[DOI](https://doi.org/10.1021/acs.jcim.3c00817) | hexapeptide 自身 amyloidogenesis。 | 对 7–9 aa 肽做滑动 6-mer 旗标，适合很快的批量初筛。 | 窗口高分不代表整条肽能促进 Aβ 或造成 PC12 损伤。 |
| **AggNet / AggreProt / AggrescanAI** | 肽/蛋白 amyloid/non-amyloid 或 APR。 | 与 PALM 做共识；定位可能的自聚区。 | 同样不含 Aβ 共孵育或 PC12 标签；短肽结构预测不确定。 |
| **Amylo-IC50Pred** | 小分子 Aβ **抑制剂**和 IC50。 | 无。 | 分子类别、训练标签与生物方向均相反。不可用于当前项目。 |

### 4.2 PC12 损伤/神经毒性：哪一个最省事？

| 模型 | 可用性/输入 | 可回答的问题 | 不能回答的问题 | 对 7–9 aa 当前肽的建议 |
|---|---|---|---|---|
| **NTxPred2**，2025，[DOI](https://doi.org/10.1002/pro.70200) | Web/代码；肽模型适用范围 7–50 aa。 | 一般“神经毒性肽 / 非神经毒性肽”序列先验；最省事的第一层旗标。 | 不是 PC12；不是剂量—时间；不是 Aβ 共暴露；不是促聚集。 | **推荐作为肽-alone 风险标注**，不得作 lead 排名的唯一依据。 |
| **ToxinPred3**，2024，[DOI](https://doi.org/10.1016/j.compbiomed.2024.108926) | Web/代码/pip；面向 ≤35 aa 肽的一般毒性，含 ML、DL、LLM 和 hybrid 方案。 | 与 NTxPred2 正交的“一般毒性”复核；对当前 7–9 aa 不存在长度域外问题。 | 非神经元特异、非 PC12、非 Aβ 共暴露；训练集的 Cys 富集可能使含 Cys 短肽的分数特别需要实验复核。 | **推荐作为第二个廉价旗标**，与 NTxPred2 分列报告，不平均成病理分。 |
| **BiToxNet**，2026，[DOI](https://doi.org/10.1186/s12915-026-02508-8) | ESM2 + 手工理化特征 + bilinear attention。 | 一般神经毒肽分类，补充 NTxPred2 的模型差异。 | 训练样本仍是一般 neurotoxic/non-toxic 肽，不是 PC12/Aβ。 | 可做第二个神经毒性分数；需核实代码/服务器可用性。 |
| **NToxSEM**，2026，[DOI](https://doi.org/10.1002/pro.70661) | 多模态 stacked ensemble。 | 一般神经毒肽分类的近期比较基线。 | 无 PC12、Aβ、AChE、聚集物状态标签。 | 作为文献补充，不取代 NTxPred2 的便捷性。 |
| **PeptiTox**，2025，[DOI](https://doi.org/10.1021/acs.jcim.5c01073) | ESM2 序列 embedding + ESMFold 结构 + GNN 的一般毒性分类。 | 当需要结构感知的一般肽毒性第二意见时使用。 | 不以 PC12/Aβ 为标签；结构预测本身给极短肽带来附加不确定性。 | 可作研究性比较，不是最省事的首选。 |
| **ToxMSRC**，2025，[DOI](https://doi.org/10.1093/bioinformatics/btaf462) | Word2vec + SMOTE + 多尺度 CNN + BiLSTM；公开代码/预训练模型。 | 对长度落在训练/声明域内的一般肽毒性。 | 论文明确的长度范围为 **11–50 aa**，当前所有 7–9 aa 肽均域外；也不是神经/PC12/Aβ 模型。 | **不对当前 12 条运行**；不能用 padding 或人为延长来规避域外。 |

**实际省事排序**：

1. 先跑 **NTxPred2 + ToxinPred3**：12 条均在二者适用长度内；前者仅标为“肽-alone 一般神经毒性先验”，后者仅标为“肽-alone 一般毒性先验”。ToxinPred3 对含 Cys 肽须特别警惕训练集组成带来的序列偏好。
2. 再跑 **PALM + AggBERT（滑动 6-mer）**：仅标为“自身聚集/ThT 混杂风险”。
3. **不运行 ToxMSRC**：其 11–50 aa 域不覆盖 12 条 7–9 aa 候选；不能为求有一个深度学习分数而人为 padding。
4. 不把各类分数相加成“促 Aβ/促 PC12 总分”；必须保留独立标签。
5. 最后用小型、明确的湿实验矩阵决定机制。12 条的实验数据量不足以训练可靠的 PC12 深度学习模型；若未来积累多批次、条件标准化的 Aβ/肽/PC12 数据，才可考虑带不确定性估计的项目内模型。

---

## 5. 将“促聚集”和“PC12 损伤”拆成可证伪实验

### 5.1 必须预先区分的六个假说

| 假说 | 动力学/结构预期 | PC12 预期 | 必须控制 |
|---|---|---|---|
| H0：肽-alone 自聚/ThT 干扰 | 肽-alone 已有 ThT、浊度、DLS/形貌变化 | 肽-alone 可能直接伤害或无伤害 | 肽-alone + ThT、肽-alone + PC12、LC–MS/Cys状态。 |
| H1：Aβ 非依赖的直接肽毒性 | 与 Aβ 动力学无必然关系 | 肽-alone 已降低活性/增 LDH | 剂量—时间矩阵，预孵育组与同加组。 |
| H2：AChE 非依赖的 Aβ 共聚集/种子 | `Aβ+肽` 已缩短 lag/改变形貌 | 仅当混合物而非肽-alone 增加损伤时支持 | Aβ+肽无 AChE；SEC/DLS/TEM/AFM/CD/FTIR。 |
| H3：AChE–PAS 正向协同 | `AChE+Aβ+肽 > AChE+Aβ`，且 PAS 竞争设计削弱差异 | 三元预形成物增加损伤 | PAS 阻断、AChE-only、BChE 比较（可行时）。 |
| H4：PAS 竞争/阻断 | `AChE+Aβ+肽 < AChE+Aβ` | 可减轻而非加重损伤 | 同 H3；不能称失败。 |
| H5：成纤增多但毒性重分配 | 纤维读出升高，寡聚体读出/PC12 可能不升甚至下降 | 细胞终点不与 ThT 同向 | 寡聚体/组分读出和至少两个细胞终点。 |

### 5.2 实验 A：Aβ 聚集动力学与物种身份

**最小分组**：vehicle、肽-alone、Aβ-alone、Aβ+肽、AChE+肽、AChE+Aβ、AChE+Aβ+肽、AChE+Aβ+PAS 阻断条件；可行时加 BChE+Aβ±肽。

**最低读出**：ThT 时间曲线（lag、表观增长速率、终点）+ 至少一种正交读出（TEM/AFM、SEC/DLS、CD/FTIR 或合适的寡聚体读出）。每种肽需先确定是否干扰 ThT。

**病理机制阳性对照思路**：AChE+Aβ 用于验证 PAS 相关促聚集框架；p3/pyroE3 只能在具备适当材料与生物安全/实验条件时用作文献型机制比较，不能替代当前候选的直接结论。

### 5.3 实验 B：PC12 损伤不只测一条代谢曲线

- 先做候选肽-alone 的剂量—时间矩阵，分清模型预测的“一般毒性”是否真实存在；
- 以物理化学状态已定义的 Aβ/Aβ–肽/AChE–Aβ/AChE–Aβ–肽预孵育复合物为主，再辅以同加组；
- 最低采用 `CCK-8 或 MTT + LDH/膜完整性`；若使用 NGF 分化 PC12，增加突起长度/形态；有机制需要时再增 ROS、线粒体膜电位、Annexin V/caspase；
- PC12 未分化与 NGF 分化是不同模型；不可混合解释为同一“神经元毒性”；
- 只有肽-alone 不能解释、且至少两个细胞终点与已定义 Aβ 物种同向时，才讨论“增强 Aβ 相关 PC12 损伤”。

### 5.4 Aβ25–35 的恰当位置

Aβ25–35 是常用的快速聚集/细胞应激阳性控制片段，其聚集、膜扰动和 PC12 redox 读出已有丰富文献；但它不是当前外源候选肽促全长 Aβ 的直接模型。它可协助校验 PC12 损伤读出是否工作，不能代替 Aβ40/Aβ42 与候选肽的三元机制验证。[Aβ25–35 膜聚集研究](https://doi.org/10.1038/s41598-019-43685-7)；[PC12 MTT 方法学](https://doi.org/10.1073/pnas.91.4.1470)

---

## 6. 推荐的 Go / No-go 决策门

| 门 | 通过条件 | 不通过时的正确处理 |
|---|---|---|
| G0：化学实体 | 肽身份、端基、盐型、Cys 氧化态与 Aβ 初始状态可追溯 | 不做机制比较。 |
| G1：模型旗标可解释 | PALM/AggBERT/NTxPred2/ToxinPred3 被记录为独立旗标，不被合成为“促病理分” | 不用黑盒总分筛 lead。 |
| G2：ThT 可解释性 | 肽-alone 光学/形貌干扰被定量，独立 Aβ 制备可重复 | 只报告信号变化或自聚集。 |
| G3：聚集物身份 | 至少一项正交结构/组分读出支持 | 不称“促进 Aβ 聚集”。 |
| G4：PAS 机制 | AChE 依赖性和 PAS 竞争/阻断控制支持 | 降级为 AChE 非依赖或未定位现象。 |
| G5：PC12 病理功能 | 肽-alone 不足以解释，至少两项细胞终点支持损伤增强 | 不称“增强 Aβ 神经毒性”。 |

---

## 7. 写作与命名建议

### 可使用的措辞

- “AChE–PAS 相关促聚集假说”；
- “与 PAS/峡内接触相容的 docking pose”；
- “候选肽自身 amyloidogenicity / APR 旗标”；
- “一般神经毒性序列先验，不等同 PC12 终点”；
- “在本体系、已定义聚集物状态下，与 Aβ 相关 PC12 损伤增强一致”。

### 不应使用的措辞

- “PALM/CANYA/AggBERT 预测该肽促进 Aβ”；
- “NTxPred2/NToxSEM 预测该肽会杀伤 PC12”；
- “PAS docking 证明促聚集”；
- “ThT 高证明病理更重”；
- “AChE 长肽/p3/pyroE3 的效果证明当前 7–9 aa 肽有效”。

---

## 8. 关键补充文献（机制、近年研究与模型）

### A. 直接或高度相关的促 Aβ 聚集机制

1. Inestrosa NC, Alvarez A, Pérez CA, et al. *Acetylcholinesterase Accelerates Assembly of Amyloid-β-Peptides into Alzheimer's Fibrils: Possible Role of the Peripheral Site of the Enzyme.* **Neuron**. 1996;16:881–891. DOI: [10.1016/S0896-6273(00)80108-7](https://doi.org/10.1016/S0896-6273(00)80108-7).
2. De Ferrari GV, Canales MA, Shin I, et al. *A structural motif of acetylcholinesterase that promotes amyloid beta-peptide fibril formation.* **Biochemistry**. 2001;40:10447–10457. DOI: [10.1021/bi0101392](https://doi.org/10.1021/bi0101392). 35 aa 疏水 AChE 肽的直接促成纤证据。
3. Hou LN, Xu JR, Zhao QN, et al. *A New Motif in the N-Terminal of Acetylcholinesterase Triggers Amyloid-β Aggregation and Deposition.* **CNS Neurosci Ther**. 2014;20:59–66. DOI: [10.1111/cns.12161](https://doi.org/10.1111/cns.12161). AChE7–20 β-hairpin 促聚集先例。
4. Tian Y, Torres-Flores AP, Shang Q, et al. *The p3 peptides (Aβ17–40/42) rapidly form amyloid fibrils that cross-seed with full-length Aβ.* **Nat Commun**. 2025;16:2040. DOI: [10.1038/s41467-025-57341-4](https://doi.org/10.1038/s41467-025-57341-4). 近期直接同源交叉成核及膜毒性证据。
5. Cruceta L, Sun Y, Kenyaga JM, et al. *Modulation of aggregation and structural polymorphisms of β-amyloid fibrils in cellular environments by pyroglutamate-3 variant cross-seeding.* **J Biol Chem**. 2023;299:105196. DOI: [10.1016/j.jbc.2023.105196](https://doi.org/10.1016/j.jbc.2023.105196).
6. Vugmeyster L, et al. *Cross-Seeded Fibrillation Induced by Pyroglutamate-3 and Truncated Aβ40 Variants Leads to Aβ40 Structural Polymorphism Modulation and Elevated Toxicity.* **ACS Chem Neurosci**. 2021. DOI: [10.1021/acschemneuro.1c00341](https://doi.org/10.1021/acschemneuro.1c00341).
7. Raskatov JA. *Amyloid Alpha: The Neglected Cousin of Amyloid Beta.* **ChemBioChem**. 2026. DOI: [10.1002/cbic.202500912](https://doi.org/10.1002/cbic.202500912). p3/Amyloid-α 的近期视角文章。
8. Zhang et al. *Exploring pathological link between antimicrobial and amyloid peptides.* **Chem Soc Rev**. 2024;53:8713–8763. DOI: [10.1039/D3CS00878A](https://doi.org/10.1039/D3CS00878A). 交叉成核方向性与结构依赖综述。
9. *Amylin and beta amyloid proteins interact to form amorphous heterocomplexes with enhanced toxicity in neuronal cells.* **Sci Rep**. 2020. DOI: [10.1038/s41598-020-66602-9](https://doi.org/10.1038/s41598-020-66602-9).
10. *Inhibition of the Early-Stage Cross-Amyloid Aggregation of Amyloid-β and IAPP via EGCG: Insights from Molecular Dynamics Simulations.* **ACS Omega**. 2024. DOI: [10.1021/acsomega.4c00500](https://doi.org/10.1021/acsomega.4c00500).
11. *Food protein-derived amyloids do not accelerate amyloid β aggregation.* **Sci Rep**. 2023. DOI: [10.1038/s41598-023-28147-5](https://doi.org/10.1038/s41598-023-28147-5). 重要反例。

### B. Aβ 聚集 / 自身聚集深度学习与机器学习

12. Wang B, Razavi S, Gamazon ER. *Towards mechanistic models of mutational effects: Deep learning on Alzheimer’s Aβ peptide.* **Comput Struct Biotechnol J**. 2023;21:2434–2445. DOI: [10.1016/j.csbj.2023.03.051](https://doi.org/10.1016/j.csbj.2023.03.051). Aβ42 突变—成核表型，不是外源肽模型。
13. Thompson M, Martín M, Olmo TS, et al. *Massive experimental quantification allows interpretable deep learning of protein aggregation.* **Sci Adv**. 2025;11:eadt5111. DOI: [10.1126/sciadv.adt5111](https://doi.org/10.1126/sciadv.adt5111). CANYA 的实验域和外推边界。
14. Eschbach E, Deibler K, Korani D, Swanson S. *Predicting Peptide Aggregation with Protein Language Model Embeddings.* **J Chem Inf Model**. 2026. DOI: [10.1021/acs.jcim.6c00577](https://doi.org/10.1021/acs.jcim.6c00577). PALM；其对 Aβ 突变任务的限制必须一并报告。
15. Perez R, Li X, Giannakoulias S, Petersson EJ. *AggBERT: Best in Class Prediction of Hexapeptide Amyloidogenesis with a Semi-Supervised ProtBERT Model.* **J Chem Inf Model**. 2023;63:5727–5733. DOI: [10.1021/acs.jcim.3c00817](https://doi.org/10.1021/acs.jcim.3c00817).
16. He W, Xu X, Li H, Zhou J, Gao X. *AggNet: Advancing protein aggregation analysis through deep learning and protein language model.* **Protein Sci**. 2025;34:e70031. DOI: [10.1002/pro.70031](https://doi.org/10.1002/pro.70031).

### C. 神经毒性 / PC12 边界与深度学习

17. Shearman MS, Ragan CI, Iversen LL. *Inhibition of PC12 cell redox activity is a specific, early indicator of the mechanism of beta-amyloid-mediated cell death.* **PNAS**. 1994;91:1470–1474. DOI: [10.1073/pnas.91.4.1470](https://doi.org/10.1073/pnas.91.4.1470).
18. Rathore AS, Jain S, Choudhury S, Raghava GPS. *A large language model for predicting neurotoxic peptides and neurotoxins.* **Protein Sci**. 2025;34:e70200. DOI: [10.1002/pro.70200](https://doi.org/10.1002/pro.70200). NTxPred2。
19. Rathore AS, Choudhury S, Arora A, Tijare P, Raghava GPS. *ToxinPred 3.0: An improved method for predicting the toxicity of peptides.* **Comput Biol Med**. 2024;179:108926. DOI: [10.1016/j.compbiomed.2024.108926](https://doi.org/10.1016/j.compbiomed.2024.108926). 一般毒性，不是神经/PC12/Aβ 模型。
20. Zhang S, Ren J, Liang Y, et al. *An innovative peptide toxicity prediction model based on multi-scale convolutional neural network and residual connection.* **Bioinformatics**. 2025;41:btaf462. DOI: [10.1093/bioinformatics/btaf462](https://doi.org/10.1093/bioinformatics/btaf462). ToxMSRC；仅 11–50 aa，不适合当前 7–9 aa 肽。
21. *Integrating Protein Language Models and Geometric Deep Learning for Peptide Toxicity Prediction.* **J Chem Inf Model**. 2025;65:7800–7810. DOI: [10.1021/acs.jcim.5c01073](https://doi.org/10.1021/acs.jcim.5c01073). PeptiTox，一般毒性模型。
22. *BiToxNet: a deep learning framework integrating multimodal features for accurate identification of neurotoxic peptides and proteins.* **BMC Biology**. 2026. DOI: [10.1186/s12915-026-02508-8](https://doi.org/10.1186/s12915-026-02508-8).
23. *NToxSEM: Enhancing prediction of neurotoxic peptides and neurotoxins using a stacked ensemble-based multimodal framework.* **Protein Sci**. 2026. DOI: [10.1002/pro.70661](https://doi.org/10.1002/pro.70661).
24. *De novo aggregation of Alzheimer’s Aβ25–35 peptides in a lipid bilayer.* **Sci Rep**. 2019. DOI: [10.1038/s41598-019-43685-7](https://doi.org/10.1038/s41598-019-43685-7).

---

## 一句话版本

**对当前 12 条肽，最省事且不越界的路线不是寻找一个不存在的“促 Aβ / PC12 一键预测器”，而是：PALM/AggBERT 标自身聚集风险，NTxPred2 + ToxinPred3 分别标肽-alone 一般神经毒性/一般毒性，AChE–PAS docking/重复 MD 提出三元机制假说，再用 Aβ+AChE+肽+PAS 阻断和 PC12 双终点决定它究竟是促聚集、竞争抑制、直接毒性还是实验假象。ToxMSRC 的 11–50 aa 域不覆盖本项目，不能硬用。近期 p3 与 pyroE3/ΔE3-Aβ 文献证明病理性交叉成核确实存在，但不能替当前 7–9 aa 肽的实验证据。**
