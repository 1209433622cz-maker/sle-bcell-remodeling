# 6013RP-wyf 全量清点结果解读与下一阶段决策

- 审计时间：2026-08-06
- 输入：本地项目 `_project_audit\20260806_110542`
- 项目根目录：`H:\cuhk-2025fALL\6013RP-wyf`

## 1. 结论修正

本次本地全量清点证明，项目实际工作区比此前上传的 `6013RP-wyf.zip` 完整得多。此前压缩包仅包含 `00_project_management`、`01_manuscript` 和 `04_submission`，因此“缺少 Data、02_analysis、03_results 和 01–16 阶段脚本”的判断只适用于上传包，不适用于本地工作区。

本地工作区目前实际包含：

- `Data`：33 个文件，约 18.65 GB；
- `03_results`：215 个文件，约 2.37 GB；
- `02_analysis`：131 个文件，其中完整分析脚本序列已延伸至 `49_build_cover_letter.py`；
- 9 个 H5AD，总计约 19.23 GB；
- 210 个 Python 文件均通过语法解析。

因此，项目已经具备开展 Phase 17 原始对象和方法学重构的主要物质基础。下一步不需要重新寻找全部脚本，而需要确认计数层、样本层级和模型设计是否满足重跑要求。

## 2. 审计日志中不构成科学故障的项目

### Shell 的 14 个“syntax error”

全部来自 `04_submission\.artifact_work_supp_tables\node_modules`。Windows 版 `bash.exe` 收到 `H:\...` 路径时丢失反斜杠，导致“文件不存在”，并非 Shell 文件本身存在语法错误，更不是核心生信流程错误。

### PDF 的 wrong pointing object 提示

这是 PDF 解析器对部分对象偏移或交叉引用异常的容错提示。本次 `22_pdf_metadata.csv` 中 71 个 PDF 全部为 `ok`；231 张位图也全部为 `ok`。暂不构成投稿文件损坏证据，但最终投稿包仍应使用 Acrobat 或 Ghostscript 做一次标准化预检。

### 4,736 组重复文件

绝大多数来自两套 `node_modules`、历史投稿包和相同图件在结果目录、审阅包、投稿包中的复制。这主要是工作区卫生和体积问题，不代表分析结果相互矛盾。科学审计应按 SHA-256 建立“权威源文件—派生副本”的关系，而不是直接删除所有重复文件。

### 652 条缺失引用

静态正则把下载脚本中的目标文件名、打包脚本中的归档内路径、历史 cleanup manifest 和带反引号的说明文字也计入缺失引用，因此该数字明显高估。真正需要处理的是核心分析脚本在当前项目根目录下无法解析的输入，而不是历史记录中的已移动文件。

## 3. 当前真正的阻塞项

### H5AD 内部结构尚未审计

本次运行使用 `D:\bioinfor\python.exe`（Python 3.13），该环境没有 `anndata/h5py`，所以 9 个 H5AD 均只登记了文件名，未得到：

- `n_obs`、`n_vars`；
- `obs` 中 donor、sample、library、cohort、disease、SLEDAI、treatment 等字段；
- `X`、`raw/X` 和 `layers` 的含义；
- 是否存在原始整数计数；
- 是否保留 B-cell-specific PCA/UMAP 或仍沿用全 PBMC 降维；
- 重复 donor、纵向样本和多 library 的实际层级。

这是 Phase 17 启动前最重要的技术阻塞。

### 环境可重复性尚未闭环

项目存在 `02_analysis\environment.yml`，但当前 PowerShell PATH 中：

- `conda=NOT_FOUND`
- `Rscript=NOT_FOUND`
- `pandoc=NOT_FOUND`
- `quarto=NOT_FOUND`

这不意味着软件一定没有安装，而是当前审计进程没有找到。重跑前应固定一个项目环境，并输出 package lock/version report。统计分析如采用 edgeR、muscat、scCODA/sccomp，还需明确 R/Python 环境边界。

### 无 Git 仓库

项目根目录未检测到 `.git`。对于即将进行的全量重跑，建议先建立 Git，仅追踪代码、配置、紧凑结果和文稿；H5AD、原始数据、缓存和大表通过 `.gitignore` 排除。这样可以把旧 v6 与新 v7 严格隔离。

### 投稿工程缓存严重污染工作区

`04_submission` 有 11,975 个文件，其中约 10,657 个属于 cache/build；主要来自 `node_modules` 和 artifact-tool 构建目录。它们不应进入科学版本控制，也不应继续复制进审阅包或投稿包。

## 4. 下一阶段的正确顺序

### Gate A：生成 H5AD 深度审计

运行本工具包中的：

```powershell
.\run_inspect_6013RP_h5ad_deep.ps1 `
  -ProjectRoot "H:\cuhk-2025fALL\6013RP-wyf"
```

输出应上传整个：

```text
H:\cuhk-2025fALL\6013RP-wyf\_phase17_h5ad_audit\YYYYMMDD_HHMMSS\
```

### Gate B：生成紧凑科学审阅包

运行：

```powershell
.\run_build_6013RP_phase17_review_pack.ps1 `
  -ProjectRoot "H:\cuhk-2025fALL\6013RP-wyf"
```

脚本会纳入代码、手稿、紧凑结果表、图件、关键 metadata、最新 QC 与审计结果，并排除 H5AD、原始归档、node_modules、缓存和巨大逐细胞表。最终只需上传生成的 ZIP。

### Gate C：开展方法与证据链审计

收到 Gate A 和 Gate B 输出后，下一轮将完成：

1. 逐脚本重建真实分析 DAG；
2. 核查 B-cell subset 是否从原始计数重新标准化、选 HVG、PCA、邻居图、聚类和 UMAP；
3. 检查标签定义是否使用 disease 信息导致循环推断；
4. 核查 donor/sample/library/cohort 的统计独立单位；
5. 区分“状态身份 pseudobulk”与“状态内 SLE-vs-HC pseudobulk”；
6. 为 scCODA/sccomp 和 edgeR/muscat 设计实际输入表与公式；
7. 建立每张主图面板对应的输入、脚本、统计表和手稿句子；
8. 决定哪些分析必须重跑，哪些现有结果可作为敏感性或补充材料保留。

## 5. 当前投稿判断

本地完整性比上传包所显示的情况明显更好，但尚不能据此恢复“直接投稿”路线。当前更准确的状态是：

> **数据与脚本资产基本齐备；方法学和样本层级真实性尚未完成原始对象级验证。**

因此，v6 继续作为冻结基线；Phase 17 先通过 H5AD 和紧凑证据包两道 gate，再进入 v7 重跑。
