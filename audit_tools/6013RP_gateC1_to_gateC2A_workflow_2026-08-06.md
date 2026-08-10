# Workflow：Gate C1 → Gate C2A → Gate C2B1

## Gate C1（2026-08-06）

**判定：PASS**

- 权威输入 SHA256：
  `fbd4692e033a57412fcc9dfe761180a9e4bdae37c4fda8f5ecc2e28fde46371b`
- `raw/X` 可用，为非负整数原始计数。
- 生物学单位为 sample；donor 用于处理重复样本相关性；library 为技术单位。
- 53 个样本跨 processing cohort，可用于技术桥接诊断。
- 全局疾病比较缺乏 common support；cohort 4 为主要直接比较，cohort 3 为探索性比较。
- 冻结保守 hard-QC，先进行疾病盲法 smoke 测试。

## Gate C2A（2026-08-10）

**表示判定：GO**  
**双细胞判定：NO-GO for freeze**

20,000-cell smoke 证明 B-cell-specific 重建可恢复有意义的中性结构，并改善
技术混合；但均衡抽样先于 Scrublet，导致自动双细胞率异常，因此不得冻结
smoke 双细胞集合。

权威报告：

```text
phase17_v7/gateC2A/20260810_164012_smoke/16_GATE_C2A_DECISION.md
```

## Gate C2B-01（2026-08-10）

**判定：PASS**

- 从权威 `raw/X` 提取 150,402 个硬 QC 合格细胞。
- 30,172 个基因全部保留。
- 工作 AnnData 只含技术/层级字段，保护结局字段单独保存。
- 输出 SHA256：
  `DC3E96BCC53B52D5C53CC0515EE352DC414AE81340032108830408E06F244AD5`

## 当前门：Gate C2B1

对 88 个完整技术文库执行可断点续跑的 Scrublet 评分。自动调用只作为诊断，
在审查文库率、阈值、分数分布及混合谱系富集前不得删除细胞。

```powershell
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_6013RP_phase17_gateC2B1_full_doublets.ps1 `
  -ResumeRunDir "H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\gateC2B1\20260810_171000_full_library_doublets"
```

Gate C2B1 通过后，才进入全量未整合/Harmony 表示、重采样稳定性和中性状态冻结。
