# 6013RP-wyf Phase 17 Gate C2A smoke test

## 当前状态

Gate C2A 已于 2026-08-10 完成，运行目录为：

```text
phase17_v7/gateC2A/20260810_164012_smoke/
```

该阶段从权威 `raw/X` 抽取 20,000 个细胞，在不包含疾病结局字段的
AnnData 中完成 B-cell-specific HVG、PCA、未整合/Harmony 表示、UMAP、
Leiden 分辨率网格、标记模块和供者/样本/文库覆盖诊断。

## 正式判定

- 表示学习：**GO，进入全量 Gate C2B**。
- smoke 双细胞集合：**NO-GO，不得冻结或复用**。
- 细胞状态：仅为疾病盲法的临时结构，不是最终注释。
- 投稿：**NO-GO**。

完整判定见：

```text
phase17_v7/gateC2A/20260810_164012_smoke/16_GATE_C2A_DECISION.md
```

## 为什么 smoke 双细胞结果不能复用

均衡抽样发生在逐文库 Scrublet 之前，改变了每个文库的细胞组成。自动
预测的总体双细胞率为 15.0%，文库中位数为 14.8%，最高为 43.7%，17 个
文库超过 20%。因此，这些调用只能解释 smoke 表示，不能用于全量排除。

## 已完成的后续工作

全量硬 QC 原始计数对象已经建立并通过读取验证：

```text
phase17_v7/gateC2B1/20260810_171000_full_library_doublets/
04_full_raw_counts.h5ad
```

对象包含 150,402 个细胞和 30,172 个基因，工作元数据中没有 `disease`、
`disease_state` 或 `ct_cov`。

## 当前运行入口

不再需要 WSL。使用已验证的 Windows 环境 `sle-bcell-v7`，从项目根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_6013RP_phase17_gateC2B1_full_doublets.ps1 `
  -ResumeRunDir "H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\gateC2B1\20260810_171000_full_library_doublets"
```

该入口逐完整文库运行 Scrublet，并为每个完成的文库保存断点。运行结束后仍
必须人工核查分数、自动阈值、文库预测率和混合谱系标记，再决定细胞排除策略。
