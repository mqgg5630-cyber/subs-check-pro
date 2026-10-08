# code/v2ray_subs：subs-check-pro → 本机桌面 → v2rayN 分组

这是沙箱与本机（Windows）之间的一条流水线，通过 git-sync 值守执行：本机 `watch.ps1` 每 2 分钟拉取一次本分支，运行 `check_cmd`（即 `local_run.ps1`），再把回执推回 git。沙箱无法直接访问本机，git 是唯一通道。

## 模式（`results/v2ray_subs/mode.txt`）

| 模式 | 作用 | 会改动什么 |
|---|---|---|
| `probe` | 只读体检：系统、v2rayN 进程与数据库、Python、端口、GitHub 与订阅源可达性 | 只写 `probe_*.txt` |
| `run` | subs-check-pro 检测默认订阅源 → 可用节点写入桌面**新文件夹** → v2rayN 新增**一个**订阅分组 | 桌面新文件夹；v2rayN 数据库新增一行（导入前自动备份） |
| `refresh` | 只读取最新交付的桌面文件夹，重新生成明文列表、README、清单（不检测、不导入、不新建文件夹） | 桌面该文件夹内的三个文件 |

当前 `mode.txt` 为 `probe`（只读）。需要重新导入时，把它改为 `run` 并发起新请求。

## 文件

| 文件 | 作用 |
|---|---|
| `local_run.ps1` | 本机入口（`sync.config.json` 的 `check_cmd`）。仅 ASCII（Windows PowerShell 5.1 按 ANSI 读取 .ps1） |
| `settings.json` | subs-check-pro 版本、官方下载地址、订阅源、分组名、超时等 |
| `v2rayn_import.py` | 导入助手（仅标准库）：备份 `guiNDB.db` → 写入 `SubItem` 一行 → 在 `127.0.0.1` 临时提供订阅 → 等待 v2rayN 拉取 → 关闭自动更新；失败则回滚 |
| `desktop_readme.txt` | 桌面 README 模板（UTF-8，中文） |

## 数据去向

- **节点与订阅内容只在本机**：桌面 `v2ray-subs-<时间>\`，工作目录 `%LOCALAPPDATA%\subs-check-pro-d2a66b2d\`。不进 git。
- git 里只有：体检报告 `probe_*.txt`、回执 `RECEIPT_*.json` 与 `RECEIPT_LATEST.json`、值守日志 `check_r*.txt`。
- 回执和日志不含节点链接；Windows 用户名会被替换为 `<user>`。

## 下载 subs-check-pro 的方式

- 官方 Windows 发布包（v3.5.0），SHA256 与官方校验文件比对，不匹配则失败。
- 先直连 GitHub。直连失败时，经过**本机已在运行的 v2rayN HTTP 入口**（10809 或 10808）下载，仅用于本次下载；不改活动节点，不开启系统代理。
- 每条路线的结果写在回执的 `download` 字段里。

## v2rayN 导入

- 只新增一个分组，名称见 `settings.json` 的 `group_name`。不切换活动节点，不开启系统代理，不改动其他分组。
- 需要 v2rayN **正在运行**。脚本不会替你启动它，因为启动时它可能按你的设置开启系统代理。
- 导入后自动更新关闭（`AutoUpdateInterval = 0`）。同名分组会被复用并替换节点，不会重复建组。
- 数据库备份在 `%LOCALAPPDATA%\subs-check-pro-d2a66b2d\backup\`。

## 安全与边界

- 免费公开节点不可信：可能很快失效，也可能记录流量。socks 类节点通常是未加密的公开代理，不要用于登录、支付或传输敏感信息。
- 本流水线不会结束、重启或修改其他值守任务。本机注册用 `watch.ps1 -Register -KeepOthers`，不要用 `-Auto` 或不带 `-KeepOthers` 的注册。
- 公开仓库：体检报告里会出现本机的计划任务名（包括其他会话的任务名）和机器名。如果不希望这些信息公开，请把仓库改为私有。
