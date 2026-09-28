# human-writing 吸收范围与来源

来源：[KKKKhazix/human-writing](https://github.com/KKKKhazix/human-writing)，版本 1.1.0，读取提交 `4fda173f3fef7fb808f3eba991eeb2528ea4b189`。本次完整阅读 README、CHANGELOG、Skill 入口、五份参考、蒸馏版、检查脚本、版本与许可；封面和安装包装不影响写作行为。

这里记录思想的对应位置与适配理由，不是写作时必须加载的另一套流程。原仓库更新后可据此核对差异。

| 来源 | 吸收的判断 | 本地落点 |
| --- | --- | --- |
| README、SKILL、dist 蒸馏版 | 材料先于口气；现实、虚构、混合分流；说话位置；只交付所需成品 | `../SKILL.md`、`material-and-voice.md` |
| forum-prose | 面向具体读者；按局部问题推进；背景按需出现；细节有作用；允许有效岔话、重复和诚实修正 | `material-and-voice.md`、`style-guide.md` |
| forum-prose 的词序与节奏 | 尽早交代主干，沿动作接话，照应清楚，长短随内容，白话与古意匹配场合 | `style-guide.md` |
| reality | 来源身份、亲历边界；人物先后与因果动机分开；产品发布阶段；行业角色、成本和责任；数字后的具体影响 | `material-and-voice.md`、既有 `reasoning-guide.md` |
| fiction | 人物目标与选择、场景变化、对白目的、视角知识、世界规则、场景与概述、留下后果的结尾 | `narrative-and-formats.md` |
| formats | 问答、长帖、文章、人物、新闻、评论、个人叙事、短内容、教程、评测、口播、对白、诗歌按用途适配 | `narrative-and-formats.md` |
| revision、CHANGELOG 1.1 | 先保护声音；识别假具体、假口语、假深刻；从词面转向修辞动作；段落增量、冷读和结尾收束 | `revision-checklist.md` |
| check_prose.py | 只读定位、保护非正文、变形对照、名词化、同构句、重复与句长/连词统计 | 本地重写的 `../scripts/check_prose.py`、`../tests/test_check_prose.py` |
| agents/openai.yaml、VERSION | 识别来源版本及适用场景 | 保留现有 writing 名称、发现边界和调用方式，不另装重复 Skill |

## 有意转化的规则

- **材料门槛**：按作品承诺、信息量与推理增量判断，取消“1200 字至少五件材料”“不足就最多 600 字”和固定追问数。充分的单一来源或推导可以展开；无材料时仍不捏造。
- **禁词与标点**：冒号、破折号、对照、三项并列、拟人和术语按功能评价。真实纠错、专业用法、文学体裁和用户声音优先；逐字引文保持原样，不为避禁词改成假引语。
- **语气与结构**：不默认所有文章都是长帖。允许报告的摘要、教程的列表和诗歌的分行。保留语义优先、编辑档位、翻译模式及用户格式要求。
- **研究痕迹与来源**：不强制“我查了资料”的开场，不捏造查阅或认识变化；沿用上游来源及实际引用要求。是否需要引用取决于事实主张，不以“个人观点稿”一概免除。
- **节奏与删改**：不按配额删连词、制造长短句、压缩三分之一或执行七遍检查。按问题轻重改到任务满足，保护有用的重复和留白。
- **检测边界**：提示是待审位置，绝非硬失败；没有 AI 概率、总分、句长合格线或“清零才交稿”。上游统计阈值的普适性未验证，因此仅保留描述性统计，不据此判断作者身份。
- **覆盖方式**：将其他路标、黑话、抒情词、长定语、比喻换场、段尾金句与段落均匀度保留为上下文审阅，不复制长黑名单。扫描器只实现可定位的部分形状，详细误报边界写进输出与测试。
- **范围**：不增加默认外部发布、持久作者画像、必经审批或写作前全量参考加载。

## 许可

以下保留来源的许可声明，适用于吸收、改写的指导内容及检测思路；本地改写不代表上游维护者认可。

MIT License

Copyright (c) 2026 Human Writing Skill contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
