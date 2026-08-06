# 寻找公司

面向一级投资人初次拜访硬科技公司的 Codex Skill。输入公司名称后，Skill 会基于公开网络信息完成公司主体识别、技术与产品梳理、商业化阶段判断和证据分级，并生成一份适合会前快速阅读的中文 HTML。

## 核心能力

- 确认公司品牌、法定主体、官网、总部与成立时间，避免同名主体混淆
- 检索产品、技术路线、团队、融资、客户、专利、招聘、竞争和风险信息
- 区分“已证实”“公司自述”“分析判断”“未确认”四类证据状态
- 输出公司画像、核心技术、工程化与商业化进展、竞争位置和待确认事项
- 固定生成恰好 3 个定制交流话题和 5 个关键问题
- 生成自包含、带来源链接、可打印的 UTF-8 中文 HTML

## 安装

在 PowerShell 中运行：

```powershell
gh repo clone XIAO-GOD/find-companies "$env:USERPROFILE\.codex\skills\prepare-hardtech-company-visit"
```

重新打开 Codex，或启动一个新任务，让 Codex 重新发现本地 Skill。

## 使用示例

直接告诉 Codex 公司名称和拜访目的，例如：

```text
帮我准备初次拜访原粒半导体，生成公司画像、3个交流话题和5个关键问题。
```

默认输出是一份中文 HTML 拜访简报。它服务于初步了解与是否继续跟进的判断，不替代完整的财务、法律、专利或客户尽调。

## 目录结构

```text
SKILL.md                         Skill 主流程
agents/openai.yaml               Codex 展示与调用元数据
references/research-guide.md     公开信息检索与证据规范
references/output-schema.md      结构化数据契约
scripts/render_brief.py          HTML 校验与渲染器
```

## 输出原则

研究遵循以下因果链：

```text
技术指标 → 稳定产品 → 客户验证 → 采购理由 → 可复制交付 → 壁垒 → 下一阶段里程碑
```

公开信息不足时，Skill 会明确展示未知项，不会补写未经证实的收入、估值、客户、订单、良率、性能或市场份额。

## 环境要求

- Codex
- Python 3，用于运行确定性 HTML 渲染器
- 可访问公开网页的研究工具或网络环境

## 许可

当前仓库未附加开源许可证，保留全部权利。
