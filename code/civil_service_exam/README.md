# 2027 国考职位表：本地文件接入与透明初筛

这个目录把现有的 Windows `watch.ps1` 值守链路与职位表分析连接起来。目标是让**一份被明确指定的本地 XLS 文件**在内容稳定后自动进入当前 Arena 分支；不会扫描桌面或上传同目录中的其他文件。

## 已配置的唯一输入

`skills/git-sync/sync.config.json` 的 `watched_uploads` 已限定为：

| 本地源文件 | Git 仓库目的地 | 回执 |
|---|---|---|
| `D:\桌面\zhiye\中央机关及其直属机构2027年度考试录用公务员招考简章.xls` | `results/civil_service_exam/source/中央机关及其直属机构2027年度考试录用公务员招考简章.xls` | `results/civil_service_exam/ingest_manifest.json` |

每轮值守在既有 `auto_pull` 成功后会：

1. 检查该**单一文件**是否存在、是否为普通文件，且在 2 秒内大小与修改时间保持不变；
2. 计算 SHA-256。若远端副本内容相同，不重复提交；
3. 先复制到仓库内的 `.partial` 临时文件，再核对源/副本哈希；
4. 原子式覆盖仓库目标文件，并写入不含绝对本地路径的 hash/大小/时间回执；
5. 交给既有 `auto_push` 推送到 `arena/d2a66b2d-subs-check-pro`。

因此，原始文件不会被移动、删除或改写。配置中的目的地必须是仓库内相对路径；`..` 和绝对目的地会被拒绝。

## 一次性启用步骤（Windows 本机）

现有长驻 `watch.ps1 -Loop` 在启动时读取脚本，所以它自动拉取到新代码后仍需**重启一次值守进程**来加载“精确文件接入”逻辑：

```powershell
cd <你的 subs-check-pro 本地克隆目录>
.\sync.ps1
.\watch.ps1 -Pause
.\watch.ps1 -Resume
.\watch.ps1 -Status
```

若任务本身未注册，再执行一次：

```powershell
.\watch.ps1 -Register
.\watch.ps1 -Status
```

状态回显或本机 `%LOCALAPPDATA%\git-sync\watch-<repo>.log` 中出现 `watched_upload: copied` 后，文件已经进入本地 Git 工作区；随后原有无交互 `auto_push` 会把文件和 `ingest_manifest.json` 推到当前会话分支。Arena 端轮询拉到该提交后即可分析。

> 不要用 `git add .`、`git clean`、`git reset --hard` 来处理上传；值守脚本已经限定了要复制的路径，其他本地内容应保持不动。

## 首次分析

安装 Excel 读取依赖（本机或 Arena 的隔离 Python 环境）：

```bash
python -m pip install -r code/civil_service_exam/requirements.txt
```

先复制模板为本机私有资料：

```text
code/civil_service_exam/profile.template.json
→ config/civil_service_profile.local.json
```

然后只填写你自己的公开资格/偏好字段，再运行：

```bash
python3 code/civil_service_exam/analyze_positions.py \
  --input 'results/civil_service_exam/source/中央机关及其直属机构2027年度考试录用公务员招考简章.xls' \
  --profile config/civil_service_profile.local.json
```

若只想先识别职位表列名和导出标准化表，不输入任何个人资料：

```bash
python3 code/civil_service_exam/analyze_positions.py --no-profile
```

默认输出位于 `results/civil_service_exam/local_analysis/`，该目录被 `.gitignore` 排除，避免将个人偏好或本机分析结果自动推送。待职位表到达 Arena 后，可在对话中给出你的必要资格与岗位偏好，我会在仓库中单独生成可审计的候选清单。

## 输出与边界

脚本输出：

- `all_positions_normalized.csv`：原始公开职位表字段 + 识别出的标准字段 + 每项判断依据；
- `shortlist.csv`：非“初筛不匹配”的审查队列，按透明偏好分排序；
- `manual_review.csv`：专业目录、学历、政治面貌、应届、基层经历等需要人工核验的条目；
- `preliminary_ineligible.csv`：仅根据可机械匹配的文字得出的不匹配提示；
- `selection_report.md`：来源表、列识别和前 20 条候选的可读摘要。

这是一套**初筛与偏好排序**工具，不是官方资格认定，也不会预测上岸概率。特别是专业目录、应届身份、基层经历、服务项目及备注条款必须回到正式招考公告逐条核对。程序不会推断或据敏感身份特征做排序；可选的政治面貌字段只用于用户本人核验职位表中明确写出的资格条件，并且本机 profile 不应提交到 Git。
