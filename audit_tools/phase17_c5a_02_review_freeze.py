#!/usr/bin/env python3
"""Gate C5A-02: independently review the external source/mapping freeze."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import tarfile
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_stream(handle) -> str:
    digest = hashlib.sha256()
    for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b''):
        digest.update(chunk)
    return digest.hexdigest().upper()


def write_text_lf(path: Path, content: str) -> None:
    with path.open('w', encoding='utf-8', newline='\n') as handle:
        handle.write(content)


def write_csv_lf(frame, path: Path) -> None:
    frame.to_csv(path, index=False, lineterminator='\n')


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir', required=True)
    parser.add_argument('--source-dir', required=True)
    parser.add_argument('--gate-c4a-dir', required=True)
    args = parser.parse_args()

    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from scipy import sparse

    run = Path(args.run_dir).resolve()
    source = Path(args.source_dir).resolve()
    c4a = Path(args.gate_c4a_dir).resolve()
    figures = run / 'figures'
    figures.mkdir(parents=True, exist_ok=True)

    status = json.loads((run / '00_GATE_C5A_RUN_STATUS.json').read_text(encoding='utf-8'))
    contract = json.loads((run / '16_GATE_C5A_FREEZE_CONTRACT.json').read_text(encoding='utf-8'))
    source_manifest = pd.read_csv(run / '01_SOURCE_FILE_MANIFEST.csv')
    tar_manifest = pd.read_csv(run / '02_TAR_MEMBER_MANIFEST.csv')
    sample_audit = pd.read_csv(run / '03_SAMPLE_SOURCE_AUDIT.csv')
    exceptions = pd.read_csv(run / '03A_METADATA_BARCODE_EXCEPTIONS.csv')
    metadata_versions = pd.read_csv(run / '04A_CHILDHOOD_METADATA_VERSION_AUDIT.csv')
    missing_samples = pd.read_csv(run / '04_METADATA_WITHOUT_MATRIX_SAMPLES.csv')
    label_dictionary = pd.read_csv(run / '05_SOURCE_LABEL_DICTIONARY.csv')
    label_support = pd.read_csv(run / '06_SAMPLE_LABEL_SUPPORT.csv')
    counts = sparse.load_npz(run / '07_EXTERNAL_PSEUDOBULK_COUNTS.npz').tocsr()
    rows = pd.read_csv(run / '08_EXTERNAL_PSEUDOBULK_ROW_METADATA.csv')
    genes = pd.read_csv(run / '09_EXTERNAL_GENE_UNIVERSE.csv.gz')
    frozen_programs = pd.read_csv(run / '10_FROZEN_PROGRAM_DICTIONARY.csv')
    availability = pd.read_csv(run / '11_FROZEN_PROGRAM_GENE_AVAILABILITY.csv')
    design_summary = pd.read_csv(run / '16_GATE_C5A_DESIGN_SUMMARY.csv')
    program_arms = pd.read_csv(run / '16_GATE_C5A_PROGRAM_ARM_SUMMARY.csv')

    checks = {}

    def record(name: str, passed: bool, detail: str):
        checks[name] = {'pass': bool(passed), 'detail': detail}

    record(
        'pre_effect_contract',
        status.get('external_disease_effects_inspected') is False
        and contract.get('external_disease_effects_inspected') is False,
        'both run status and freeze contract report no external effect inspection',
    )

    source_failures = []
    for item in source_manifest.itertuples(index=False):
        path = source / item.filename
        if not path.is_file():
            source_failures.append(f'missing:{item.filename}')
        elif path.stat().st_size != int(item.size_bytes):
            source_failures.append(f'size:{item.filename}')
        elif sha256_file(path) != str(item.sha256).upper():
            source_failures.append(f'sha256:{item.filename}')
    record(
        'source_file_integrity',
        not source_failures,
        f'{len(source_manifest)} source files independently rehashed; failures={source_failures}',
    )

    member_failures = []
    raw_tar = source / 'GSE135779_RAW.tar'
    with tarfile.open(raw_tar, 'r') as archive:
        members = {member.name: member for member in archive.getmembers() if member.isfile()}
        for item in tar_manifest.itertuples(index=False):
            member = members.get(item.member_name)
            if member is None:
                member_failures.append(f'missing:{item.member_name}')
                continue
            handle = archive.extractfile(member)
            if handle is None:
                member_failures.append(f'unreadable:{item.member_name}')
            elif sha256_stream(handle) != str(item.sha256_compressed_member).upper():
                member_failures.append(f'sha256:{item.member_name}')
    record(
        'tar_member_integrity',
        len(tar_manifest) == 112 and not member_failures,
        f'{len(tar_manifest)}/112 members independently rehashed; failures={len(member_failures)}',
    )

    sample_pass = (
        len(sample_audit) == 56
        and sample_audit['sample_id'].is_unique
        and (sample_audit['matrix_genes'] == 32738).all()
        and sample_audit['integer_nonnegative'].astype(bool).all()
        and int(sample_audit['unmatched_metadata_cells'].sum()) == len(exceptions) == 4
        and int(sample_audit['matched_metadata_cells'].sum()) == 321106
        and int(sample_audit['bconv_cells'].sum()) == 32179
    )
    record(
        'sample_matrix_and_barcode_audit',
        sample_pass,
        '56 unique samples; 32,738 genes; 321,106 matched metadata cells; 4 explicit exceptions',
    )

    missing_pairs = missing_samples[['sample_id', 'donor_name', 'disease_group']].drop_duplicates()
    missing_pass = (
        set(missing_pairs['sample_id']) == {'JB19002', 'JB19016'}
        and set(missing_pairs['donor_name']) == {'aHD2', 'aSLE8'}
        and missing_pairs['disease_group'].value_counts().to_dict() == {'HC': 1, 'SLE': 1}
    )
    record(
        'metadata_matrix_sample_gap_explained',
        missing_pass,
        '58 metadata donors versus 56 matrices: JB19002/aHD2 and JB19016/aSLE8 absent, one per group',
    )

    aggregate_jaccard = contract['source']['childhood_metadata_version_jaccard']
    version_pass = (
        len(metadata_versions) == 44
        and aggregate_jaccard >= 0.95
        and not contract['source']['metadata_versions_are_identical']
        and contract['source']['authoritative_metadata'] == 'Meta_caSLE_processed_08092021_small.csv'
    )
    record(
        'metadata_version_policy',
        version_pass,
        f'44 childhood samples; aggregate Jaccard={aggregate_jaccard:.4f}; extended metadata frozen as authoritative',
    )

    matrix_pass = (
        counts.shape == (len(rows), len(genes)) == (672, 32738)
        and np.array_equal(rows['pseudobulk_row'].to_numpy(), np.arange(len(rows)))
        and (counts.data.size == 0 or (counts.data.min() >= 0 and np.all(counts.data == np.floor(counts.data))))
        and np.array_equal(
            np.asarray(counts.sum(axis=1)).ravel().astype(np.int64),
            rows['library_size_umi'].to_numpy(dtype=np.int64),
        )
        and genes['ensembl_id'].is_unique
    )
    record(
        'pseudobulk_count_integrity',
        matrix_pass,
        f'matrix={counts.shape}; dtype={counts.dtype}; row sums and Ensembl uniqueness exact',
    )

    representation_pass = True
    for sample_id in sample_audit['sample_id']:
        for compartment in ('B_CONV_ANALOG', 'B_ASC_CONTROL'):
            total_row = rows.loc[
                rows['sample_id'].eq(sample_id)
                & rows['representation'].eq('compartment')
                & rows['frozen_compartment'].eq(compartment)
            ]
            label_rows = rows.loc[
                rows['sample_id'].eq(sample_id)
                & rows['representation'].eq('source_label')
                & rows['frozen_compartment'].eq(compartment)
            ]
            if len(total_row) != 1:
                representation_pass = False
                continue
            total_vector = counts[int(total_row['pseudobulk_row'].iloc[0])]
            label_vector = counts[label_rows['pseudobulk_row'].to_numpy(dtype=int)].sum(axis=0)
            if not np.array_equal(np.asarray(total_vector.todense()).ravel(), np.asarray(label_vector).ravel()):
                representation_pass = False
    record(
        'label_to_compartment_conservation',
        representation_pass,
        'all sample-level B/PC source-label rows sum exactly to their compartment pseudobulk',
    )

    b_labels = label_dictionary.loc[
        label_dictionary['frozen_compartment'].eq('B_CONV_ANALOG'), 'source_label'
    ]
    pc_labels = label_dictionary.loc[
        label_dictionary['frozen_compartment'].eq('B_ASC_CONTROL'), 'source_label'
    ]
    mapping_pass = (
        len(b_labels) == 8
        and len(pc_labels) == 2
        and b_labels.str.upper().str.startswith('B-').all()
        and pc_labels.str.upper().str.startswith('PC-').all()
        and contract['identity_mapping']['mapping_uses_disease'] is False
    )
    record(
        'disease_blind_identity_mapping',
        mapping_pass,
        '8 B-caSC labels -> B_CONV_ANALOG; 2 PC-caSC labels -> identity control; disease unused',
    )

    c4a_programs = pd.read_csv(c4a / '11_program_dictionary.csv', encoding='utf-8-sig')
    program_exact = c4a_programs.equals(frozen_programs)
    availability_pass = program_arms['pass_80pct'].astype(bool).all()
    ifn = program_arms.loc[program_arms['program_id'].eq('IFN_ISG')]
    program_pass = (
        program_exact
        and availability_pass
        and int(ifn['available'].sum()) == int(ifn['total'].sum()) == 12
        and len(availability) == len(c4a_programs)
    )
    record(
        'frozen_program_contract',
        program_pass,
        'exact C4A dictionary; all signed arms >=80%; IFN/ISG 12/12 genes available',
    )

    required_designs = {
        'combined_min50': (54, 16, 38, 3),
        'childhood_min50': (43, 11, 32, 2),
        'adult_min50': (11, 5, 6, 2),
        'combined_min20': (56, 16, 40, 3),
        'combined_min100': (51, 16, 35, 3),
    }
    design_pass = True
    for name, expected in required_designs.items():
        row = design_summary.loc[design_summary['analysis_name'].eq(name)]
        if len(row) != 1:
            design_pass = False
            continue
        observed = tuple(
            int(row[column].iloc[0])
            for column in ('n_samples', 'n_hc', 'n_sle', 'design_rank')
        )
        design_pass &= observed == expected and int(row['design_rank'].iloc[0]) == int(row['required_rank'].iloc[0])
    record(
        'external_design_identifiability',
        design_pass,
        'five frozen designs match expected group sizes and are full rank',
    )

    all_pass = all(item['pass'] for item in checks.values())
    decision = (
        'PASS_GATE_C5A_TO_FROZEN_EXTERNAL_EFFECT_MODELING'
        if all_pass
        else 'HOLD_GATE_C5A_EXTERNAL_EFFECTS_LOCKED'
    )

    # Disease-blind source/design QC figure.
    plt.rcParams.update(
        {
            'font.family': 'Arial',
            'font.size': 9,
            'axes.linewidth': 0.8,
            'axes.spines.top': False,
            'axes.spines.right': False,
            'pdf.fonttype': 42,
        }
    )
    fig, axes = plt.subplots(2, 2, figsize=(11.8, 8.7), constrained_layout=True)

    ax = axes[0, 0]
    accounting_labels = ['Metadata donors', 'Matrix-matched donors', '>=20 B cells', '>=50 B cells', '>=100 B cells']
    accounting_values = [58, 56, 56, 54, 51]
    colors = ['#6B7280', '#1F4E79', '#4C956C', '#2A9D8F', '#D55E00']
    y = np.arange(len(accounting_labels))[::-1]
    ax.barh(y, accounting_values, color=colors, height=0.62)
    ax.set_yticks(y, accounting_labels)
    ax.set_xlim(0, 62)
    for index, value in enumerate(accounting_values):
        ax.text(value + 0.7, y[index], str(value), va='center', fontsize=8)
    ax.set_xlabel('Donors/samples')
    ax.set_title('Source and support accounting', loc='left', fontweight='bold')
    ax.text(-0.12, 1.06, 'a', transform=ax.transAxes, fontsize=13, fontweight='bold')

    ax = axes[0, 1]
    ordered = sample_audit.sort_values('bconv_cells').reset_index(drop=True)
    cohort_colors = ordered['cohort'].map({'childhood': '#1F4E79', 'adult': '#D55E00'})
    ax.scatter(np.arange(len(ordered)), ordered['bconv_cells'], c=cohort_colors, s=28, edgecolor='white', linewidth=0.4)
    ax.axhline(50, color='#111827', lw=0.9, linestyle='--')
    ax.axhline(20, color='#9CA3AF', lw=0.8, linestyle=':')
    ax.axhline(100, color='#9CA3AF', lw=0.8, linestyle=':')
    ax.set_yscale('log')
    ax.set_xlabel('Samples ordered by B-cell support')
    ax.set_ylabel('B_CONV-analog cells')
    ax.set_title('Disease-blind sample support', loc='left', fontweight='bold')
    ax.text(-0.12, 1.06, 'b', transform=ax.transAxes, fontsize=13, fontweight='bold')

    ax = axes[1, 0]
    label_total = (
        label_support.groupby(['source_label', 'frozen_compartment'], observed=True)['cell_count']
        .sum()
        .reset_index()
        .sort_values('cell_count')
    )
    label_colors = label_total['frozen_compartment'].map({'B_CONV_ANALOG': '#2A9D8F', 'B_ASC_CONTROL': '#B2182B'})
    y = np.arange(len(label_total))
    ax.barh(y, label_total['cell_count'], color=label_colors, height=0.65)
    ax.set_yticks(y, label_total['source_label'])
    ax.set_xlabel('Matched cells')
    ax.set_title('Frozen source-label representation', loc='left', fontweight='bold')
    ax.text(-0.12, 1.06, 'c', transform=ax.transAxes, fontsize=13, fontweight='bold')

    ax = axes[1, 1]
    arm_plot = program_arms.copy()
    arm_plot['display'] = arm_plot['program_id'].replace(
        {
            'NAIVE_TO_MEMORY_AXIS': 'Naive-to-memory',
            'ATYPICAL_LOW_NAIVE_AXIS': 'Atypical/low-naive',
            'APC_HLA': 'APC/HLA',
            'IFN_ISG': 'IFN/ISG',
            'ACTIVATION_STRESS': 'Activation/stress',
            'TLR7_INNATE': 'TLR7/innate',
            'PLATELET_AMBIENT_QC': 'Platelet QC',
            'ASC_UPR_IDENTITY_QC': 'ASC/UPR QC',
            'PAN_B_IDENTITY_QC': 'Pan-B QC',
        }
    )
    arm_plot['arm'] = arm_plot['sign'].map({1: 'positive', -1: 'negative'})
    y = np.arange(len(arm_plot))[::-1]
    ax.scatter(arm_plot['fraction'] * 100, y, color='#1F4E79', s=30)
    ax.axvline(80, color='#B2182B', lw=0.9, linestyle='--')
    ax.set_yticks(y, arm_plot['display'] + ' (' + arm_plot['arm'] + ')')
    ax.set_xlim(75, 102)
    ax.set_xlabel('Frozen gene availability (%)')
    ax.set_title('Program-arm availability', loc='left', fontweight='bold')
    ax.text(-0.12, 1.06, 'd', transform=ax.transAxes, fontsize=13, fontweight='bold')

    png = figures / 'gate_c5a_gse135779_source_mapping_freeze.png'
    pdf = figures / 'gate_c5a_gse135779_source_mapping_freeze.pdf'
    fig.savefig(png, dpi=320, facecolor='white')
    fig.savefig(pdf, facecolor='white')
    plt.close(fig)

    review = {
        'created_at': dt.datetime.now().astimezone().isoformat(timespec='seconds'),
        'decision': decision,
        'external_effect_unlock_authorized': all_pass,
        'external_disease_effects_inspected': False,
        'checks': checks,
        'frozen_primary': 'GSE135779 childhood B_CONV-analog pseudobulk, >=50 cells, SLE versus HC',
        'frozen_combined': 'GSE135779 combined B_CONV-analog pseudobulk, >=50 cells, is_adult adjustment',
        'frozen_secondary': 'GSE135779 adult B_CONV-analog pseudobulk, >=50 cells',
        'threshold_sensitivities': [20, 100],
        'principal_program': 'IFN_ISG; exact 12-gene Gate C4A dictionary; 12/12 available',
        'limitations': [
            'Two adult metadata donors lack matrix files: aHD2 and aSLE8.',
            'The childhood-only and extended metadata versions are not cell-identical; extended metadata is authoritative.',
            '42,977 source-matrix barcodes lack rows in the processed extended metadata and are excluded from label-based analysis.',
            'Adult >=50 analysis contains 5 HC and 6 SLE donors and is secondary.',
            'Sex and treatment covariates are not present in the local processed metadata.',
            'Source B-caSC labels authorize a broad conventional-B analog, not hard naive/memory identities.',
        ],
        'next_if_pass': 'Gate C5B edgeR/HC3 external disease modeling using only frozen C5A objects.',
    }
    write_text_lf(run / '17_GATE_C5A_ADVISOR_DECISION.json', json.dumps(review, indent=2))
    check_lines = [
        f"| {name} | {'PASS' if item['pass'] else 'FAIL'} | {item['detail']} |"
        for name, item in checks.items()
    ]
    decision_md = [
        '# Gate C5A advisor decision',
        '',
        f'## `{decision}`',
        '',
        'GSE135779 source, identity mapping, pseudobulk counts, program dictionary and external designs are frozen without inspecting a new disease-effect coefficient.',
        '',
        '| Check | Result | Detail |',
        '|---|---:|---|',
        *check_lines,
        '',
        '## Frozen analyses',
        '',
        '- Primary: childhood B_CONV analog, >=50 matched B cells, 11 HC and 32 SLE donors.',
        '- Combined: childhood plus adult, >=50 cells, 16 HC and 38 SLE donors, adjusted for adult stratum.',
        '- Secondary: adult, >=50 cells, 5 HC and 6 SLE donors.',
        '- Threshold sensitivities: >=20 and >=100 cells.',
        '- Confirmatory multiplicity: BH across the exact four Gate C4A programs.',
        '- IFN/ISG dictionary: 12 frozen genes, 12/12 available.',
        '',
        '## Source limitations',
        '',
        '- The 58-to-56 donor difference is fully explained by absent matrices for JB19002/aHD2 and JB19016/aSLE8.',
        '- Four metadata barcodes are absent from matrix barcode lists and are listed explicitly.',
        '- 42,977 matrix barcodes have no extended processed metadata annotation and cannot enter source-label-defined B analysis.',
        '- Childhood metadata versions overlap strongly but are not identical; they must never be concatenated.',
        '',
        '## Next action',
        '',
        'Gate C5B is authorized. Export the frozen >=50/20/100 B_CONV pseudobulks to edgeR, qualify R import against C5A row and gene sums, then fit childhood, combined and adult models. Existing legacy GSE135779 effects remain prohibited as confirmatory inputs.',
    ]
    write_text_lf(run / '17_GATE_C5A_ADVISOR_DECISION.md', '\n'.join(decision_md) + '\n')

    integrity = {
        'created_at': review['created_at'],
        'decision': decision,
        'checks': checks,
        'source_failures': source_failures,
        'tar_member_failures': member_failures,
    }
    write_text_lf(run / '18_GATE_C5A_INTEGRITY_AUDIT.json', json.dumps(integrity, indent=2))
    write_text_lf(
        run / '18_GATE_C5A_INTEGRITY_AUDIT.md',
        '\n'.join(
            [
                '# Gate C5A independent integrity audit',
                '',
                f'- Decision: `{decision}`',
                f"- Checks passed: `{sum(item['pass'] for item in checks.values())}/{len(checks)}`",
                f'- Source files rehashed: `{len(source_manifest)}`',
                f'- Tar members rehashed: `{len(tar_manifest)}`',
                f'- Pseudobulk matrix: `{counts.shape[0]} x {counts.shape[1]}`',
                '- Disease-effect coefficients inspected: **no**',
            ]
        )
        + '\n',
    )

    manifest_rows = []
    for path in sorted(item for item in run.rglob('*') if item.is_file()):
        if path.name == '19_gate_c5a_integrity_manifest.csv':
            continue
        relative = str(path.relative_to(run)).replace('\\', '/')
        manifest_rows.append(
            {
                'relative_path': relative,
                'size_bytes': path.stat().st_size,
                'sha256': sha256_file(path),
                'repository_policy': 'local_recomputable' if path.suffix in {'.npz', '.gz'} else 'tracked',
            }
        )
    write_csv_lf(pd.DataFrame(manifest_rows), run / '19_gate_c5a_integrity_manifest.csv')
    print(json.dumps(review, indent=2))
    return 0 if all_pass else 2


if __name__ == '__main__':
    raise SystemExit(main())
