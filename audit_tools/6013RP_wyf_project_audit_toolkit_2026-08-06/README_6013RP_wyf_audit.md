# 6013RP-wyf 项目全量清点工具

## 文件

- `run_6013RP_wyf_audit.ps1`：Windows PowerShell 一键入口
- `audit_6013RP_wyf.py`：核心只读审计脚本

## 推荐运行方式

把两个脚本复制到项目根目录：

```text
H:\cuhk-2025fALL\6013RP-wyf\
```

然后打开 PowerShell：

```powershell
cd "H:\cuhk-2025fALL\6013RP-wyf"
Set-ExecutionPolicy -Scope Process Bypass

.\run_6013RP_wyf_audit.ps1 `
  -ProjectRoot "H:\cuhk-2025fALL\6013RP-wyf" `
  -HashMode smart `
  -MaxHashGB 20 `
  -OpenReport
```

默认输出到：

```text
H:\cuhk-2025fALL\6013RP-wyf\_project_audit\YYYYMMDD_HHMMSS\
```

## 三种哈希模式

```powershell
# 推荐：关键文件、小文件和同尺寸重复候选
.\run_6013RP_wyf_audit.ps1 -HashMode smart

# 最完整：20 GB 阈值内全部文件
.\run_6013RP_wyf_audit.ps1 -HashMode all

# 最快：不计算 SHA-256
.\run_6013RP_wyf_audit.ps1 -HashMode none
```

## WSL 运行

把脚本放到例如：

```text
H:\cuhk-2025fALL\6013RP-wyf\audit_tools\
```

在 Ubuntu/WSL 中：

```bash
cd /mnt/h/cuhk-2025fALL/6013RP-wyf/audit_tools

python3 audit_6013RP_wyf.py \
  --root /mnt/h/cuhk-2025fALL/6013RP-wyf \
  --hash-mode smart \
  --max-hash-gb 20 \
  --verbose
```

## 可选依赖

基础清点只需要 Python 3 标准库。安装以下包后会获得更完整的 H5AD、图片和 PDF 元数据：

```powershell
py -3 -m pip install anndata h5py pillow pypdf
```

或者在项目 conda 环境中：

```bash
conda install -c conda-forge anndata h5py pillow pypdf
```

没有这些包时脚本不会失败，只会把相应检查标记为 `skipped`。

## 主要输出

- `00_AUDIT_SUMMARY.md`：总报告
- `01_file_manifest.csv`：完整文件清单和 SHA-256
- `07_duplicate_files.csv`：重复文件
- `09_python_syntax.csv`：Python 语法
- `10_R_syntax.csv`：R 语法
- `14_missing_path_references.csv`：疑似缺失引用
- `15_hardcoded_absolute_paths.csv`：硬编码 Windows/WSL 路径
- `18_single_cell_assets.csv`：单细胞与生信资产
- `19_manuscript_figure_assets.csv`：手稿、图件和补充材料
- `20_h5ad_metadata.csv`：H5AD 维度与关键槽位
- `21_image_metadata.csv`：图片像素与 DPI
- `23_expected_structure_check.csv`：项目角色检查
- `27_project_tree.txt`：目录树
- `30_audit_summary.json`：机器可读摘要
- `31_WORKFLOW_RECORD.md`：本次独立 workflow

## 回传方式

运行结束后，把最新的整个目录压缩：

```text
H:\cuhk-2025fALL\6013RP-wyf\_project_audit\YYYYMMDD_HHMMSS\
```

上传给我即可继续建立：

```text
原始输入 → metadata → 分析脚本 → 中间对象 → 统计表 → 主图/补图 → 手稿陈述
```

的全链路追踪矩阵。
