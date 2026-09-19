# Single-note login recovery

Use this branch when a public note resolves to an ordinary login page and the preferred logged-in Xiaohongshu MCP route in `../SKILL.md` is unavailable or cannot retrieve the note. Check MCP availability before proposing a separate browser or requesting account access; an anonymous login redirect does not establish MCP login state. This is distinct from captcha or risky-IP restrictions, which require stopping. Do not retry anonymously through the login `redirectPath`: the ID/type in that target are diagnostic hints only.

## Authorization and runtime

Use an already applicable authorization for the user's own dedicated browser session; otherwise ask once whether to use it for this note. An explicit instruction to use the user's logged-in MCP authorizes that MCP route without another confirmation, but does not itself authorize a separate browser profile. Permission merely to edit this skill, or merely receiving a link, does not authorize opening that profile. Never request passwords, SMS codes or cookie values in chat. A configured profile alone is not permission.
