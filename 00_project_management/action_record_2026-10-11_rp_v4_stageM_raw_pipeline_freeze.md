# RP v4 Stage M 疾病盲原始计数流程冻结行动记录

**日期：** 2026-10-11
**阶段：** `RPV4_STAGE_M__RAW_RECONSTRUCTION_AUTHORIZATION_AND_DISEASE_BLIND_COUNT_PIPELINE_FREEZE`
**裁决：** `PASS_STAGE_M_DISEASE_BLIND_PIPELINE_AND_SIMULATION_FREEZE__HOLD_RUNTIME_STORAGE_AND_DOWNLOAD_AUTHORIZATION`

## 1. 本轮目的与授权边界

本轮按照 RP v4 继续推进，但没有把“一般性继续推进”解释为约 233 GB
SRA 下载授权。允许的工作仅包括：核对 Stage L、冻结 run-to-library
身份、固定参考基因组和计数流程、建立疾病盲执行输入、运行不含真实表达
结局的小样本模拟，以及判断当前主机是否具备后续执行条件。

本轮明确没有执行：SRA/FASTA/GTF 下载、FASTQ 转换、比对、真实整数计数
重构、RPKM 读取、active/inactive 表达比较、ATAC 整合、手稿外部结果写入、
投稿包、GitHub Release 或 Zenodo 更新。

## 2. 输入与来源复核

### 2.1 Git 与上游冻结状态

- 开始时本地 `main` 与 `origin/main` 均为
  `441cfd4a117d7708d2a05b74eab826f32a89c380`，工作区干净。
- Stage L 的 12 个 manifest payload 全部通过文件大小和 SHA-256 复核。
- Stage L 的科学问题保持不变：26 名 rN/T1T2 配对 SLE 患者中，比较
  active 与 inactive 的患者内 `T1T2 - rN` 冻结 IFN/ISG 分数差。

### 2.2 SRA RunInfo

权威文件为：

`phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze/source_metadata/PRJNA1093470_RunInfo.csv`

其 SHA-256 为：

`25f5a677e283d3f3dedf957699c8c56abfdb6e41aafc09b2fb36f054fe441ad0`

工作区内四个历史副本均为 95,173 bytes，SHA-256 完全一致。解析结果为：

| 对象 | 数量/总量 |
|---|---:|
| SRA runs | 176 |
| SRA experiments | 88 |
| BioSamples | 88 |
| GEO GSM libraries | 88 |
| 每个 GSM 的 runs | 2 |
| 总 bases | 752,698,793,704 |
| RunInfo 报告 SRA 体积 | 233,209 MB |

所有记录均为 human、ILLUMINA、paired-end、RNA-Seq、cDNA、TRANSCRIPTOMIC。
`LibraryName` 与 `SampleName` 对每条 run 一致；每个 experiment、BioSample
和 GSM 构成一对一映射。

### 2.3 已知身份异常的处理

`GSM8180322` 的 GEO title 为 `SLE.0.3621.rN`，而冻结的 MINiML patient-id
字段和配对关系将其归入患者 3651。该异常不是通过猜测“修正”title，而是
被写入永久规则：原始计数流程只使用 GSM/experiment/BioSample/run；患者
身份在计数与 QC 封存后，按 Stage L 冻结的 GSM 表连接，禁止解析 title。

## 3. 疾病盲执行对象

本轮生成：

- `02_DISEASE_BLIND_RUN_MAP.csv`：176 条 run，含技术身份、read/base/体积、
  SRA hash 和 FASTQ 路径模板；
- `03_LIBRARY_RUN_ACCOUNTING.csv`：88 个 GSM 的两 run 汇总；
- `04_NFCORE_SAMPLESHEET_TEMPLATE.csv`：176 行 nf-core technical-replicate
  输入，重复 GSM 自动在比对前合并。

这些文件不包含 patient ID、disease、SLEDAI、activity、cell type、sex、
race、treatment 或任何效应值。Stage L 样本表仅用于集合闭合和预设模拟
设计，不复制进原始计数执行表。

## 4. 参考资源与工作流冻结

### 4.1 参考资源

- Genome：GENCODE 50，GRCh38.p14 primary assembly FASTA；
- Annotation：GENCODE 50 comprehensive primary-assembly GTF；
- FASTA MD5：`da1a11258be075cfa7af718162c894e7`；
- GTF MD5：`289b91e5e95e8b0450d223246f10a12e`。

MD5 来自 GENCODE release 50 官方 `MD5SUMS`。本轮只读取小型 checksum
清单，没有下载 FASTA/GTF。

### 4.2 固定软件与参数

- SRA Toolkit 3.4.1；只允许 full-quality SRA normalized format，拒绝
  `.sralite`；
- `prefetch` 后必须 `vdb-validate`，再以 `fasterq-dump --split-files`
  转换并压缩；
- Nextflow 最低版本 25.10.4；
- nf-core/rnaseq 3.27.0，Linux x86-64 Docker profile，用于 STAR 比对、
  strandedness inference 和 QC，并保存 STAR BAM；
- Salmon 只承担 strandedness 支持和 secondary QC，不是整数计数 owner；
- Subread featureCounts 2.1.1 对每个 GSM 的 STAR BAM 运行
  `-p --countReadPairs -B -C -t exon -g gene_id`，再按冻结 GSM 顺序合并；
- 不做 trimming；对所有样本统一保留 raw QC；
- strandedness 固定为 `auto`，阈值为 0.8/0.1；
- 只允许同一 GSM 的两条 run 合并；
- 12 个冻结 IFN/ISG symbol 必须全部映射。annotation 缺失是技术失败，
  真实零计数仍为零。

采用成熟的 nf-core 工作流而不是临时手写比对/计数链，目的是将工具版本、
容器、技术重复合并、QC 和 provenance 置于一个可审计框架内。该选择在
看到任何外部表达结局之前完成。

## 5. 前瞻性小样本模拟

### 5.1 固定设计

- 独立单位：患者；
- n=26；active=12，inactive=14；
- 设计列：intercept、active indicator、RNA batch 3 indicator；
- 四个 activity-by-batch 单元：5/7/7/7；
- rank=3，residual df=23，condition number=3.094；
- 推断：OLS active coefficient、HC3 variance、双侧 t(23)。

### 5.2 模拟合同

固定 seed 为 20261011。六个零效应场景各 25,000 次：同方差正态、active
组四倍方差、batch 3 四倍方差、缩放 t(3)、中心化标准化 lognormal、5%
污染正态。两个替代效应场景（0.5、0.8）各 10,000 次，仅描述 power。

预先固定门槛：每个零场景 type-I error 不超过 0.075；每个场景 95% CI
coverage 不低于 0.925；绝对 bias 不超过 0.05。power 不参与方法选择。

### 5.3 模拟结果

| 场景 | rejection | coverage | bias |
|---|---:|---:|---:|
| N0 normal | 0.0384 | 0.9616 | 0.0006 |
| N1 active variance x4 | 0.0436 | 0.9564 | 0.0007 |
| N2 batch-3 variance x4 | 0.0383 | 0.9617 | 0.0018 |
| N3 scaled t(3) | 0.0328 | 0.9672 | 0.0005 |
| N4 lognormal | 0.0303 | 0.9697 | 0.0004 |
| N5 contaminated normal | 0.0364 | 0.9636 | -0.0016 |
| A1 effect 0.5 | 0.1966 | 0.9585 | -0.0021 |
| A2 effect 0.8 | 0.4472 | 0.9635 | 0.0070 |

所有预设门通过。该结果只说明当前固定设计下 HC3-t(23) 实现具有可接受的
合成运行特征；不证明真实外部效应存在，也不允许根据 power 更换模型。

## 6. 当前主机与存储审查

Windows PATH 中未找到 `prefetch`、`fasterq-dump`、`vdb-validate`、
`nextflow`、`docker` 或 `featureCounts`。WSL2 `Ubuntu-22.04` 存在且 Java
可用，但同样缺少上述工具和容器运行时。

| 位置 | 报告空闲空间 |
|---|---:|
| C: | 106.3 GB |
| D: | 99.4 GB |
| H: | 353.7 GB |
| WSL root virtual filesystem（仅诊断，不计作物理 scratch） | 986.8 GB |

即使采用最大的 WSL 报告值，也低于 2.5 TB；且 WSL sparse disk 的物理
后端空间不能按其虚拟上限视为真实可用空间。因此 runtime 和 storage 两门
均为 HOLD。

## 7. 完整性与验证

- 新增 Stage M 单元测试 6/6 PASS；
- 模拟两次运行逐对象一致，证明固定 seed 的确定性；
- 改动后的完整 RP v4 测试套件 87/87 PASS；测试集合同时包含旧式
  同目录导入和包式导入，因此统一入口显式将项目根目录与 `audit_tools`
  加入 `PYTHONPATH`，避免测试发现方式产生假阴性；
- Stage M 目录含 15 个受控 payload 和一份 SHA-256 manifest；
- unsigned Stage N 模板所有授权字段均为 false；
- `raw_download_started=false`、`expression_matrix_read=false`、
  `external_outcome_fitted=false`。

## 8. 科学判断

GSE262846 仍值得推进，但价值不在再次证明 SLE IFN 阳性，而在回答一个不同
的问题：同一患者 transitional 与 resting-naive B 细胞之间的冻结 IFN/ISG
差异是否随活动度改变。Stage M 已经关闭身份、流程与小样本估计器三类设计
风险。现在继续改变 score、mapper、annotation、QC cutoff 或协变量，只会
增加 outcome-guided 分析风险。

## 9. 下一阶段

下一阶段为：

`RPV4_STAGE_N__QUALIFIED_RUNTIME_STORAGE_AND_WRITE_ONCE_RAW_RECONSTRUCTION`

进入条件：

1. 指定真实可用、可写、至少 2.5 TB 的 scratch 路径；
2. 在 Linux x86-64 环境安装并记录 SRA Toolkit 3.4.1、Nextflow >=25.10.4
   和 Docker；
3. 完成工具版本、容器拉取、参考资源 MD5、磁盘和断点续跑小型 smoke test；
4. 两位作者共同签署 Stage N 模板中的下载、存储、固定流程、疾病盲和
   fail-closed 条件；
5. 只运行一次疾病盲 raw count reconstruction，先封存 88-library counts
   与 QC，再单独决定是否允许连接 Stage L 结局字段。

在这些条件满足前，不应启动 233,209 MB SRA 下载，也不应使用 RPKM 替代
整数计数门。
