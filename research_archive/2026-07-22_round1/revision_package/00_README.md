# MOS² 重投稿修订包

## 推荐检查顺序

1. 打开 `04_original_vs_revised_marked_side_by_side.pdf`，左侧是第一次实际投稿 PDF，右侧是蓝色修改标记稿。
2. 对照 `06_complete_original_vs_revised_bilingual_audit.md`，逐项检查全部 69 段蓝色内容、原文、改后英文、中文含义和修改原因。
3. `02_bilingual_manuscript_change_audit.md` 是按审稿问题归纳的简版审计，可用于快速复核。
4. 打开 `manuscript/conference_101719_targeted_revision_marked.pdf` 检查完整蓝色标记稿。
5. 打开 `manuscript/conference_101719_targeted_revision_clean.pdf` 检查无标记净稿。
6. 审核 `01_response_to_reviewers_initial_draft.md` 中的逐条回信。
7. 查看 `05_publication_language_audit.md` 的正文过程性措辞扫描结果。
8. 根据 `03_remaining_manual_checklist.md` 完成投稿前人工确认。

## 目录结构

- `manuscript/`：第一次投稿基线、蓝色标记稿、无标记净稿及其 TeX/PDF。
- `figures/`：正文实际使用的 PDF 图件，以及按 `513×253` 参考尺寸重绘、待手工贴回 Fig. 2 的紧凑型进化优化面板。
- `data/`：Stage-II 五方法柱图的数值 CSV 与核验表。
- `spreadsheets/`：Stage-II 五方法数据、八张可编辑原生柱图和公式核验页组成的 Excel 工作簿。
- `evidence/`：小规模联合优化与真实区域泛化的回信证据和汇总 CSV。
- `code_repro/`：本轮图件、DQN、CLS 敏感性、联合优化和泛化实验的关键复现脚本。

## Overleaf 使用

正式无标记版本以

`manuscript/conference_101719_targeted_revision_clean.tex`

为主文件；审稿标记版本以

`manuscript/conference_101719_targeted_revision_marked.tex`

为主文件。`manuscript/` 已包含正文实际引用的全部 PDF 图件和 `IEEEtran.cls`，因此可作为一个自包含目录直接上传；`figures/` 另存一份用于分类检查。Fig. 2 的独立替换面板需要先按 `03_remaining_manual_checklist.md` 合入 Visio，再用最终导出的整图替换 `algo_0421.pdf`。

## 文件说明

- `conference_101719_first_submission.tex`：第一次投稿原始 TeX，不作覆盖。
- `conference_101719_first_submission_compile_only.tex`：仅移除算法包冲突和多余换行的本地编译副本，可见论文内容不变，不用于投稿。
- `conference_101719_targeted_revision_marked.tex`：修改内容显示为蓝色，满足编辑部要求。
- `conference_101719_targeted_revision_clean.tex`：已移除所有修改标记命令的正式净稿源码。

## 当前编译状态

- 第一次投稿编译副本：Tectonic 编译通过。
- 蓝色标记稿：Tectonic 编译通过，14 页。
- 无标记净稿：Tectonic 编译通过，14 页。
- `manuscript/` 自包含目录：独立编译通过。
- Fig. 1 已裁除最外围导出边框并保持单栏宽度；两组 Stage-II 柱图、Pareto 图和 DQN 正文页已逐页渲染检查。
- 左右对照版：已重新生成并完成视觉抽查。
