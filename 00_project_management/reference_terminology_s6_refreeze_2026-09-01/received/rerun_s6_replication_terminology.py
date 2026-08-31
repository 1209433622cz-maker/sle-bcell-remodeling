from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

HERE = Path(__file__).resolve().parent
DATA = HERE / 'Supplementary_Figure_S6_source_data.csv'
OUT_PDF = HERE / 'Supplementary_Figure_S6_replication_robustness_diagnostics.pdf'
OUT_PNG = HERE / 'Supplementary_Figure_S6_replication_robustness_diagnostics.png'

# Nature-like compact source rerender; no scientific values are changed.
rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Arimo', 'Liberation Sans', 'DejaVu Sans'],
    'font.size': 8,
    'axes.titlesize': 8,
    'axes.labelsize': 8,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8,
    'axes.linewidth': 1.0,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
})

# Retain the established project semantic palette.
CONTROL = '#2C6EAD'
SLE = '#C93F3A'
NAIVE = '#2C6EAD'
ATYP = '#7C6AB0'
APC = '#2A8F8F'
IFN = '#D64C45'
RANGE = '#BFC4CA'
PROGRAM_COLORS = {'Naive-to-memory': NAIVE, 'Atypical/low-naive': ATYP, 'APC/HLA': APC, 'IFN/ISG': IFN}

df = pd.read_csv(DATA)
fig = plt.figure(figsize=(170/25.4, 125/25.4))
gs = fig.add_gridspec(2, 2, left=0.09, right=0.985, bottom=0.10, top=0.91, wspace=0.48, hspace=0.70)

# a: donor support by analysis
ax = fig.add_subplot(gs[0,0])
a = df[df.panel.eq('a')].copy()
x = np.arange(len(a))
ref = a.reference_n.astype(float).values
exp = a.exposed_n.astype(float).values
ax.bar(x, ref, width=0.78, label='Control', color=CONTROL)
ax.bar(x, exp, width=0.78, bottom=ref, label='SLE', color=SLE)
ax.set_ylabel('Donors')
ax.set_xticks(x, a['label'].tolist(), rotation=34, ha='right')
ax.set_title('GSE135779 support by analysis', loc='left', pad=5)
ax.legend(frameon=False, loc='upper left')
ax.spines[['top','right']].set_visible(False)
ax.text(-0.12, 1.08, 'a', transform=ax.transAxes, fontweight='bold', va='bottom')

# b: childhood program effects
ax = fig.add_subplot(gs[0,1])
b = df[df.panel.eq('b')].copy()
labels = b['label'].tolist()
y = np.arange(len(labels))[::-1]
for yi, (_, r) in zip(y, b.iterrows()):
    c = PROGRAM_COLORS[r['label']]
    ax.errorbar(float(r.effect), yi,
                xerr=[[float(r.effect-r.ci_low)], [float(r.ci_high-r.effect)]],
                fmt='o', markersize=4, lw=1.0, capsize=0, color=c)
ax.axvline(0, ls='--', lw=1.0, color='0.45')
ax.set_yticks(y, labels)
ax.set_xlabel('Adjusted program-score difference')
ax.set_title('Childhood primary program family', loc='left', pad=5)
ax.spines[['top','right']].set_visible(False)
ax.text(-0.12, 1.08, 'b', transform=ax.transAxes, fontweight='bold', va='bottom')

# c: source-label omission sensitivity
ax = fig.add_subplot(gs[1,0])
cdf = df[df.panel.eq('c')].copy()
y = np.arange(len(cdf))[::-1]
for yi, (_, r) in zip(y, cdf.iterrows()):
    ax.errorbar(float(r.effect), yi,
                xerr=[[float(r.effect-r.ci_low)], [float(r.ci_high-r.effect)]],
                fmt='o', markersize=3.5, lw=1.0, capsize=0, color=APC)
ax.axvline(0, ls='--', lw=1.0, color='0.45')
ax.set_yticks(y, cdf.omitted_source_label.tolist())
ax.set_xlabel('IFN/ISG effect after source-label omission')
ax.set_title('Source-label omission sensitivity', loc='left', pad=5)
ax.spines[['top','right']].set_visible(False)
ax.text(-0.12, 1.08, 'c', transform=ax.transAxes, fontweight='bold', va='bottom')

# d: donor influence range
ax = fig.add_subplot(gs[1,1])
ddf = df[df.panel.eq('d')].copy()
labels = ddf['label'].tolist()
y = np.arange(len(labels))[::-1]
for yi, (_, r) in zip(y, ddf.iterrows()):
    c = PROGRAM_COLORS[r['label']]
    ax.hlines(yi, float(r.loo_min_effect), float(r.loo_max_effect), color=RANGE, lw=1.2)
    ax.plot(float(r.full_effect), yi, 'o', ms=4, color=c)
ax.axvline(0, ls='--', lw=1.0, color='0.45')
ax.set_yticks(y, labels)
ax.set_xlabel('Full effect and donor-deletion range')
ax.set_title('Childhood donor influence', loc='left', pad=5)
ax.spines[['top','right']].set_visible(False)
ax.text(-0.12, 1.08, 'd', transform=ax.transAxes, fontweight='bold', va='bottom')

fig.suptitle('GSE135779 replication and robustness diagnostics', x=0.09, y=0.985, ha='left', fontsize=9, fontweight='bold')
fig.savefig(OUT_PDF, bbox_inches='tight', pad_inches=0.02)
fig.savefig(OUT_PNG, dpi=600, bbox_inches='tight', pad_inches=0.02)
print(OUT_PDF)
print(OUT_PNG)
