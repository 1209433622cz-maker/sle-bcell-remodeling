# 行动记录：Figure 1 identity-boundary 来源重绘与科学重冻结

- **完成日期：** 2026-09-02
- **最终状态：** `SCIENTIFIC_FIGURE1_BOUNDARY_PROMOTION_REFREEZE`
- **工作边界：** 手稿文本与图件科学表达；未推进投稿包、GitHub Release 或 Zenodo
- **冻结投稿包 SHA-256：** `02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1`

## 1. 本轮问题与独立裁决

外部 hostile audit 指出：当前标题、摘要与 Results 的关键转折是 fixed representation 下 broad scaffold 通过，但 end-to-end reconstruction 时 B_ASC state overlap 未满足预设 0.95 criterion；旧 Figure 1b-d 却全部呈现 fixed-representation 证据，导致最重要的边界只出现在 Supplementary Figure S4。

独立复核同意这一信息层级缺陷，但没有直接采用外部候选 PNG。最终裁决为：Figure 1a、1b 保留科学职责；旧 1d 的 fixed-representation state-Jaccard summary 移至新 1c；旧 1c 的逐次 ARI/agreement 退出主图但完整 Source Data 保留；新 1d 从哈希锁定的 S4 Source Data 重算 end-to-end minimum/median Jaccard。Figure 2-5 与 S1-S10 全部保持冻结。

## 2. 来源与数值核验

- 旧 Figure 1 Source Data SHA-256：`F3D45F72422B8469F7DD0A6E888541075A1D090277E9F96D16565B5B44C5B805`。
- Supplementary Figure S4 Source Data SHA-256：`46EE840F86CA33AA4F5FCE0A37EEFCB4DB23831533BBFA20400BAE50744F5D42`。
- 外部候选的 8 个 Jaccard 汇总值均由仓库冻结来源独立重算并在 1e-12 容差内一致。
- Fixed representation：B_CONV minimum/median = 0.999832/0.999925；B_ASC = 0.981096/0.991371。
- End-to-end reconstruction：B_CONV minimum/median = 0.998760/0.999363；B_ASC = 0.871750/0.930323。
- 没有重跑统计模型、没有改变阈值、没有产生新的生物学估计。

## 3. 图件重绘与子图裁决

- Figure 1a：`KEEP`，保持 identity adjudication 先于 disease-field join 的工作流职责。
- Figure 1b：`KEEP`，保持 candidate policy selection 职责。
- Figure 1c：`KEEP_RELOCATED`，成为 fixed-representation overlap criterion met 的唯一主图 owner，并保留 5/5 B_ASC marker support 与 minimum sample support 1.00。
- Figure 1d：`SOURCE_REPLACEMENT`，直接呈现 end-to-end B_ASC median 0.930 与 minimum 0.872 未满足 0.95 criterion。
- c/d 使用相同 x 轴范围与相同 marker 语义，允许读者直接比较 fixed 与 end-to-end reconstruction。
- S4 五个面板完整保留，继续拥有 20 次逐次诊断、boundary exchange、composition propagation 与 IFN propagation。
- 45 个图件/Source Data 资产中仅 Figure 1 PDF、PNG 与 Figure 1 Source Data 三项改变；其余 42 项哈希不变。

## 4. 手稿同步

仅执行三项来源级操作：fixed-representation 结果交叉引用从 Fig. 1a-d 收窄到 Fig. 1a-c；end-to-end boundary 首次锚定 Fig. 1d 与 Supplementary Fig. S4；Figure 1c/d legend 按新职责重写。Title、Abstract、Discussion、Conclusion、Figure 2-5 legends、Supplementary Information、参考文献与全部科学数字保持不变。

## 5. 文档与回归 QA

- Figure 1：170.0 mm 单页 PDF，SHA-256 `E81D2167F09B91FAF6FBA388D645EC002674721EF0139C498045B7AA96998397`；600-dpi PNG SHA-256 `00F4E8760907494539FBFB7D3E1B292A332A9C71868BC749792FACDB8BBC4776`。
- WPS 主文：31 页，SHA-256 `EADCB937DCD58C198D285D729B20A08F69411CA4A0EDA183B5A5F6BB6D629001`。
- LibreOffice 主文：31 页，SHA-256 `BA21836890D4602F2E8040F1A4AB25DCE6C629328BE859CCFD712BA59D3A4D77`。
- 双引擎共 62 页、12 张联系表已逐页视觉检查；无空白页、截断、重叠、缺字或异常分页。
- DOCX accessibility audit：0 high / 0 medium / 0 low。
- 全量回归：187/187 通过。
- 投稿包 SHA-256 保持不变。

## 6. 当前科学判断与下一阶段

本轮提升的是中心矛盾在主图中的可见性，而不是扩大结论。现在 Figure 1 自身形成完整链条：identity workflow -> policy selection -> fixed representation criterion met -> end-to-end B_ASC criterion not met。旧逐次 ARI/agreement panel 退出主图是合理的信息去重，其来源值仍完整保存；S4 则继续承担详细审计职责。

下一阶段进入 `FULL_MAIN_FIGURE_CLAIM_DENSITY_HOSTILE_READ`：不再主动重开 Figure 1 或扩展分析，转为全文 figure-to-text claim-density hostile read，重点只检查 Figure 2-5 是否存在与本轮类似的“核心边界未在主图第一视野出现”问题。只有发现可定位、可由冻结来源重绘解决的职责缺口时才重开单个 panel；否则回到科学呈现维护冻结。
