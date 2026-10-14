# Aβ 聚集抑制与 PC12 神经保护｜文献与模型审查（初版）

**生成时间：2026-10-14 09:12 Asia/Shanghai**

## 文件

- `Aβ聚集抑制与PC12神经保护_12条候选肽_文献与模型审查_初版.md` — 完整、可搜索的中文审查正文。
- `Aβ聚集抑制与PC12神经保护_12条候选肽_文献与模型审查_初版.docx` — 便于转发、批注和放入课题资料的 Word 版本。
- `核心文献索引.csv` — 19 条核心文献的 DOI/PMID/用途索引，可导入表格软件。
- `references_abeta_pc12.bib` — 用于 Zotero/BibTeX 的简化引用索引；正式投稿前应从 DOI 元数据服务核对所有作者、卷期页码。
- `12条候选肽_序列与实验映射模板.csv` — 待拿到 12 条序列后填充的映射模板。

## 当前边界

用户给出的 Windows `.docx` 路径未同步到此工作区，因此本版不能把任何结论说成针对具体 12 条肽。请上传该文档或填写序列映射 CSV；收到后即可进行逐条序列-文献-模型-实验条件映射。

## 重建

```bash
PYTHONPATH=/tmp/accio-deps python3 code/build_abeta_pc12_literature_packet.py
```

脚本需要 `python-docx`；Markdown 与 CSV 不依赖该库。
