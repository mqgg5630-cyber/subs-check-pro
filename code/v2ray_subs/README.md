# code/v2ray_subs：subs-check-pro → 本机桌面 → v2rayN 分组

这是沙箱与本机之间的一条流水线，通过 git-sync 值守执行（本机 `watch.ps1` 每 2 分钟拉取一次分支）。

## 组成

| 文件 | 作用 |
|---|---|
| `local_run.ps1` | 本机入口（`sync.config.json` 的 `check_cmd`）。按 `results/v2ray_subs/mode.txt` 切换模式 |
| `results/v2ray_subs/mode.txt` | `probe` = 只读体检；`run` = 完整流水线（subs-check-pro 检测 → 桌面 → v2rayN） |
| `tools/arena-sync/poller.sh` | 沙箱侧自动 pull/push 轮询（每 120 秒，只提交白名单目录，不切分支、不杀进程） |

## 数据去向（重要）

- **节点列表、订阅内容、subs-check-pro 工作目录** 只放在本机：桌面 `v2ray-subs-<时间>\` 与 `%LOCALAPPDATA%\subs-check-pro-d2a66b2d\`，**不进 git**。本仓库是公开 fork。
- git 里只有：体检报告 `probe_*.txt`、回执 `RECEIPT*`、值守日志 `check_r*.txt`。这些文件里不写节点链接、不写 Windows 用户名（自动替换为 `<user>`）。

## 安全与边界

- 公开免费节点不可信：可能记录流量、很快失效。导入后建议不要把它设为系统默认节点，不要用它登录敏感账户。
- 导入只新增一个分组（名称固定），**不自动切换活动节点、不修改系统代理**。
- 不会结束、重启或修改其他值守任务（本机注册用 `watch.ps1 -Register -KeepOthers`）。
