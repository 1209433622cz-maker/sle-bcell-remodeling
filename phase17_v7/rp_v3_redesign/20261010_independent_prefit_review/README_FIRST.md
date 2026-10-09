# SLE RP v3｜Stage 0B 独立复核与 WP1 效应前导出

## 先读结论

这是独立复核/准备包，不是 WP1 结果包，也不是 RP v3 的自动修订版。

- 最终 Stage 0B 清单 31/31 匹配。
- 五箱共同支持为 68/89 供体，尚未加入 A2 资格条件。
- A2 strong-ISG flags 为零，但保留 IFN12 中的 LY6E。
- A1 的 pi_ref 标准化算子与联合对比含义，需要在看 β 前记录。
- 已完成的仅为只读审计及新增组件测试；真实疾病系数和 bootstrap 均未运行。

`WP1_PREFIT_EXECUTION_ADDENDUM_DRAFT.md` 标注了需要审阅的定义，不得把其 PENDING 字段当成已经冻结。

## 内容

`action_record_...md`：详细科学与工程审查、执行边界和下一阶段。
`audit/`：38 个检查对象、共同支持成员、IFN 特征交集、两份清单的核验、环境、重复执行与组件测试记录。
`code/audit_stage0b.py`：可重复的附件只读审计。
`code/export_wp1_prefit.py`：从作者原工程导出最小原始计数充分对象；不拟合疾病效应。
`code/test_prefit_tools.py`：21 项新增小矩阵组件测试；不是原 Stage0B 的 6 项测试。
`received_contracts/`：上传包内关键合同/表格的原始字节，供审阅比对，不含大型诊断 H5AD。

原上传包和原工程均应保留。本包不覆盖旧版文档，不替换已冻结模型，不操作投稿、GitHub Release 或 Zenodo。

## 在原 Windows 工程上导出

依赖为 `numpy pandas scipy h5py`，现有 sle-bcell 环境通常是合适的入口，但此处没有替作者验证本地安装版本。必须从本包解压目录运行；下列输出目录必须尚不存在。

```powershell
conda run -n sle-bcell python .\code\export_wp1_prefit.py `
  --project-root 'H:\cuhk-2025fALL\6013RP-wyf' `
  --output 'H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\rp_v3_redesign\20261010_wp1_prefit_export'
```

程序预期使用原 counts/A0/design 的固定 SHA-256，并验证原 Stage 0B 最终清单。它不会自动下载、更换路径内容、删除旧结果或降低门槛。

成功时输出 `20261010_wp1_prefit_export.zip`。其中 A2 映射在读取疾病设计前被锁定；包含 A0/A2 每单位 IFN12 原始和、A1 每单位×箱原始和、完整原始库总计、单元格数、A1 支持、固定设计、T0/pi_ref 及校验和。它不决定 A1 算子，不计算 β，也不运行 2,000 次 bootstrap。

若异常，退出码为 2，并写出 `EXPORT_HOLD.json`。部分文件只能作为诊断，不得投入推断。不要修改冻结 gene means/SDs 或 thresholds 以让脚本通过；先查明版本、分母或 ID 对齐问题。

程序对 A1/T0 参数重现采用 1e-6 的数值容差，这是实现精度检查，不是疾病效应的等效性界限。A2 的 >=50 细胞条件仅作为继承原广义支架规则的候选支持诊断，必须在执行附录中明确其最终角色。

## 测试和只读审计

```powershell
python -m unittest discover -s .\code -p 'test_prefit_tools.py' -v
python .\code\audit_stage0b.py `
  --stage0b 'H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\rp_v3_redesign\20261009_stage0b' `
  --output '.\stage0b_readonly_audit_new_run'
```

独立审计脚本需要 Python 3.11+（使用 hashlib.file_digest），导出器使用流式 SHA-256，不依赖该接口。二者只读输入并要求新输出目录。

## 限制

导出器关键组件已在人工小矩阵通过测试；本会话没有原始发现队列 counts/A0，因此没有完成真实数据端到端导出。HDF5 raw X 不为 CSR、ID 不一致、归一化无法复现等均会显式停止，需要来源级审查，不保证任意环境均无修改可运行。

目前不得把本包当作 G2、WP1 完成、无组成混杂、IFN 完全独立、等效性或临床迁移的证明。
