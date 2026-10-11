# 安装、连接与登录

## 运行位置

推荐 Python CLI、Bridge、Chrome 在同一台可信电脑运行。不是无头服务器自带登录，也不是连接旧 MCP 服务：必须在用户要使用的 Chrome 配置中加载本扩展。服务端环境里已有 Cookie 不证明桌面 Chrome 已连接。

需要 Python 3.11+、Chrome，以及 `runtime/requirements.txt` 中的依赖。用隔离环境，不改系统包：

```bash
cd <本 Skill 的绝对目录>
python3 -m venv runtime/.venv
runtime/.venv/bin/python -m pip install -r runtime/requirements.txt
```

在 Chrome 打开 `chrome://extensions`，开启开发者模式，选择“加载已解压的扩展程序”，选择本 Skill 的 `runtime/extension` 目录。使用已有登录的小红书标签页；多账号须先指定目标，不能自动选一个账号试探。

操作时该 Chrome 配置中只保留一个目标小红书/创作者标签页；多个匹配页会报歧义并停止，不自动选第一个或关闭用户标签页。

启动 Bridge（前台运行，Ctrl+C 结束）：

```bash
runtime/.venv/bin/python runtime/scripts/bridge_server.py
```

另一个终端检查：

```bash
runtime/.venv/bin/python scripts/xhs.py status
runtime/.venv/bin/python scripts/xhs.py check-login
```

`status` 不打开 Chrome、不创建后台服务、不导航、不检测账号；`check-login` 会访问授权会话，必要时返回本地二维码。用户扫码后 `wait-login --timeout 30` 检查，或直接在浏览器正常登录。不在聊天里收集短信码；短信流程由用户在网页完成。二维码属于临时认证材料，不进入仓库、公共链接或第三方解码服务。

Bridge 只监听 localhost:9333，拒绝普通网页 Origin，只允许本地 CLI 和 Chrome 扩展 Origin。同机进程仍被信任，不能用于不可信多用户主机；它不是具有独立鉴权的远程 API。不要暴露 9333 到公网。命令失败不会自动启动浏览器或其他服务。

若 Agent 和 Chrome 在不同机器，应先说明这个部署差异。可将本 Skill 复制到 Chrome 所在电脑本地运行；不要默认开放远程调试端口。只有明确授权并了解本地信任边界后才设计 SSH 回环隧道。上传路径必须在 **Chrome 所在机器** 存在，远端 CLI 上的路径不等于本地可上传文件。

结束会话：停止自己启动的 Bridge 即可断开操作通道，扩展可能重连但不会自行发起业务操作。无需退出账号；停用/移除扩展由用户决定。已有服务不擅自终止。
