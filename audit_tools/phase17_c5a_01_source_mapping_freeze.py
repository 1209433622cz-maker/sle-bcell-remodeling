#!/usr/bin/env python3
"""Gate C5A-01: audit GSE135779 and freeze disease-blind external mappings."""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def write_text_lf(path: Path, content: str) -> None:
    with path.open('w', encoding='utf-8', newline='\n') as handle:
        handle.write(content)


def write_csv_lf(frame, path: Path, **kwargs) -> None:
    kwargs.setdefault('index', False)
    kwargs.setdefault('lineterminator', '\n')
    frame.to_csv(path, **kwargs)


def read_csv(path: Path):
    import pandas as pd

    return pd.read_csv(path)


def classify_label(label: str) -> tuple[str, str]:
    upper = str(label).upper()
    if upper.startswith('B-'):
        return 'B_CONV_ANALOG', 'primary conventional-B source annotation'
    if upper.startswith('PC-'):
        return 'B_ASC_CONTROL', 'plasma-cell/ASC identity control only'
    return 'EXCLUDED_NON_B', 'excluded from B-lineage pseudobulk'


def build_design(sample_table, name: str, threshold: int, cohort: str | None):
    import numpy as np

    work = sample_table.loc[sample_table['bconv_cells'] >= threshold].copy()
    if cohort is not None:
        work = work.loc[work['cohort'] == cohort].copy()
    work.insert(0, 'analysis_name', name)
    work['intercept'] = 1.0
    work['is_sle'] = (work['disease_group'] == 'SLE').astype(int)
    work['is_adult'] = (work['cohort'] == 'adult').astype(int)
    columns = ['intercept', 'is_sle']
    if cohort is None:
        columns.append('is_adult')
    rank = int(np.linalg.matrix_rank(work[columns].to_numpy(dtype=float)))
    work['design_columns'] = ';'.join(columns)
    work['design_rank'] = rank
    work['minimum_bconv_cells'] = threshold
    return work.sort_values(['cohort', 'disease_group', 'sample_id']).reset_index(drop=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-dir', required=True)
    parser.add_argument('--gate-c4a-dir', required=True)
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()

    import numpy as np
    import pandas as pd
    from scipy import sparse
    from scipy.io import mmread

    source = Path(args.source_dir).resolve()
    c4a = Path(args.gate_c4a_dir).resolve()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    raw_tar = source / 'GSE135779_RAW.tar'
    gene_path = source / 'GSE135779_genes.tsv.gz'
    child_meta_path = source / 'Meta_cSLE_processed_0809202_small.csv'
    extended_meta_path = source / 'Meta_caSLE_processed_08092021_small.csv'
    required = [
        raw_tar,
        gene_path,
        child_meta_path,
        extended_meta_path,
        source / 'GSE135779_series_matrix.txt.gz',
        source / 'libaries.csv',
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError('Missing GSE135779 source files: ' + ', '.join(missing))

    source_manifest = []
    for path in required:
        source_manifest.append(
            {
                'filename': path.name,
                'size_bytes': path.stat().st_size,
                'sha256': sha256_file(path),
                'role': 'raw matrix archive' if path == raw_tar else 'source metadata',
            }
        )
    write_csv_lf(pd.DataFrame(source_manifest), output / '01_SOURCE_FILE_MANIFEST.csv')

    genes = pd.read_csv(
        gene_path,
        sep='\t',
        header=None,
        names=['ensembl_id', 'gene_symbol'],
    )
    genes['gene_symbol_upper'] = genes['gene_symbol'].astype(str).str.upper()
    genes['is_mitochondrial'] = genes['gene_symbol_upper'].str.startswith('MT-')
    genes['is_ribosomal'] = genes['gene_symbol_upper'].str.match(r'^RP[SL]')
    genes['is_hemoglobin'] = genes['gene_symbol_upper'].str.match(r'^HB[ABDEGQZ]')
    genes['is_immunoglobulin'] = genes['gene_symbol_upper'].str.match(r'^IG[HKL]')
    if genes['ensembl_id'].duplicated().any():
        raise RuntimeError('GSE135779 Ensembl identifiers are not unique')

    child_meta = pd.read_csv(child_meta_path)
    extended = pd.read_csv(extended_meta_path)
    child_ids = set(child_meta['IDs'].astype(str))
    extended_child = extended.loc[extended['IDs'].astype(str).isin(child_ids)]
    if child_ids != set(extended_child['IDs'].astype(str)):
        raise RuntimeError('Childhood sample IDs differ between metadata versions')
    metadata_version_rows = []
    for sample_id in sorted(child_ids):
        child_barcodes = set(
            child_meta.loc[child_meta['IDs'].astype(str) == sample_id, 'index']
            .astype(str)
            .str.split('-')
            .str[0]
        )
        extended_barcodes = set(
            extended_child.loc[extended_child['IDs'].astype(str) == sample_id, 'index']
            .astype(str)
            .str.split('-')
            .str[0]
        )
        intersection = len(child_barcodes & extended_barcodes)
        union = len(child_barcodes | extended_barcodes)
        metadata_version_rows.append(
            {
                'sample_id': sample_id,
                'childhood_only_cells': len(child_barcodes),
                'extended_version_cells': len(extended_barcodes),
                'shared_cells': intersection,
                'childhood_only_unique_cells': len(child_barcodes - extended_barcodes),
                'extended_unique_cells': len(extended_barcodes - child_barcodes),
                'overlap_over_smaller': intersection / min(len(child_barcodes), len(extended_barcodes)),
                'jaccard': intersection / union,
            }
        )
    metadata_version_audit = pd.DataFrame(metadata_version_rows)
    aggregate_jaccard = len(
        set(zip(child_meta['IDs'].astype(str), child_meta['index'].astype(str).str.split('-').str[0]))
        & set(zip(extended_child['IDs'].astype(str), extended_child['index'].astype(str).str.split('-').str[0]))
    ) / len(
        set(zip(child_meta['IDs'].astype(str), child_meta['index'].astype(str).str.split('-').str[0]))
        | set(zip(extended_child['IDs'].astype(str), extended_child['index'].astype(str).str.split('-').str[0]))
    )
    if aggregate_jaccard < 0.95:
        raise RuntimeError(f'Childhood metadata versions overlap inadequately: Jaccard={aggregate_jaccard:.4f}')
    write_csv_lf(metadata_version_audit, output / '04A_CHILDHOOD_METADATA_VERSION_AUDIT.csv')

    extended['sample_id'] = extended['IDs'].astype(str)
    extended['donor_name'] = extended['Names'].astype(str)
    extended['barcode'] = extended['index'].astype(str)
    extended['barcode_core'] = extended['barcode'].str.split('-').str[0]
    extended['cohort'] = np.where(
        extended['donor_name'].str.startswith('a'),
        'adult',
        np.where(extended['donor_name'].str.startswith('c'), 'childhood', 'unknown'),
    )
    sample_uniqueness = extended.groupby('sample_id')['donor_name'].nunique()
    if (sample_uniqueness != 1).any():
        raise RuntimeError('A sample ID maps to multiple donor names')
    if extended.duplicated(['sample_id', 'barcode_core']).any():
        raise RuntimeError('Duplicate barcode cores exist within a sample')

    sample_info = (
        extended.groupby('sample_id', observed=True)
        .agg(
            donor_name=('donor_name', 'first'),
            cohort=('cohort', 'first'),
            metadata_cells=('barcode_core', 'size'),
            metadata_labels=('subclusters', 'nunique'),
        )
        .reset_index()
    )
    sample_info['disease_group'] = np.where(
        sample_info['donor_name'].str.upper().str.contains('SLE'), 'SLE', 'HC'
    )

    labels = sorted(extended['subclusters'].astype(str).unique())
    label_dictionary = []
    for label in labels:
        compartment, role = classify_label(label)
        label_dictionary.append(
            {
                'source_label': label,
                'frozen_compartment': compartment,
                'publication_role': role,
                'disease_blind_rule': 'prefix mapping from source annotation only',
                'metadata_cells': int((extended['subclusters'].astype(str) == label).sum()),
                'metadata_samples': int(extended.loc[extended['subclusters'].astype(str) == label, 'sample_id'].nunique()),
            }
        )
    label_dictionary = pd.DataFrame(label_dictionary)
    write_csv_lf(label_dictionary, output / '05_SOURCE_LABEL_DICTIONARY.csv')
    selected_labels = label_dictionary.loc[
        label_dictionary['frozen_compartment'].isin(['B_CONV_ANALOG', 'B_ASC_CONTROL']),
        'source_label',
    ].tolist()

    tar_member_rows = []
    sample_rows = []
    barcode_exception_rows = []
    label_support_rows = []
    aggregate_rows = []
    aggregate_metadata = []
    tar_sample_ids = []

    with tarfile.open(raw_tar, 'r') as archive:
        members = {member.name: member for member in archive.getmembers() if member.isfile()}
        barcode_members = sorted(name for name in members if name.endswith('_barcodes.tsv.gz'))
        matrix_members = sorted(name for name in members if name.endswith('_matrix.mtx.gz'))
        if len(barcode_members) != 56 or len(matrix_members) != 56:
            raise RuntimeError(f'Expected 56 barcode and matrix members, found {len(barcode_members)} and {len(matrix_members)}')

        for barcode_name in barcode_members:
            parts = barcode_name.split('_')
            accession = parts[0]
            sample_id = parts[1]
            matrix_name = barcode_name.replace('_barcodes.tsv.gz', '_matrix.mtx.gz')
            if matrix_name not in members:
                raise RuntimeError(f'Missing matrix partner for {barcode_name}')
            tar_sample_ids.append(sample_id)
            sample_meta = extended.loc[extended['sample_id'] == sample_id].copy()
            if sample_meta.empty:
                raise RuntimeError(f'Tar sample {sample_id} has no extended metadata')

            barcode_handle = archive.extractfile(members[barcode_name])
            matrix_handle = archive.extractfile(members[matrix_name])
            if barcode_handle is None or matrix_handle is None:
                raise RuntimeError(f'Cannot read tar pair for {sample_id}')
            barcode_bytes = barcode_handle.read()
            matrix_bytes = matrix_handle.read()
            for name, payload, member, role in (
                (barcode_name, barcode_bytes, members[barcode_name], 'barcodes'),
                (matrix_name, matrix_bytes, members[matrix_name], 'matrix'),
            ):
                tar_member_rows.append(
                    {
                        'member_name': name,
                        'sample_id': sample_id,
                        'accession': accession,
                        'role': role,
                        'size_bytes': member.size,
                        'sha256_compressed_member': sha256_bytes(payload),
                    }
                )

            barcodes = [
                line.strip()
                for line in gzip.decompress(barcode_bytes).decode('utf-8').splitlines()
                if line.strip()
            ]
            barcode_cores = [barcode.split('-')[0] for barcode in barcodes]
            if len(set(barcode_cores)) != len(barcode_cores):
                raise RuntimeError(f'Duplicate matrix barcode cores for {sample_id}')
            barcode_lookup = {barcode: index for index, barcode in enumerate(barcode_cores)}
            sample_meta['matrix_col'] = sample_meta['barcode_core'].map(barcode_lookup)
            matched = sample_meta['matrix_col'].notna()
            for exception in sample_meta.loc[~matched].itertuples(index=False):
                barcode_exception_rows.append(
                    {
                        'sample_id': sample_id,
                        'donor_name': exception.donor_name,
                        'barcode': exception.barcode,
                        'barcode_core': exception.barcode_core,
                        'source_label': exception.subclusters,
                        'issue': 'metadata barcode absent from source matrix barcode list',
                    }
                )

            with gzip.GzipFile(fileobj=io.BytesIO(matrix_bytes), mode='rb') as stream:
                matrix = mmread(stream).tocsr()
            if matrix.shape != (len(genes), len(barcodes)):
                raise RuntimeError(f'Matrix shape mismatch for {sample_id}: {matrix.shape}')
            integer_nonnegative = bool(
                matrix.data.size == 0
                or (matrix.data.min() >= 0 and np.all(matrix.data == np.floor(matrix.data)))
            )
            if not integer_nonnegative:
                raise RuntimeError(f'Non-integer or negative counts in {sample_id}')

            sample_row = sample_info.loc[sample_info['sample_id'] == sample_id].iloc[0]
            bconv_mask = sample_meta['subclusters'].astype(str).str.upper().str.startswith('B-') & matched
            basc_mask = sample_meta['subclusters'].astype(str).str.upper().str.startswith('PC-') & matched
            bconv_columns = sample_meta.loc[bconv_mask, 'matrix_col'].astype(int).to_numpy()
            basc_columns = sample_meta.loc[basc_mask, 'matrix_col'].astype(int).to_numpy()

            bconv_counts = np.asarray(matrix[:, bconv_columns].sum(axis=1)).ravel().astype(np.int64)
            basc_counts = np.asarray(matrix[:, basc_columns].sum(axis=1)).ravel().astype(np.int64)
            for compartment, counts_vector, cell_count in (
                ('B_CONV_ANALOG', bconv_counts, len(bconv_columns)),
                ('B_ASC_CONTROL', basc_counts, len(basc_columns)),
            ):
                aggregate_rows.append(sparse.csr_matrix(counts_vector.reshape(1, -1)))
                aggregate_metadata.append(
                    {
                        'representation': 'compartment',
                        'sample_id': sample_id,
                        'accession': accession,
                        'frozen_compartment': compartment,
                        'source_label': '',
                        'cell_count': int(cell_count),
                        'library_size_umi': int(counts_vector.sum()),
                        'detected_genes': int((counts_vector > 0).sum()),
                    }
                )

            for label in selected_labels:
                label_mask = (sample_meta['subclusters'].astype(str) == label) & matched
                columns = sample_meta.loc[label_mask, 'matrix_col'].astype(int).to_numpy()
                counts_vector = np.asarray(matrix[:, columns].sum(axis=1)).ravel().astype(np.int64)
                compartment, _ = classify_label(label)
                aggregate_rows.append(sparse.csr_matrix(counts_vector.reshape(1, -1)))
                aggregate_metadata.append(
                    {
                        'representation': 'source_label',
                        'sample_id': sample_id,
                        'accession': accession,
                        'frozen_compartment': compartment,
                        'source_label': label,
                        'cell_count': int(len(columns)),
                        'library_size_umi': int(counts_vector.sum()),
                        'detected_genes': int((counts_vector > 0).sum()),
                    }
                )
                label_support_rows.append(
                    {
                        'sample_id': sample_id,
                        'source_label': label,
                        'frozen_compartment': compartment,
                        'cell_count': int(len(columns)),
                        'library_size_umi': int(counts_vector.sum()),
                    }
                )

            sample_rows.append(
                {
                    'sample_id': sample_id,
                    'accession': accession,
                    'donor_name': sample_row['donor_name'],
                    'cohort': sample_row['cohort'],
                    'metadata_cells': int(len(sample_meta)),
                    'matrix_barcodes': len(barcodes),
                    'matched_metadata_cells': int(matched.sum()),
                    'unmatched_metadata_cells': int((~matched).sum()),
                    'unannotated_matrix_barcodes': int(len(barcodes) - matched.sum()),
                    'matrix_genes': int(matrix.shape[0]),
                    'matrix_nnz': int(matrix.nnz),
                    'matrix_total_umi': int(matrix.sum()),
                    'integer_nonnegative': integer_nonnegative,
                    'bconv_cells': int(len(bconv_columns)),
                    'bconv_library_size_umi': int(bconv_counts.sum()),
                    'basc_control_cells': int(len(basc_columns)),
                    'basc_control_library_size_umi': int(basc_counts.sum()),
                }
            )
            print(
                f'[C5A] {sample_id}: {matrix.shape[1]:,} cells; '
                f'{len(bconv_columns):,} B_CONV; {len(basc_columns):,} PC/ASC'
            )
            del matrix

    tar_manifest = pd.DataFrame(tar_member_rows).sort_values(['sample_id', 'role'])
    write_csv_lf(tar_manifest, output / '02_TAR_MEMBER_MANIFEST.csv')
    sample_audit = pd.DataFrame(sample_rows).sort_values('sample_id').reset_index(drop=True)
    write_csv_lf(sample_audit, output / '03_SAMPLE_SOURCE_AUDIT.csv')
    write_csv_lf(
        pd.DataFrame(barcode_exception_rows), output / '03A_METADATA_BARCODE_EXCEPTIONS.csv'
    )

    missing_samples = sample_info.loc[~sample_info['sample_id'].isin(tar_sample_ids)].copy()
    missing_counts = (
        extended.loc[extended['sample_id'].isin(missing_samples['sample_id'])]
        .groupby(['sample_id', 'donor_name', 'cohort', 'subclusters'], observed=True)
        .size()
        .reset_index(name='metadata_cells')
    )
    missing_counts = missing_counts.merge(
        missing_samples[['sample_id', 'disease_group']], on='sample_id', how='left'
    )
    write_csv_lf(missing_counts, output / '04_METADATA_WITHOUT_MATRIX_SAMPLES.csv')
    write_csv_lf(pd.DataFrame(label_support_rows), output / '06_SAMPLE_LABEL_SUPPORT.csv')

    aggregate = sparse.vstack(aggregate_rows, format='csr', dtype=np.int64)
    aggregate_meta = pd.DataFrame(aggregate_metadata)
    aggregate_meta.insert(0, 'pseudobulk_row', np.arange(len(aggregate_meta), dtype=int))
    if not np.array_equal(
        np.asarray(aggregate.sum(axis=1)).ravel().astype(np.int64),
        aggregate_meta['library_size_umi'].to_numpy(dtype=np.int64),
    ):
        raise RuntimeError('External pseudobulk row sums do not match metadata')
    sparse.save_npz(output / '07_EXTERNAL_PSEUDOBULK_COUNTS.npz', aggregate, compressed=True)
    write_csv_lf(aggregate_meta, output / '08_EXTERNAL_PSEUDOBULK_ROW_METADATA.csv')
    write_csv_lf(genes, output / '09_EXTERNAL_GENE_UNIVERSE.csv.gz', compression='gzip')

    frozen_programs = pd.read_csv(c4a / '11_program_dictionary.csv', encoding='utf-8-sig')
    write_csv_lf(frozen_programs, output / '10_FROZEN_PROGRAM_DICTIONARY.csv')
    available_symbols = set(genes['gene_symbol_upper'])
    program_availability = frozen_programs.copy()
    program_availability['present'] = program_availability['gene_symbol'].str.upper().isin(available_symbols)
    symbol_feature_counts = genes.groupby('gene_symbol_upper').size()
    program_availability['matching_features'] = (
        program_availability['gene_symbol'].str.upper().map(symbol_feature_counts).fillna(0).astype(int)
    )
    write_csv_lf(program_availability, output / '11_FROZEN_PROGRAM_GENE_AVAILABILITY.csv')

    compartment_rows = aggregate_meta.loc[
        (aggregate_meta['representation'] == 'compartment')
        & (aggregate_meta['frozen_compartment'] == 'B_CONV_ANALOG')
    ][['sample_id', 'cell_count', 'library_size_umi', 'detected_genes']].rename(
        columns={
            'cell_count': 'bconv_cells',
            'library_size_umi': 'bconv_library_size_umi',
            'detected_genes': 'bconv_detected_genes',
        }
    )
    model_samples = sample_info.merge(compartment_rows, on='sample_id', how='inner')
    designs = {
        'combined_min50': build_design(model_samples, 'C5B_GSE135779_COMBINED_MIN50', 50, None),
        'childhood_min50': build_design(model_samples, 'C5B_GSE135779_CHILDHOOD_MIN50', 50, 'childhood'),
        'adult_min50': build_design(model_samples, 'C5B_GSE135779_ADULT_MIN50', 50, 'adult'),
        'combined_min20': build_design(model_samples, 'C5B_GSE135779_COMBINED_MIN20', 20, None),
        'combined_min100': build_design(model_samples, 'C5B_GSE135779_COMBINED_MIN100', 100, None),
    }
    write_csv_lf(designs['combined_min50'], output / '12_COMBINED_MIN50_MODEL_MATRIX.csv')
    write_csv_lf(designs['childhood_min50'], output / '13_CHILDHOOD_MIN50_MODEL_MATRIX.csv')
    write_csv_lf(designs['adult_min50'], output / '14_ADULT_MIN50_MODEL_MATRIX.csv')
    write_csv_lf(
        pd.concat([designs['combined_min20'], designs['combined_min100']], ignore_index=True),
        output / '15_THRESHOLD_SENSITIVITY_MODEL_MATRICES.csv',
    )

    program_arm_summary = (
        program_availability.groupby(['program_id', 'program_label', 'analysis_family', 'sign'], observed=True)
        .agg(available=('present', 'sum'), total=('present', 'size'))
        .reset_index()
    )
    program_arm_summary['fraction'] = program_arm_summary['available'] / program_arm_summary['total']
    program_arm_summary['pass_80pct'] = program_arm_summary['fraction'] >= 0.8

    design_summary = []
    for name, table in designs.items():
        design_columns = table['design_columns'].iloc[0].split(';')
        design_summary.append(
            {
                'analysis_name': name,
                'minimum_bconv_cells': int(table['minimum_bconv_cells'].iloc[0]),
                'n_samples': len(table),
                'n_hc': int((table['disease_group'] == 'HC').sum()),
                'n_sle': int((table['disease_group'] == 'SLE').sum()),
                'design_columns': ';'.join(design_columns),
                'design_rank': int(table['design_rank'].iloc[0]),
                'required_rank': len(design_columns),
            }
        )

    contract = {
        'created_at': dt.datetime.now().astimezone().isoformat(timespec='seconds'),
        'status': 'C5A_SOURCE_MAPPING_FREEZE_COMPLETE_REVIEW_REQUIRED',
        'external_disease_effects_inspected': False,
        'source': {
            'accession': 'GSE135779',
            'metadata_donors': int(sample_info['sample_id'].nunique()),
            'matrix_samples': int(len(sample_audit)),
            'missing_matrix_samples': missing_samples['sample_id'].tolist(),
            'missing_matrix_donors': missing_samples['donor_name'].tolist(),
            'missingness_balance': missing_samples['disease_group'].value_counts().to_dict(),
            'gene_features': int(len(genes)),
            'ensembl_unique': True,
            'authoritative_metadata': 'Meta_caSLE_processed_08092021_small.csv',
            'childhood_metadata_version_jaccard': aggregate_jaccard,
            'metadata_versions_are_identical': False,
            'matched_metadata_cells': int(sample_audit['matched_metadata_cells'].sum()),
            'unmatched_metadata_cells': int(sample_audit['unmatched_metadata_cells'].sum()),
            'unannotated_matrix_barcodes': int(sample_audit['unannotated_matrix_barcodes'].sum()),
        },
        'identity_mapping': {
            'B_CONV_ANALOG': 'all source labels with B- prefix in extended metadata',
            'B_ASC_CONTROL': 'all source labels with PC- prefix; identity/QC only',
            'mapping_uses_disease': False,
            'hard_subtype_claims_authorized': False,
        },
        'pseudobulk': {
            'shape': list(aggregate.shape),
            'dtype': str(aggregate.dtype),
            'row_sum_conserved': True,
            'inferential_unit': 'one matrix sample / one donor',
        },
        'minimum_bconv_cells': 50,
        'threshold_sensitivities': [20, 100],
        'designs': design_summary,
        'program_policy': {
            'source': 'exact Gate C4A frozen dictionary',
            'confirmatory_family': ['NAIVE_TO_MEMORY_AXIS', 'ATYPICAL_LOW_NAIVE_AXIS', 'APC_HLA', 'IFN_ISG'],
            'primary_multiplicity': 'BH across four external coefficients',
            'minimum_availability_per_signed_arm': 0.8,
            'all_arms_pass': bool(program_arm_summary['pass_80pct'].all()),
            'ifn_isg_frozen_gene_count': int((frozen_programs['program_id'] == 'IFN_ISG').sum()),
            'ifn_isg_available_gene_count': int(
                program_availability.loc[program_availability['program_id'] == 'IFN_ISG', 'present'].sum()
            ),
        },
        'frozen_primary_external_analysis': 'childhood_min50',
        'frozen_combined_analysis': 'combined_min50 with is_adult adjustment',
        'frozen_secondary_analysis': 'adult_min50',
        'prohibited': [
            'cell-level disease testing',
            'reuse of legacy external effect estimates as confirmatory evidence',
            'outcome-adaptive source-label inclusion',
            'program membership changes after external effect inspection',
            'B_ASC_CONTROL as a conventional-B disease endpoint',
        ],
    }
    write_text_lf(output / '16_GATE_C5A_FREEZE_CONTRACT.json', json.dumps(contract, indent=2))
    write_csv_lf(pd.DataFrame(design_summary), output / '16_GATE_C5A_DESIGN_SUMMARY.csv')
    write_csv_lf(program_arm_summary, output / '16_GATE_C5A_PROGRAM_ARM_SUMMARY.csv')

    status = {
        'created_at': contract['created_at'],
        'status': contract['status'],
        'external_disease_effects_inspected': False,
        'source_files_hashed': len(source_manifest),
        'tar_members_hashed': len(tar_manifest),
        'matrix_samples_audited': len(sample_audit),
        'pseudobulk_rows': len(aggregate_meta),
    }
    write_text_lf(output / '00_GATE_C5A_RUN_STATUS.json', json.dumps(status, indent=2))
    print(json.dumps(status, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
