# Aβ 病理机制：促聚集、AChE–PAS 与 PC12 损伤
## 12 条候选短肽的独立文献—计算—湿实验审查（v3）

**版本**：2026-10-14（Asia/Shanghai）

**文件性质**：新建的机制导向研究备忘；不覆盖目录中的 `Aβ聚集抑制与PC12神经保护_12条候选肽_文献与模型审查_初版.docx`，也不把 docking、MD 或序列模型预测写成已证实结论。

**本版方向**：研究目标是检验外源短肽是否**促进病理性 Aβ 聚集过程和/或增加 Aβ 相关 PC12 损伤**，尤其是其是否通过人 AChE 的 peripheral anionic site（PAS）改变 Aβ 装配；不是寻找抑制 Aβ 聚集或神经保护的肽。

---

## 一页结论：先纠正“促聚集”真正要证明什么

1. **AChE–Aβ 本身有促装配的经典病理机制依据。**Inestrosa 等报道 AChE 可加速 Aβ 成纤，且 PAS 配体 propidium 会削弱这一效应，而催化位点抑制剂 edrophonium 不产生同样模式。这个结果支持“PAS 参与 AChE 促 Aβ 装配”的病理机制，但**不能**自动推出任何 PAS-docking 短肽都会进一步促聚集。
2. **PAS 结合肽的方向必须由三元体系决定。**同一个肽可能桥接/稳定 AChE–Aβ、改变 PAS 表面并增强装配；也可能竞争 Aβ 而阻断 AChE 的促聚集作用。因此，`AChE + Aβ + 肽` 相对 `AChE + Aβ` 的结果，以及 PAS 阻断控制，才是方向性证据。
3. **“纤维更多”与“PC12 更毒”不是同义命题。**ThT 高、β-sheet 增加或成熟纤维增加可以表示聚集加速，却不等于可溶性有毒寡聚体更多。病理机制研究必须把“成纤负荷”和“毒性物种/细胞损伤”分成独立终点。
4. **建议首先验证的机制组合**：YLSLLQR 与 FLLHTTR 作为 PAS 假说主候选；ALLLHRC 作为峡内/催化区相关的比较肽，而非 PAS 阴性对照。若第三条目标是提高 PAS 接触命中率而非做比较，可用 LLHPLRL 替代，但其自身聚集干扰风险更高。
5. **可成立的最终表述应是分层的。**只有在肽-alone 对照、Aβ 动力学、正交聚集物表征、AChE 依赖性/PAS 竞争控制和至少两类 PC12 终点同向后，才能说“该肽在本体系中增强 AChE 相关 Aβ 病理性装配并伴随 PC12 损伤增强”。在此之前，仅能称为“促聚集/促毒机制假说”。

---

## 1. 病理机制问题的正确拆分

### 1.1 本项目的主问题不是“ThT 是否升高”

本项目要建立的是下列因果链中的哪一段成立：

`候选肽 → AChE–PAS / Aβ 相互作用改变 → Aβ 物种与装配动力学改变 → PC12 损伤改变`

每一个箭头都需要自己的对照；不能用一个 Vina 分数、一次 MD 轨迹、一个 ThT 终点或一次 CCK-8 同时替代所有箭头。

| 待区分的机制 | 关键问题 | 可能出现的表型 | 若不分开会造成的错误 |
|---|---|---|---|
| M1：肽自身聚集/染料干扰 | 肽是否自己成团、发光、淬灭或吸附 ThT？ | 肽-alone 已改变 ThT、浊度或形貌 | 把肽本身的物理化学行为误判成 Aβ 促聚集 |
| M2：AChE 非依赖的 Aβ 共聚集/种子作用 | 肽是否直接缩短 Aβ lag phase 或改变 Aβ 物种？ | `Aβ + 肽` 相对 Aβ-alone 改变 | 错把直接 Aβ 作用解释为 PAS 机制 |
| M3：AChE–PAS 正向协同 | 肽是否让 AChE 更强地促进 Aβ 装配？ | `AChE+Aβ+肽 > AChE+Aβ`，且 PAS 阻断减弱差异 | 仅凭“碰到 PAS 残基”就宣布促聚集 |
| M4：PAS 竞争/阻断 | 肽是否占据/改变 PAS 而减少 AChE–Aβ 接触？ | `AChE+Aβ+肽 < AChE+Aβ` | 把有价值的反向结果误称为实验失败 |
| M5：毒性物种重分配 | 形成的是成熟纤维、原纤维、可溶寡聚体还是非特异沉淀？ | 聚集读出与 PC12 终点可同向或反向 | 将“ThT 更高”误写成“病理毒性更强” |

### 1.2 对“病理性促聚集”的操作性定义

本备忘不把任何聚集增加都称为病理性。建议预先定义三层证据：

- **装配层**：相对 Aβ-alone 或 AChE+Aβ，对照明确地缩短 lag time、提高表观增长速率、改变终点/β-sheet/形貌；
- **机制层**：该差异有 AChE 依赖性，并被合适的 PAS 阻断/竞争设计或适当酶对照支持；
- **病理功能层**：经过物理化学表征的聚集物在 PC12 中引起更严重的、不能由肽-alone 解释的损伤，并由至少两个细胞终点支持。

如果只达到第一层，正确结论是“促进或重定向 Aβ 装配”；不能直接升级成“促进阿尔茨海默病病理”或“增强神经毒性”。

---

## 2. 可用的病理机制文献支点

| 文献 | 可支持的命题 | 不能被过度外推的部分 |
|---|---|---|
| Inestrosa NC et al., *Neuron*, 1996, DOI: 10.1016/S0896-6273(00)80108-7 | AChE 可增强 Aβ 成纤；PAS 参与该效应；propidium 与 edrophonium 的不同结果提供 PAS 方向性控制。 | 不证明任意新短肽会促进 Aβ；也不证明 docking 的 PAS pose 就是三元体系中的真实作用模式。 |
| De Ferrari GV et al., *Biochemistry*, 2001, DOI: 10.1021/bi0101392 | AChE 邻近 PAS 的疏水结构基序能够影响 Aβ 成纤。 | 不应把 AChE 的内源结构基序直接等同于 7–9 aa 外源肽。 |
| Alvarez A et al., *J Neurosci*, 1998, 18:3213–3223 | 稳定 AChE–Aβ 复合物可改变 AChE 生化性质，并与 Aβ 纤维神经毒性增强相关。 | 不应省略 AChE-alone、肽-alone 与 Aβ-alone 条件。 |
| Muñoz FJ & Inestrosa NC, *FEBS Lett*, 1999, DOI: 10.1016/S0014-5793(99)00468-8 | AChE–Aβ 聚集物的毒性受 Aβ 类型和 AChE 浓度影响。 | 不能将一个 AChE:Aβ 比值的结果泛化到所有浓度或 Aβ40/Aβ42 状态。 |
| Shearman MS et al., *PNAS*, 1994, DOI: 10.1073/pnas.91.4.1470 | PC12 的 MTT/redox 读出可敏感反映 Aβ 早期损伤机制。 | MTT/CCK-8 不是不可逆死亡的单独证明；需配合 LDH、凋亡或形态终点。 |
| RCSB PDB 4EY6 | 4EY6 是人源重组 AChE 与 (−)-galantamine 的复合物，可作为 AChE 对接起点。 | 共晶配体、受体链、质子化、末端状态和网格处理都会影响短肽 pose；必须在方法中公开。 |

**关键辨析**：Aβ1–40 的 AChE 促纤维动力学更容易与经典机制文献衔接；若要把结果接到 PC12 病理损伤，需在独立且状态定义明确的 Aβ1–42 寡聚/预纤维体系中验证。不能把两者不加区分地统称为一个“Aβ 实验”。

---

## 3. 12 条肽：按机制假说而不是“预测已证实”分层

### 3.1 PAS 判定口径

本文件把人 AChE 的核心 PAS 记为 **Tyr72、Asp74、Tyr124、Trp286、Tyr341**。Thr75/Ser125 属于邻近峡口环境；Ser203/His447/Glu334 为催化三联体相关；Trp86 为催化阴离子位点。接触到后几类残基不应被直接称为“PAS 结合”。

| 肽 | aa | Vina 最优 / 三次均值 | 已报告关键接触 | 机制定位与首轮角色 | 主要混杂/复核点 |
|---|---:|---|---|---|---|
| **YLSLLQR** | 7 | −9.49 / −9.44 | Tyr72、Thr75、Glu202 | **PAS 主候选 1**：当前排序最稳定；用于检验是否存在 AChE–PAS 正向协同或竞争。 | 仅有 Tyr72 一个核心 PAS 触点；需做 pose cluster、重复 MD 与竞争实验。 |
| **FLLHTTR** | 7 | −9.60 / −8.77 | Asp74、Tyr72、His287 | **PAS 主候选 2**：两个核心 PAS 接触，值得首轮并列检验。 | 最优分与均值差 0.83，说明最佳 pose 的稳健性须优先复核；His 质子化需说明。 |
| **ALLLHRC** | 7 | −9.29 / −9.18 | Ser125、Ser203、Tyr124 | **峡内/催化区相关比较肽**：用于比较不同沟槽几何是否产生不同表型。 | 同时触及 PAS Tyr124 和 Ser203，不能当“PAS 阴性”或“纯催化位点”；含 Cys、GRAVY 1.14、自聚集/氧化风险。 |
| **LLHPLRL** | 7 | −8.94 / −8.91 | Trp286、Tyr341、His447 | 若需要增加 PAS 命中率，可作**替代第三主候选**。 | 两个核心 PAS 触点，但 GRAVY 0.84、a3v 0.45，肽自身聚集/ThT 干扰风险高。 |
| FCLHLQLR | 8 | −9.27 / −8.96 | Ser203、Thr75、Tyr341 | PAS/峡内混合备选。 | 含 Cys；不优先于无 Cys 的两条主候选。 |
| HLLTLKKHV | 9 | −8.88 / −8.69 | Tyr72、Phe346 | 单 PAS 触点备选。 | 多 Lys/His，实际电荷与端基状态要一致。 |
| YHHLLCRR | 8 | −9.03 / −8.62 | Trp86、Ser203 | 非 PAS 比较备选。 | Cys、双 His；与 PAS 肽理化性质不匹配，不能作为单一严格阴性对照。 |
| LLHLPKRTT | 9 | −9.01 / −8.89 | Ser203、Val340 | 非 PAS 比较备选。 | 多碱性/His，需独立测肽-alone 效应。 |
| WLLVHLKK | 8 | −8.94 / −8.64 | Asn283、Gln279 | 低优先级。 | a3v 0.49 最高，疏水/碱性混杂风险强。 |
| LLHPLRC | 7 | −8.91 / −8.78 | Ser125、Ser293 | 低优先级。 | 含 Cys，且无核心 PAS 证据。 |
| HLPLLHRCC | 9 | −8.35 / −8.28 | Ser125、Tyr124、Tyr337 | 暂不进入首轮。 | 双 Cys，氧化/二聚化与自身聚集风险最高。 |
| HVLLLRQCA | 9 | −8.25 / −8.07 | Thr75 | 暂不进入首轮。 | 仅邻近 PAS 的 Thr75；含 Cys、GRAVY 0.97。 |

### 3.2 推荐的首轮配置

- **最小两肽**：YLSLLQR + FLLHTTR；
- **三肽机制版**：YLSLLQR + FLLHTTR + ALLLHRC（不同峡内几何比较）；
- **三肽 PAS 命中版**：YLSLLQR + FLLHTTR + LLHPLRL（更多核心 PAS 接触，但更高自身聚集风险）。

这三套配置的共同前提是：它们是**待检验的机制假说工具**，不等于三条肽已被证明促 Aβ 聚集或增强 PC12 损伤。

---

## 4. 现有计算结果应如何解释

### 4.1 Docking/MD 的合法结论范围

- 可说：“该 pose 与 AChE PAS/峡内接触相容”；
- 可说：“在当前 Vina 工作流中，YLSLLQR 的三次排序较一致，FLLHTTR 的最佳 pose 更强但离散度较大”；
- 可说：“对接结果支持优先做 AChE 依赖性与 PAS 竞争的动力学实验”；
- **不可说**：“Vina −9.x 证明高亲和力/Kd”、“肽已占据 PAS”、“肽会通过 PAS 促进 Aβ 聚集”、“NTxPred2 阳性证明 PC12 神经毒性”。

### 4.2 4EY6 与肽化学实体的一致性门槛

4EY6 含 galantamine。后续复核应记录：

1. galantamine、结晶水、糖基/非必要杂原子是否移除以及处理方法；
2. 受体链、网格中心/大小、柔性键、质子化状态和离子条件；
3. 真实合成肽是游离 N 端还是封端、C 端游离酸还是酰胺、盐型为何；
4. Cys 肽使用还原单体、自然氧化混合物还是指定二硫键形式；
5. 至少两个合理 pose cluster 与独立初速度 MD 重复中的核心 PAS 接触占有率。

若湿实验是 C 端酰胺化肽而 docking 为自由羧基版本，电荷与 H-bond 图谱已改变；二者不能混作同一个分子实体解释。

### 4.3 AI/ML 的边界

- NTxPred2：至多提供一般“神经毒性序列”旗标，**不是** PC12、生物剂量反应或 Aβ 共暴露预测器；
- CANYA、PALM、AggBERT、PATH、AmyloGram：可做候选肽**自身**聚集风险/局部 APR 注释，**不是**“促进 Aβ 聚集”的模型；
- CANYA 的实验域为随机 20 aa 肽的 Sup35N 融合体系，对 7–9 aa 游离短肽是实质性域外推；
- 小分子 Aβ inhibitor IC50 模型在分子类别和生物方向上均不适用于本项目。

因此，模型只能帮助决定“哪些肽更需要先排除自聚集、Cys 氧化或光学干扰”，不能把任一肽选为“促病理 lead”。

---

## 5. 可证伪的实验路线

### 5.1 G0：先锁定材料身份与初始状态

| 项目 | 必须确认的内容 | 未确认时不能做出的结论 |
|---|---|---|
| 候选肽 | 序列、纯度、端基、盐型、工作液浓度、冻融/溶解记录 | 不能将实验效应归属到文档中标注的单一序列/电荷状态 |
| 含 Cys 肽 | 还原/氧化状态；必要时 LC–MS 或等效游离巯基检查 | 不能将二硫键二聚、沉淀或自聚集误作 Aβ 促聚集 |
| Aβ | Aβ40/Aβ42、批号、单体化方法、溶剂残留、预孵育状态、浓度确认 | 不能将不同批次/不同物种状态作机制比较 |
| AChE | 人源/其他物种、活性位点摩尔浓度、批次与缓冲体系 | 不能将 docking 的人 AChE 结论无说明外推给其他酶 |

### 5.2 G1：Aβ 装配动力学——先区分 M1–M4

建议在同一 Aβ 制备批次中至少配置下列组别：

- vehicle；
- 肽-alone；
- Aβ-alone；
- Aβ + 肽；
- AChE + 肽（无 Aβ）；
- AChE + Aβ；
- AChE + Aβ + 肽；
- AChE + Aβ + 合适 PAS 阻断/竞争控制；
- 条件允许时，BChE + Aβ ± 肽或另一适当酶比较，检验 cholinesterase/PAS 架构特异性。

**读出不应只有一个 ThT 终点。**最低应报告：空白校正后的 ThT 时间曲线、lag time、表观增长速率、终点；并加入至少一种正交手段，例如 TEM/AFM、SEC/DLS、CD/FTIR 或经验证的寡聚体读出。肽-alone 的光学/形貌对照必须与 Aβ 体系同期进行。

### 5.3 G2：把“更多聚集”拆成聚集物身份

| 结果模式 | 合理解释 | 下一步 |
|---|---|---|
| ThT 上升，但肽-alone 也上升/有沉淀 | 可能是肽自聚集或染料效应 | 先做 LC–MS、形貌、无 Aβ 光学控制；不称促 Aβ。 |
| Aβ+肽 增强，AChE 加入不再额外增加 | 可能为 AChE 非依赖共聚集/种子路径 | 检验直接 Aβ–肽相互作用与聚集物组成。 |
| AChE+Aβ+肽 高于 AChE+Aβ，且 PAS 阻断削弱差异 | 支持 AChE–PAS 相关正向协同 | 进入不同 Aβ 状态和 PC12 复合物验证。 |
| AChE+Aβ+肽 低于 AChE+Aβ | 支持 PAS 竞争/阻断或其他反向机制 | 不应硬解释成“促聚集失败”；将其按 anti-aggregation 机制另行验证。 |
| 成熟纤维上升而 PC12 损伤不升/下降 | 可能把 Aβ 转向相对低毒的纤维终点 | 定量可溶寡聚体/原纤维，不将纤维负荷等同神经毒性。 |

### 5.4 G3：PC12 损伤验证——只在聚集物状态定义后开展

建议先将细胞外预孵育、已表征的 Aβ/Aβ–肽/AChE–Aβ/AChE–Aβ–肽复合物加入 PC12，以降低“游离肽即时直接作用”与“聚集物效应”混杂；同时保留同加细胞组作为辅助判断。

**最小细胞分组**：vehicle、肽-alone、AChE-alone、AChE+肽、Aβ-alone、Aβ+肽、AChE+Aβ、AChE+Aβ+肽，以及在 G1 出现机制信号后加入的 PAS 阻断条件。

**最小细胞终点**：CCK-8 或 MTT 加上 LDH/膜完整性；如采用 NGF 分化 PC12，应增加突起长度/形态。若拟声称凋亡或线粒体机制，则相应增加 Annexin V/caspase 或 ROS/线粒体读出。一个单独的 MTT/CCK-8 下降只能说明代谢/氧化还原读出改变，不能单独证明不可逆细胞死亡。

### 5.5 G4：Go / No-go 决策门

| 门 | 进入下一层的条件 | 不满足时的处理 |
|---|---|---|
| G0 材料门 | 肽和 Aβ 的化学实体/初始状态可追溯 | 先解决制剂与 Cys 状态；不比较机制。 |
| G1 可解释性门 | 肽-alone 不足以解释 ThT/形貌变化；动力学在独立 Aβ 制备中可重复 | 仅报告光学/自身聚集现象。 |
| G2 聚集物门 | 有至少一个正交结构/组分读出支持 | 不把 ThT 改变写成 Aβ 装配改变。 |
| G3 PAS 机制门 | AChE 依赖性和 PAS 阻断/比较证据支持 | 降级为 AChE 非依赖或未定位的现象。 |
| G4 病理功能门 | 肽-alone 无法解释，且至少两个 PC12 终点支持损伤增强 | 不称“增强 Aβ 神经毒性”。 |

---

## 6. 建议的写作措辞

### 可使用

- “与人 AChE PAS 接触相容的 docking pose”；
- “在当前设置下，YLSLLQR 显示较一致的 Vina 重复排序”；
- “FLLHTTR 对 Asp74/Tyr72 的接触值得用竞争与三元动力学实验检验”；
- “候选肽可能引起 AChE–Aβ 协同、PAS 竞争或 AChE 非依赖共聚集，需用预设对照区分”；
- “在本体外体系中，经过定义的复合物与 PC12 损伤增强相关”。

### 不可使用

- “已证明这 12 条肽通过 PAS 促进 Aβ 聚集”；
- “Vina 分数就是亲和力/Kd”；
- “NTxPred2 阳性证明 PC12 神经毒性”；
- “自身 amyloid predictor 高分证明促 Aβ”；
- “ALLLHRC 是 PAS 阴性对照”；
- “ThT 高就代表阿尔茨海默病病理/神经毒性更重”。

---

## 7. 参考文献与数据边界

1. Inestrosa NC, Alvarez A, Pérez CA, et al. *Acetylcholinesterase Accelerates Assembly of Amyloid-β-Peptides into Alzheimer's Fibrils: Possible Role of the Peripheral Site of the Enzyme.* **Neuron**. 1996;16:881–891. DOI: 10.1016/S0896-6273(00)80108-7.
2. De Ferrari GV, Canales MA, Shin I, et al. *A structural motif of acetylcholinesterase that promotes amyloid beta-peptide fibril formation.* **Biochemistry**. 2001;40:10447–10457. DOI: 10.1021/bi0101392.
3. Alvarez A, Alarcón R, Opazo C, et al. *Stable complexes involving acetylcholinesterase and amyloid-beta peptide change the biochemical properties of the enzyme and increase the neurotoxicity of Alzheimer's fibrils.* **J Neurosci**. 1998;18:3213–3223.
4. Muñoz FJ, Inestrosa NC. *Neurotoxicity of acetylcholinesterase amyloid β-peptide aggregates is dependent on the type of Aβ peptide and the AChE concentration present in the complexes.* **FEBS Lett**. 1999. DOI: 10.1016/S0014-5793(99)00468-8.
5. Shearman MS, Ragan CI, Iversen LL. *Inhibition of PC12 cell redox activity is a specific, early indicator of the mechanism of beta-amyloid-mediated cell death.* **PNAS**. 1994;91:1470–1474. DOI: 10.1073/pnas.91.4.1470.
6. RCSB Protein Data Bank. *Crystal Structure of Recombinant Human Acetylcholinesterase in Complex with (−)-galantamine*, PDB 4EY6.
7. Rathore AS, Jain S, Choudhury S, Raghava GPS. *A large language model for predicting neurotoxic peptides and neurotoxins.* **Protein Science**. 2025;34:e70200. DOI: 10.1002/pro.70200.
8. Thompson M, Martín M, Olmo TS, et al. *Massive experimental quantification allows interpretable deep learning of protein aggregation.* **Sci Adv**. 2025;11:eadt5111. DOI: 10.1126/sciadv.adt5111.
9. Perez R, Li X, Giannakoulias S, Petersson EJ. *AggBERT: Best in Class Prediction of Hexapeptide Amyloidogenesis with a Semi-Supervised ProtBERT Model.* **J Chem Inf Model**. 2023;63:5727–5733. DOI: 10.1021/acs.jcim.3c00817.

---

## 结语

本版的逻辑方向是明确的：**不是“如何阻止 Aβ 聚集并保护 PC12”，而是“候选肽是否、经由何种可证伪机制，促进 Aβ 病理性装配并增加 Aβ 相关 PC12 损伤”。**

但是，真正严谨的病理机制不能预设答案。对 PAS 候选肽而言，“促进”“竞争阻断”和“肽自身造成的假象”都是同等需要被实验排除或支持的可能结果。把这三者区分开，才能让反方向研究得到可发表、可复核的机制结论。
