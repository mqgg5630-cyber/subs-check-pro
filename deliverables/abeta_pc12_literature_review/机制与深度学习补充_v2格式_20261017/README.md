# 机制与深度学习补充（v2.1 格式，独立目录）

本目录是为“Aβ 病理机制中促进 Aβ 聚集、AChE–PAS、交叉成核、PC12 损伤及可用深度学习模型”重做的**独立**交付。结构沿用既有 v2 的结论先行、数据边界、12 肽分层、计算模型适用性、可证伪实验、Go/No-go 和写作措辞；没有覆盖原始初版、既有 v2 或 v3。

## 文件

- `Aβ促聚集_AChE-PAS_12条对接肽_机制与深度学习补充_v2.1.docx`：可直接审阅/批注的 Word 版本。
- `Aβ促聚集_AChE-PAS_12条对接肽_机制与深度学习补充_v2.1.md`：同内容、可搜索且便于粘贴的 Markdown 源稿。
- `机制与模型补充文献索引_v2.1.csv`：关键机制与模型文献的 DOI 级审计索引。
- `SHA256SUMS.txt`：最终交付文件的完整性校验；本地同步后可用 `sha256sum -c SHA256SUMS.txt`（或同等工具）复核。
- `code/build_abeta_pas_mechanism_dl_v21.py`：独立渲染脚本（位于仓库 `code/`）。

## 重要边界

1. AChE 35-aa motif、AChE7–20、p3、pyroE3/ΔE3-Aβ 是有证据的机制先例/阳性对照框架，**不是**当前 12 条 7–9 aa 肽已经生效的证据。
2. PALM/CANYA/AggBERT/AggNet 预测的是自身聚集或局部 amyloidogenicity；Wang 2023 是 Aβ42 单点变体模型；这些不是“外源肽促进 Aβ”预测器。
3. NTxPred2/BiToxNet/NToxSEM 是一般神经毒性预测器；ToxinPred3/PeptiTox 是一般肽毒性预测器；它们都**不是** Aβ 共暴露下的 PC12 CCK-8、LDH、ROS、线粒体膜电位或凋亡预测器。ToxMSRC 仅覆盖 11–50 aa，故不适用于当前 7–9 aa 候选。
4. 计算输出应保留为独立旗标，不能相加成“促 Aβ/促 PC12 总分”。
5. `E:\0github\git-sync\...` 不是本沙箱可直接写入的位置；本目录已写入仓库工作区。是否同步到 Windows 硬盘应以用户本地同步回执为准。

## 重建

```bash
python3 -m venv /tmp/abeta-v2-render
/tmp/abeta-v2-render/bin/pip install python-docx
/tmp/abeta-v2-render/bin/python code/build_abeta_pas_mechanism_dl_v21.py
```

渲染脚本只会生成本目录的 DOCX、CSV 与 README。
