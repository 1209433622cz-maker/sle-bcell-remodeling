# Workflow：6013RP-wyf 项目清点脚本开发

- 日期：2026-08-06
- 目标项目：`H:\cuhk-2025fALL\6013RP-wyf`
- 任务：生成可在本地直接运行的全量、只读项目清点工具

## 已完成

1. 编写标准库优先的 Python 核心审计脚本；
2. 编写 Windows PowerShell 一键启动器；
3. 加入文件、目录、扩展名、体积和修改时间清点；
4. 加入 smart/all/none 三种 SHA-256 策略和重复文件识别；
5. 加入 Python、R、Shell 静态语法检查；
6. 加入脚本内文件引用、缺失路径和硬编码 Windows/WSL 路径扫描；
7. 加入单细胞数据、metadata、手稿、图件及补充材料专项资产表；
8. 加入 H5AD、Notebook、图片和 PDF 轻量元数据检查；
9. 加入 Git、环境信息、目录树和运行错误记录；
10. 每次实际运行时自动生成独立 `31_WORKFLOW_RECORD.md`。

## 设计原则

- 默认只读，不修改项目；
- 审计输出自动排除，避免递归扫描；
- 基础功能不依赖 pandas/anndata；
- 大文件哈希有上限，避免意外长时间占用磁盘；
- 输出同时兼顾人工阅读的 Markdown 与后续程序处理的 CSV/JSON；
- 为 Phase 17/v7 重跑建立可追踪的项目资产底图。

## 本地验证

开发包生成后执行：

```bash
python -m py_compile audit_6013RP_wyf.py
python audit_6013RP_wyf.py --root <临时测试目录> --hash-mode smart
```

应生成 `00_AUDIT_SUMMARY.md`、完整 CSV 索引和 workflow 记录。
