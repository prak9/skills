# 四个补充来源的吸收记录

这是可选的来源与维护记录，不是写作前必读的第四套规则。2026-09-28 读取公开仓库并固定到下列提交。

| 来源与提交 | 实际阅读范围 | 本地吸收位置 |
| --- | --- | --- |
| [Humanizer-zh](https://github.com/op7418/Humanizer-zh/tree/f4518a8eab97b8bfebc66a89d34320a89bef6930) | 入口全部 31 项及例子、README、CHANGELOG、测试说明、许可 | 主入口的材料指令边界；`editing-boundaries.md` 的未知施事者、归因与文件保护；保留原有按功能检查的风格规则 |
| [stop-slop](https://github.com/hardikpandya/stop-slop/tree/8da1f030185bdfe8471220585162991eaeb970e9) | 入口、phrases、structures、examples、README、CHANGELOG、许可 | 终稿检查中的铺垫、假对照、负面清单、戏剧化碎片、空泛重要性与责任主体；英语同样按含义处理 |
| [taste-skill](https://github.com/leonxlnx/taste-skill/tree/ce26fc25c0e5e8cab638f883de62d9a86ee5e45b) | README；主技能的 brief/dials、内容密度、引语、内容数据、营销文案、标点、重设计保护段落；完整 output 与 redesign 入口；许可 | 按受众与场景选择表达；`editing-boundaries.md` 的功能文案、真实数据、语气一致；交付完整与渐进修改。视觉实现、图片资产和全部研究附录未做写作迁移 |
| [shuorenhua](https://github.com/MrGeDiao/shuorenhua/tree/9e6400d5e2cc050485c38fbf0dda682bce66c180) | v2.5 入口、editing-guide、examples、README、评测运行说明与质量判据、许可 | 独有抽象命题、承诺与责任、否定作用域、来源处理、引用用途、局部范围及程序注释保护；正向收益与误改分别验证 |

## 取舍

共同目标是让读者更容易理解，同时保住作者说了什么。现有规则已覆盖的部分只建立映射，不复制几百条词表；新增内容进入按需参考。

- Humanizer-zh 的当前修订已经撤销机械标点和三项列举禁令，不能沿用其旧版印象。保留实际关系，正常稿可以原样返回。
- stop-slop 提供了有用的结构诊断，但不采用“所有副词都删”“每句必须有人作主语”“两项优于三项”、Wh 开头禁令、破折号禁令及 35/50 自评分门槛。其个别例子会改变范围或观点，不能当作保真示范；例如删掉 most 会扩大断言。
- taste 的审美服从 brief、先诊断再修改、每处文字有用途，可以迁移到写作。颜色、动效、字体、强制图片、固定字数和 dials 默认数值留在设计领域。其“用不规则数字显得真实”、随机日期、虚构客户姓名等示意设计建议不用于事实文案；真实数据优先，示例显式标明。引文也不因行数或破折号禁令改写。
- shuorenhua 对抽象信息和独有评价的保护值得保留，但不替换本地四档编辑体系，不增加约千字即锁段落的默认门槛。访谈讲话清理须有相应授权；证据性原话及用户要求逐字保留的内容保持原貌。保守到只复制问题稿也不算表达改善。
- 各来源的脚本、分数和发布门槛不自动变成本地验收。采用固定请求、匿名对照、独立判分、保留失败与复核记录；分别报告保真、任务完成、正常文本误改和正向改善。上游自报成绩不代表本地复现，单次同模型偏好也不代表所有读者。
- 不安装上游重复 Skill，不执行其安装脚本，不添加模型、编辑器或发布依赖。没有导入外部研究结论或投资参数。

## MIT 许可与归属

以下声明保留四个来源的归属，适用于基于这些来源改写的指导思想与示例边界；本地取舍不代表原作者认可。

MIT License

Humanizer-zh: Copyright (c) 2026 歸藏

stop-slop: Copyright (c) 2025 Hardik Pandya

taste-skill: Copyright (c) 2026 Leonxlnx

shuorenhua: Copyright (c) 2026 MrGeDiao

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
