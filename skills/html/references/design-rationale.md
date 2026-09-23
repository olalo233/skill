# 阅读样式的设计依据

用于维护资产，不要求每次生成文档都读取本文件。调色板是本地设计值，未引入组件库或复制第三方 CSS。

## 参考资料（2026-09-23 核对）

- [Anthropic frontend-design skill](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md)：围绕内容选择字体与层级；结构性装饰要有信息价值；避免把每段内容都装进相同卡片。
- [Refactoring UI](https://refactoringui.com/)：公开页面示例强调减少边框，用间距与表面层次组织内容。
- [Radix Colors: Understanding the scale](https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale)：区分背景、交互表面、边框和文字各自的颜色角色，明暗模式保留这些角色。
- [Andy Bell: My favourite 3 lines of CSS](https://piccalil.li/blog/my-favourite-3-lines-of-css/)：按内容流组织垂直间距，使排版规则可复用。

## 本地决策

主要用途是中文解释文档，不是营销首页。默认采用系统无衬线字体和中文回退，不依赖字体 CDN。标题通过字号、字重和段前间距组织层级；正文保持开放，不添加粗竖线或重复的整段外框。代码和图表可以有轻量背景。

文章侧栏可选；表格以横线区分行；引用采用轻量缩进。表单字体、内边距、圆角、键盘焦点由共享资产统一。暗色通过低对比边界和更亮的文字保持相同的信息顺序，避免每个区域都出现发亮的描边。

`.mb-flow` 是同一份 HTML 在桌面横排、手机纵排的简短流程组件。Canvas 使用实际容器宽度和设备像素比绘制，字号不随整个画布缩小。

继续沿用一套 DOM、布局和语义变量。未来生成时复制资产，不重新输出调色板。明确复刻现有网页或图片时，按 SKILL.md 的规则确认是否保留原样。

这些是解释文档的默认值。已有产品的视觉系统或用户明确指定的风格优先，不把这套阅读样式强加给所有网站。
