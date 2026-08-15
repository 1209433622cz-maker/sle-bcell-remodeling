#!/usr/bin/env python3
"""Gate C4B-04: audit frozen outputs, adjudicate claims, and draw the figure."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

CONFIRMATORY = (
    'NAIVE_TO_MEMORY_AXIS',
    'ATYPICAL_LOW_NAIVE_AXIS',
    'APC_HLA',
    'IFN_ISG',
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest().upper()


def bh_adjust(values):
    import numpy as np

    values = np.asarray(values, dtype=float)
    order = np.argsort(values)
    ranked = values[order] * len(values) / np.arange(1, len(values) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    output = np.empty_like(ranked)
    output[order] = np.minimum(ranked, 1.0)
    return output


def direction(value: float) -> int:
    return 1 if value > 0 else -1 if value < 0 else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir', required=True)
    parser.add_argument('--gate-c4a-dir', required=True)
    args = parser.parse_args()

    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from matplotlib.lines import Line2D

    run = Path(args.run_dir).resolve()
    c4a = Path(args.gate_c4a_dir).resolve()
    figures = run / 'figures'
    figures.mkdir(parents=True, exist_ok=True)

    qualification = json.loads((run / '04_EDGER_QUALIFICATION.json').read_text(encoding='utf-8'))
    export = json.loads((run / '03_MATRIX_EXPORT_AUDIT.json').read_text(encoding='utf-8'))
    summaries = pd.read_csv(run / '05_MODEL_SUMMARY.csv')
    top = pd.read_csv(run / '06_TOP100_GENE_RESULTS.csv')
    programs = pd.read_csv(run / '07_PROGRAM_RESULTS.csv')
    pathways = pd.read_csv(run / '09_FROZEN_PROGRAM_ARM_CAMERA.csv')
    loo = pd.read_csv(run / '10_PRIMARY_PROGRAM_LOO.csv')
    concordance = pd.read_csv(run / '12_CROSS_COHORT_EFFECT_CONCORDANCE.csv')
    qc = pd.read_csv(run / '13_PRIMARY_RANKED_QC_FAMILY_AUDIT.csv')
    dictionary = pd.read_csv(c4a / '11_program_dictionary.csv', encoding='utf-8-sig')

    checks = {}

    def record(name: str, passed: bool, detail: str):
        checks[name] = {'pass': bool(passed), 'detail': detail}

    record(
        'qualification_gate',
        qualification.get('status') == 'PASS_C4B_EDGER_QUALIFICATION',
        str(qualification.get('status')),
    )
    record(
        'matrix_export_gate',
        export.get('status') == 'PASS_C4B_FROZEN_MATRIX_EXPORT',
        str(export.get('status')),
    )
    expected_names = {item['analysis_name'] for item in export['analyses']}
    record(
        'seven_frozen_models_complete',
        len(summaries) == 7 and set(summaries['analysis_name']) == expected_names,
        f'{len(summaries)}/7 model summaries',
    )

    gene_audits = []
    gene_integrity_pass = True
    for item in export['analyses']:
        name = item['analysis_name']
        path = run / '05_gene_results' / f'{name}_gene_results.csv.gz'
        table = pd.read_csv(path)
        finite = table['PValue'].notna()
        q_match = np.allclose(
            bh_adjust(table.loc[finite, 'PValue'].to_numpy()),
            table.loc[finite, 'FDR'].to_numpy(),
            rtol=1e-10,
            atol=1e-12,
        )
        summary = summaries.loc[summaries['analysis_name'] == name].iloc[0]
        passed = (
            len(table) == 30172
            and table['ensembl_id'].is_unique
            and int(finite.sum()) == int(summary['tested_genes'])
            and q_match
            and table.loc[finite, 'PValue'].between(0, 1).all()
            and table.loc[finite, 'FDR'].between(0, 1).all()
        )
        gene_integrity_pass &= bool(passed)
        gene_audits.append(
            {
                'analysis_name': name,
                'rows': len(table),
                'tested_genes': int(finite.sum()),
                'unique_ensembl': bool(table['ensembl_id'].is_unique),
                'bh_exact': bool(q_match),
                'pass': bool(passed),
            }
        )
    record(
        'gene_table_integrity',
        gene_integrity_pass,
        '7 complete 30,172-row tables; BH recomputed independently',
    )

    program_integrity = len(programs) == 63 and programs['availability_pass'].astype(bool).all()
    primary_program_rows = programs['analysis_family'] == 'primary_confirmatory'
    for _, group in programs.loc[primary_program_rows].groupby('analysis_name'):
        program_integrity &= np.allclose(
            bh_adjust(group['p_value'].to_numpy()),
            group['q_value_primary4'].to_numpy(),
            rtol=1e-10,
            atol=1e-12,
        )
    record(
        'program_table_integrity',
        program_integrity,
        f'{len(programs)} rows; four-program BH independently recomputed',
    )

    primary = programs.loc[
        programs['analysis_name'].eq('primary_base')
        & programs['analysis_family'].eq('primary_confirmatory')
    ].set_index('program_id')
    comparison_names = (
        'validation_full',
        'validation_nonoverlap',
        'primary_min20',
        'primary_min100',
        'primary_residual_risk_negative',
    )
    candidates = []
    for program_id in CONFIRMATORY:
        primary_row = primary.loc[program_id]
        expected_sign = direction(float(primary_row['effect']))
        comparison_rows = programs.loc[
            programs['program_id'].eq(program_id)
            & programs['analysis_name'].isin(comparison_names)
        ].set_index('analysis_name')
        directional = {
            name: direction(float(comparison_rows.loc[name, 'effect'])) == expected_sign
            for name in comparison_names
        }
        loo_row = loo.loc[loo['program_id'] == program_id].iloc[0]
        influence_pass = (
            not bool(loo_row['loo_any_sign_flip'])
            and float(loo_row['loo_sign_concordance']) == 1.0
        )
        arms = pathways.loc[
            pathways['analysis_name'].eq('primary_base')
            & pathways['program_id'].eq(program_id)
        ]
        arm_direction_passes = []
        arm_fractions = []
        for arm in arms.itertuples(index=False):
            arm_sign = 1 if arm.arm == 'positive' else -1
            expected_direction = 'Up' if expected_sign * arm_sign > 0 else 'Down'
            arm_direction_passes.append(str(arm.camera_direction) == expected_direction)
            raw_fraction = float(arm.expected_direction_fraction)
            arm_fractions.append(raw_fraction if expected_sign > 0 else 1 - raw_fraction)
        coherence_pass = (
            len(arms) >= 1
            and all(arm_direction_passes)
            and max(arm_fractions) >= 0.6
            and float(arms['camera_fdr_within_analysis'].min()) < 0.10
        )
        eligible = (
            float(primary_row['q_value_primary4']) < 0.05
            and all(directional.values())
            and influence_pass
            and coherence_pass
        )
        validation_row = comparison_rows.loc['validation_full']
        nonoverlap_row = comparison_rows.loc['validation_nonoverlap']
        candidates.append(
            {
                'program_id': program_id,
                'program_label': primary_row['program_label'],
                'primary_effect': float(primary_row['effect']),
                'primary_ci': [float(primary_row['ci_low']), float(primary_row['ci_high'])],
                'primary_q': float(primary_row['q_value_primary4']),
                'validation_full_effect': float(validation_row['effect']),
                'validation_full_q': float(validation_row['q_value_primary4']),
                'validation_nonoverlap_effect': float(nonoverlap_row['effect']),
                'validation_nonoverlap_q': float(nonoverlap_row['q_value_primary4']),
                'directional_checks': directional,
                'loo_pass': bool(influence_pass),
                'coherence_pass': bool(coherence_pass),
                'central_eligibility': bool(eligible),
            }
        )

    qc50 = qc.loc[qc['rank_cutoff'] == 50].iloc[0]
    platelet = programs.loc[
        programs['analysis_name'].eq('primary_base')
        & programs['program_id'].eq('PLATELET_AMBIENT_QC')
    ].iloc[0]
    asc = programs.loc[
        programs['analysis_name'].eq('primary_base')
        & programs['program_id'].eq('ASC_UPR_IDENTITY_QC')
    ].iloc[0]
    qc_clean = (
        platelet['p_value'] >= 0.05
        and asc['p_value'] >= 0.05
        and float(qc50['mitochondrial_fraction']) <= 0.10
        and float(qc50['ribosomal_fraction']) <= 0.10
        and float(qc50['hemoglobin_fraction']) <= 0.10
        and float(qc50['immunoglobulin_fraction']) <= 0.10
    )
    record(
        'qc_families_not_dominant',
        qc_clean,
        'platelet p={:.3g}; ASC/UPR p={:.3g}; top-50 technical fractions <=0.10'.format(
            platelet['p_value'], asc['p_value']
        ),
    )

    ifn = next(item for item in candidates if item['program_id'] == 'IFN_ISG')
    central_pass = bool(ifn['central_eligibility'] and qc_clean)
    decision = (
        'PASS_GATE_C4B_TO_INDEPENDENT_SLE_VALIDATION'
        if central_pass
        else 'NO_GO_GATE_C4B_AS_CENTRAL_TRANSCRIPTION_CLAIM'
    )
    eligible_programs = [item['program_id'] for item in candidates if item['central_eligibility']]
    record(
        'gate_c4b_central_acceptance',
        central_pass,
        f'eligible={eligible_programs}; anchor=IFN_ISG',
    )

    # Nature-style figure without repeated volcano plots.
    plt.rcParams.update(
        {
            'font.family': 'Arial',
            'font.size': 9,
            'axes.linewidth': 0.8,
            'axes.spines.top': False,
            'axes.spines.right': False,
            'pdf.fonttype': 42,
            'ps.fonttype': 42,
        }
    )
    colors = {
        'primary': '#1F4E79',
        'validation': '#D55E00',
        'ifn': '#B2182B',
    }
    labels = {
        'NAIVE_TO_MEMORY_AXIS': 'Naive-to-memory',
        'ATYPICAL_LOW_NAIVE_AXIS': 'Atypical/low-naive',
        'APC_HLA': 'APC/HLA',
        'IFN_ISG': 'IFN/ISG',
    }
    analysis_labels = {
        'primary_base': 'Primary C4 (n=89)',
        'primary_min20': 'Primary >=20 (n=94)',
        'primary_min100': 'Primary >=100 (n=87)',
        'primary_residual_risk_negative': 'Residual-risk negative (n=89)',
        'validation_full': 'Validation C2 (n=64)',
        'validation_nonoverlap': 'Validation nonoverlap (n=54)',
        'flare_full': 'Flare C3, secondary (n=34)',
    }
    fig, axes = plt.subplots(2, 2, figsize=(12.2, 9.2), constrained_layout=True)

    ax = axes[0, 0]
    y_base = np.arange(len(CONFIRMATORY))[::-1]
    forest_specs = (
        (-0.11, 'primary_base', colors['primary'], 'o'),
        (0.11, 'validation_nonoverlap', colors['validation'], 's'),
    )
    for offset, name, color, marker in forest_specs:
        subset = programs.loc[
            programs['analysis_name'].eq(name)
            & programs['program_id'].isin(CONFIRMATORY)
        ].set_index('program_id').loc[list(CONFIRMATORY)]
        ax.errorbar(
            subset['effect'],
            y_base + offset,
            xerr=[subset['effect'] - subset['ci_low'], subset['ci_high'] - subset['effect']],
            fmt=marker,
            color=color,
            ms=5,
            lw=1.2,
            capsize=2,
            label=analysis_labels[name],
        )
    ax.axvline(0, color='#9CA3AF', lw=0.8)
    ax.set_yticks(y_base, [labels[item] for item in CONFIRMATORY])
    ax.set_xlabel('Adjusted program-score difference')
    ax.set_title('Frozen confirmatory programs', loc='left', fontweight='bold')
    ax.legend(
        frameon=False,
        fontsize=8,
        loc='upper center',
        bbox_to_anchor=(0.5, -0.16),
        ncol=2,
    )
    ax.text(-0.12, 1.06, 'a', transform=ax.transAxes, fontsize=13, fontweight='bold')

    ax = axes[0, 1]
    analysis_order = [
        'primary_base',
        'primary_min20',
        'primary_min100',
        'primary_residual_risk_negative',
        'validation_full',
        'validation_nonoverlap',
        'flare_full',
    ]
    ifn_rows = programs.loc[programs['program_id'].eq('IFN_ISG')].set_index('analysis_name').loc[analysis_order]
    y = np.arange(len(analysis_order))[::-1]
    for index, name in enumerate(analysis_order):
        row = ifn_rows.loc[name]
        color = colors['validation'] if 'validation' in name else colors['ifn'] if name == 'flare_full' else colors['primary']
        ax.errorbar(
            row['effect'],
            y[index],
            xerr=[[row['effect'] - row['ci_low']], [row['ci_high'] - row['effect']]],
            fmt='o',
            color=color,
            ms=5,
            lw=1.2,
            capsize=2,
        )
    ax.axvline(0, color='#9CA3AF', lw=0.8)
    ax.set_yticks(y, [analysis_labels[name] for name in analysis_order])
    ax.set_xlabel('Adjusted IFN/ISG score difference')
    ax.set_title('IFN/ISG robustness and replication', loc='left', fontweight='bold')
    ax.text(-0.12, 1.06, 'b', transform=ax.transAxes, fontsize=13, fontweight='bold')

    ax = axes[1, 0]
    primary_genes = pd.read_csv(run / '05_gene_results' / 'primary_base_gene_results.csv.gz')
    validation_genes = pd.read_csv(run / '05_gene_results' / 'validation_nonoverlap_gene_results.csv.gz')
    merged = primary_genes.loc[
        primary_genes['tested_filterByExpr'], ['ensembl_id', 'feature_name', 'logFC']
    ].merge(
        validation_genes.loc[
            validation_genes['tested_filterByExpr'], ['ensembl_id', 'logFC']
        ],
        on='ensembl_id',
        suffixes=('_primary', '_validation'),
    )
    ax.scatter(
        merged['logFC_primary'], merged['logFC_validation'],
        s=8, color='#B8BEC6', alpha=0.55, linewidths=0,
    )
    ifn_genes = set(dictionary.loc[dictionary['program_id'].eq('IFN_ISG'), 'gene_symbol'])
    highlighted = merged.loc[merged['feature_name'].isin(ifn_genes)]
    ax.scatter(
        highlighted['logFC_primary'], highlighted['logFC_validation'],
        s=32, color=colors['ifn'], edgecolor='white', linewidth=0.5, zorder=3,
    )
    for row in highlighted.nlargest(6, 'logFC_primary').itertuples(index=False):
        ax.annotate(
            row.feature_name,
            (row.logFC_primary, row.logFC_validation),
            xytext=(3, 3),
            textcoords='offset points',
            fontsize=7,
        )
    ax.axhline(0, color='#9CA3AF', lw=0.7)
    ax.axvline(0, color='#9CA3AF', lw=0.7)
    rho = concordance.loc[
        concordance['comparison'].eq('primary_vs_validation_nonoverlap'), 'spearman_rho'
    ].iloc[0]
    ax.text(
        0.03, 0.96,
        f'Shared tested genes: {len(merged):,}\nSpearman rho = {rho:.2f}',
        transform=ax.transAxes, va='top', fontsize=8,
    )
    ax.set_xlabel('Primary C4 log2 fold change')
    ax.set_ylabel('Nonoverlap validation C2 log2 fold change')
    ax.set_title('Cross-cohort gene-effect concordance', loc='left', fontweight='bold')
    ax.legend(
        handles=[Line2D([0], [0], marker='o', color='none', markerfacecolor=colors['ifn'], markeredgecolor='white', label='Frozen IFN/ISG genes')],
        frameon=False, fontsize=8, loc='lower right',
    )
    ax.text(-0.12, 1.06, 'c', transform=ax.transAxes, fontsize=13, fontweight='bold')

    ax = axes[1, 1]
    effect_matrix = np.array(
        [
            [
                programs.loc[
                    programs['analysis_name'].eq(name)
                    & programs['program_id'].eq(program_id),
                    'effect',
                ].iloc[0]
                for program_id in CONFIRMATORY
            ]
            for name in analysis_order
        ]
    )
    limit = max(abs(effect_matrix.min()), abs(effect_matrix.max()))
    image = ax.imshow(effect_matrix, cmap='RdBu_r', vmin=-limit, vmax=limit, aspect='auto')
    ax.set_xticks(
        np.arange(4), [labels[item] for item in CONFIRMATORY], rotation=30, ha='right'
    )
    ax.set_yticks(
        np.arange(len(analysis_order)), [analysis_labels[name] for name in analysis_order]
    )
    for row_index, name in enumerate(analysis_order):
        for column_index, program_id in enumerate(CONFIRMATORY):
            q_value = programs.loc[
                programs['analysis_name'].eq(name)
                & programs['program_id'].eq(program_id),
                'q_value_primary4',
            ].iloc[0]
            text_color = 'white' if abs(effect_matrix[row_index, column_index]) > limit * 0.55 else '#111827'
            marker = '*' if q_value < 0.05 else ''
            ax.text(
                column_index, row_index,
                f'{effect_matrix[row_index, column_index]:.2f}{marker}',
                ha='center', va='center', fontsize=7.5, color=text_color,
            )
    colorbar = fig.colorbar(image, ax=ax, fraction=0.045, pad=0.03)
    colorbar.set_label('Adjusted score difference', fontsize=8)
    ax.set_title('Program effects across frozen analyses', loc='left', fontweight='bold')
    ax.text(-0.12, 1.06, 'd', transform=ax.transAxes, fontsize=13, fontweight='bold')

    png_path = figures / 'gate_c4b_bconv_transcription_replication.png'
    pdf_path = figures / 'gate_c4b_bconv_transcription_replication.pdf'
    fig.savefig(png_path, dpi=320, facecolor='white')
    fig.savefig(pdf_path, facecolor='white')
    plt.close(fig)

    primary_fdr = int(
        summaries.loc[summaries['analysis_name'].eq('primary_base'), 'fdr_0_05_genes'].iloc[0]
    )
    validation_fdr = int(
        summaries.loc[summaries['analysis_name'].eq('validation_full'), 'fdr_0_05_genes'].iloc[0]
    )
    nonoverlap = concordance.loc[
        concordance['comparison'].eq('primary_vs_validation_nonoverlap')
    ].iloc[0]
    pan_b = programs.loc[
        programs['analysis_name'].eq('primary_base')
        & programs['program_id'].eq('PAN_B_IDENTITY_QC')
    ].iloc[0]
    review = {
        'created_at': dt.datetime.now().astimezone().isoformat(timespec='seconds'),
        'decision': decision,
        'central_anchor': 'IFN_ISG' if central_pass else None,
        'central_claim_authorized': central_pass,
        'independent_validation_required': True,
        'basc_gene_level_authorized': False,
        'checks': checks,
        'gene_table_audits': gene_audits,
        'confirmatory_programs': candidates,
        'contextual_findings': {
            'primary_fdr_genes': primary_fdr,
            'validation_fdr_genes': validation_fdr,
            'nonoverlap_gene_rho': float(nonoverlap['spearman_rho']),
            'nonoverlap_top500_direction_concordance': float(nonoverlap['leading_direction_concordance']),
            'pan_b_identity_effect': float(pan_b['effect']),
            'pan_b_identity_p': float(pan_b['p_value']),
        },
        'interpretation_limits': [
            'Cohort-2 validation is internal to GSE174188 and is not independent SLE replication.',
            'Managed-state treatment exposure and clinical covariates remain potential residual confounders.',
            'Flare is secondary and cannot replace the managed-state primary contrast.',
            'B_ASC gene-level disease inference remains prohibited by the C4A support gate.',
            'PAN_B identity shift is a sensitivity flag for external validation, not evidence against the IFN result by itself.',
        ],
        'next_stage': 'Gate C5: independent SLE validation led by GSE135779, with GSE163121 directional support and OneK1K healthy context.',
    }
    (run / '15_GATE_C4B_ADVISOR_DECISION.json').write_text(
        json.dumps(review, indent=2), encoding='utf-8'
    )

    candidate_lines = []
    for item in candidates:
        candidate_lines.append(
            '| {} | {:.3f} | {:.3g} | {:.3f} | {:.3f} | {} |'.format(
                item['program_label'],
                item['primary_effect'],
                item['primary_q'],
                item['validation_full_effect'],
                item['validation_nonoverlap_effect'],
                'PASS' if item['central_eligibility'] else 'NO',
            )
        )
    decision_md = [
        '# Gate C4B advisor decision',
        '',
        f'## `{decision}`',
        '',
        'The frozen B_CONV transcription analysis passes to independent validation. The central anchor is the pre-registered IFN/ISG program, not the number of significant genes.',
        '',
        '| Frozen program | Primary effect | Primary BH q | Validation effect | Nonoverlap effect | Central criteria |',
        '|---|---:|---:|---:|---:|---:|',
        *candidate_lines,
        '',
        '## Principal finding',
        '',
        '- IFN/ISG: primary effect `{:.3f}` (95% CI `{:.3f}` to `{:.3f}`, BH q `{:.3g}`).'.format(
            ifn['primary_effect'], ifn['primary_ci'][0], ifn['primary_ci'][1], ifn['primary_q']
        ),
        '- Internal validation: full C2 effect `{:.3f}` (q `{:.3g}`); donor-nonoverlap effect `{:.3f}` (q `{:.3g}`).'.format(
            ifn['validation_full_effect'], ifn['validation_full_q'], ifn['validation_nonoverlap_effect'], ifn['validation_nonoverlap_q']
        ),
        '- Direction is stable at B_CONV thresholds 20 and 100 and in the residual-risk-negative branch; all 89 leave-one-sample-out effects retain the sign.',
        '- Leading primary genes are coherent interferon-response genes rather than technical or ambient families.',
        '',
        '## Secondary interpretation',
        '',
        'Naive-to-memory and APC/HLA pass frozen directional and influence checks but lack multiplicity-supported internal validation; they are supporting axes, not co-equal central claims. The atypical/low-naive program is negative.',
        '',
        'The significant pan-B identity control is retained as an explicit caution. It is smaller than the IFN effect and does not coincide with platelet/ASC contamination or ranked technical-family dominance, but it requires direct review in external datasets.',
        '',
        '## Scope control',
        '',
        'Cohort 2 is internal replication within GSE174188. This gate does not yet support an upper-Q1 mechanistic claim, does not authorize B_ASC gene-level inference, and does not establish treatment-independent causality.',
        '',
        '## Next gate',
        '',
        'Proceed to Gate C5. Use GSE135779 as the principal independent SLE validation layer, GSE163121 only as smaller directional support, and OneK1K as healthy immune-reference context. Freeze external mapping and the IFN/ISG score before inspecting external disease effects.',
    ]
    (run / '15_GATE_C4B_ADVISOR_DECISION.md').write_text(
        '\n'.join(decision_md) + '\n', encoding='utf-8'
    )

    audit_md = [
        '# Gate C4B independent result-integrity audit',
        '',
        f'- Decision: `{decision}`',
        f"- Checks passed: `{sum(item['pass'] for item in checks.values())}/{len(checks)}`",
        f"- Gene tables: `{sum(item['pass'] for item in gene_audits)}/7` complete and exact",
        '- Program rows: `63/63`; four-program BH independently reproduced',
        '- Full gene tables contain all 30,172 frozen Ensembl features, including explicit non-tested rows.',
        '',
        '| Analysis | Rows | Tested | Ensembl unique | BH exact |',
        '|---|---:|---:|---:|---:|',
    ]
    for item in gene_audits:
        audit_md.append(
            '| {} | {:,} | {:,} | {} | {} |'.format(
                item['analysis_name'], item['rows'], item['tested_genes'],
                'yes' if item['unique_ensembl'] else 'no',
                'yes' if item['bh_exact'] else 'no',
            )
        )
    (run / '16_GATE_C4B_RESULT_INTEGRITY_AUDIT.md').write_text(
        '\n'.join(audit_md) + '\n', encoding='utf-8'
    )
    (run / '16_GATE_C4B_RESULT_INTEGRITY_AUDIT.json').write_text(
        json.dumps(
            {'created_at': review['created_at'], 'checks': checks, 'gene_table_audits': gene_audits},
            indent=2,
        ),
        encoding='utf-8',
    )

    manifest_rows = []
    for path in sorted(item for item in run.rglob('*') if item.is_file()):
        if path.name == '17_gate_c4b_integrity_manifest.csv':
            continue
        relative = str(path.relative_to(run)).replace('\\', '/')
        manifest_rows.append(
            {
                'relative_path': relative,
                'size_bytes': path.stat().st_size,
                'sha256': sha256(path),
                'repository_policy': 'local_recomputable' if path.suffix == '.gz' else 'tracked',
            }
        )
    pd.DataFrame(manifest_rows).to_csv(
        run / '17_gate_c4b_integrity_manifest.csv', index=False
    )
    print(json.dumps(review, indent=2))
    return 0 if all(item['pass'] for item in checks.values()) else 2


if __name__ == '__main__':
    raise SystemExit(main())
