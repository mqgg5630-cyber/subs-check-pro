# 爆款电商视觉案例库｜公开在线案例｜v3

**生成时间：2026-10-14 09:12 Asia/Shanghai（Asia/Shanghai）**<br>
注意：这表示沙箱构建时间；复制到 Windows 后的文件创建 / 修改时间由本机文件系统决定。

## 交付内容

- `爆款电商视觉案例库_公开在线案例_Accio视觉复刻参考_v3.pdf` — 23 页、已扁平化的案例研究 PDF
- `爆款电商视觉案例库_公开在线案例_Accio视觉复刻参考_v3.pptx` — 23 页、每页仅一张完整图片的 PPTX
- `preview_contact_sheet_v3.jpg` — 全页预览
- `SOURCES_AND_USAGE_BOUNDARIES.md` — 视觉图源、分析图源和使用边界
- `AI_ASSISTED_RECREATION_TEMPLATE.md` — AI 示范的真实边界、工件清单与迁移清单
- `ai_recreation_prompt_used.txt` — S0 实际调用提示词原文（Arena 图像模型；非 Accio）
- `recreation_review_log.csv` — 人工审核风险与改动模板

## 这版解决的问题

上一版用了自创龙虾周边来说明流程，视觉与真实产品案例的距离过大。本版不再把原创示意当主案例：

1. 选用 6 个公开在线、具有明确视觉语言的电商案例；
2. 每个案例分开“视觉图源”和“分析图源”；
3. 从每个案例提炼一条具体购买决策逻辑，而不是只评价“好看”；
4. 把案例翻译成产品介绍问题、资产角色表、PDP 首屏结构和可执行任务书；
5. 所有图片均作为低分辨率研究摘录，明确不是可商用素材、品牌授权或 Accio 实机输出。
6. 新增 6 页透明的 AI 辅助复刻示范：来源规则 → 实际提示词 → Arena 的 S0 概念图 → 人审风险单 → S1 人工重建 → 证据账本。它明确不是 Accio 实机运行。

## 公开来源

1. **Magic Spoon**<br>
   - 视觉摘录：[Luna Templates 的公开页面截图](https://lunatemplates.co/blogs/shopify-website-inspiration/magic-spoon)<br>
   - 案例 / 结构分析：[Shopify：亮色、动效、UGC 与 BYOB 筛选案例](https://www.shopify.com/blog/11863377-30-beautiful-and-creative-ecommerce-website-designs)
2. **De La Calle**<br>
   - 视觉摘录：[Shopify 公开案例截图](https://www.shopify.com/blog/11863377-30-beautiful-and-creative-ecommerce-website-designs)<br>
   - 案例 / 结构分析：[Shopify：价值主张在首屏、属性在下一层](https://www.shopify.com/blog/11863377-30-beautiful-and-creative-ecommerce-website-designs)
3. **Graza**<br>
   - 视觉摘录：[I Love Creatives 的公开站点截图](https://ilovecreatives.com/internet-gem-websites/graza)<br>
   - 案例 / 结构分析：[Shopify：色彩、烹饪场景、mini cart 与套装/订阅选择](https://www.shopify.com/blog/11863377-30-beautiful-and-creative-ecommerce-website-designs)
4. **Vacation Inc.**<br>
   - 视觉摘录：[PR Daily 公开产品新闻图](https://www.prdaily.com/how-orange-gelee-sunscreen-made-a-comeback-with-retro-chic-flair/)<br>
   - 案例 / 结构分析：[Shopify / Sitebuilder Report：复古色彩、颗粒影像、极简产品页](https://www.shopify.com/blog/11863377-30-beautiful-and-creative-ecommerce-website-designs)
5. **Fenty Beauty**<br>
   - 视觉摘录：[Fenty Beauty 官方公开产品图](https://fentybeauty.com/)<br>
   - 案例 / 结构分析：[第三方 PDP 研究：粗体视觉、色号选择、利益导向信息](https://www.creativecorner.studio/blog/product-page-examples)
6. **Stanley Quencher**<br>
   - 视觉摘录：[AL.com 公开新闻产品图](https://www.al.com/shopping/2024/07/stanley-surprise-drops-2-new-quencher-tumbler-colors-indigo-and-seafoam.html)<br>
   - 案例 / 结构分析：[WiserNotify PDP 案例：图像 → 变体 → 价格 → 按钮](https://wisernotify.com/blog/product-page/)

## 运行

```bash
PYTHONPATH=/tmp/accio-deps python3 code/build_accio_online_casebook_v3.py
```

需要 `Pillow` 与 `python-pptx`。渲染源图位于 `assets/accio_online_case_research_v3/`，仅用于该研究型交付的低清引述与来源定位。
