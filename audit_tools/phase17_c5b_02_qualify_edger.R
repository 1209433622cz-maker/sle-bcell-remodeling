#!/usr/bin/env Rscript

# Gate C5B-02: qualify R import and edgeR without fitting a real disease effect.

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2L) {
  stop("Usage: phase17_c5b_02_qualify_edger.R <run_dir> <qualification_output_json>")
}
run_dir <- normalizePath(args[[1]], winslash = "/", mustWork = TRUE)
output_json <- args[[2]]

suppressPackageStartupMessages({
  library(Matrix)
  library(edgeR)
  library(limma)
  library(jsonlite)
  library(statmod)
})

audit <- fromJSON(file.path(run_dir, "03_MATRIX_EXPORT_AUDIT.json"), simplifyVector = FALSE)
if (!identical(audit$status, "PASS_C5B_FROZEN_MATRIX_EXPORT")) {
  stop("Frozen C5B matrix export did not pass")
}
if (!identical(audit$real_effect_estimates_inspected, FALSE)) {
  stop("C5B pre-effect contract is not intact")
}

read_and_check <- function(item) {
  connection <- gzfile(file.path(run_dir, item$matrix_relative_path), open = "rt")
  counts <- readMM(connection)
  close(connection)
  counts <- as(counts, "CsparseMatrix")
  samples <- read.csv(
    file.path(run_dir, item$sample_relative_path),
    check.names = FALSE,
    stringsAsFactors = FALSE
  )
  gene_sums <- read.csv(
    file.path(run_dir, item$gene_sums_relative_path),
    check.names = FALSE,
    stringsAsFactors = FALSE
  )
  dimensions <- identical(
    as.integer(dim(counts)),
    c(as.integer(item$n_genes), as.integer(item$n_samples))
  )
  column_sums <- identical(
    as.numeric(colSums(counts)),
    as.numeric(samples$matrix_library_size_umi)
  )
  row_sums <- identical(as.numeric(rowSums(counts)), as.numeric(gene_sums$count_sum))
  integer_nonnegative <- length(counts@x) == 0L ||
    (all(counts@x >= 0) && all(counts@x == floor(counts@x)))
  list(
    analysis_name = item$analysis_name,
    shape = as.integer(dim(counts)),
    dimensions_pass = dimensions,
    column_sums_pass = column_sums,
    gene_sums_pass = row_sums,
    integer_nonnegative_pass = integer_nonnegative,
    pass = dimensions && column_sums && row_sums && integer_nonnegative
  )
}

main_imports <- lapply(audit$analyses, read_and_check)
source_imports <- lapply(audit$source_label_sensitivities, read_and_check)
all_imports <- c(main_imports, source_imports)
all_imports_pass <- all(vapply(all_imports, function(item) isTRUE(item$pass), logical(1)))

fit_synthetic <- function(with_signal, seed) {
  set.seed(seed)
  n_genes <- 2000L
  n_samples <- 80L
  n_signal <- 100L
  group <- rep(c(0, 1), each = n_samples / 2L)
  age <- as.numeric(scale(rnorm(n_samples, 42, 11), center = TRUE, scale = FALSE))
  design <- cbind(intercept = 1, group = group, age_centered = age)
  base_mean <- exp(rnorm(n_genes, log(60), 0.9))
  library_factor <- exp(rnorm(n_samples, 0, 0.18))
  true_log2fc <- rep(0, n_genes)
  if (with_signal) true_log2fc[seq_len(n_signal)] <- 1.25
  mu <- outer(base_mean, library_factor) * 2 ^ outer(true_log2fc, group)
  synthetic <- matrix(
    rnbinom(n_genes * n_samples, mu = as.vector(mu), size = 1 / 0.12),
    nrow = n_genes,
    ncol = n_samples
  )
  rownames(synthetic) <- sprintf("SYN%04d", seq_len(n_genes))
  y <- DGEList(counts = synthetic)
  y <- normLibSizes(y, method = "TMM")
  keep <- filterByExpr(y, design = design)
  y <- y[keep, , keep.lib.sizes = FALSE]
  y <- estimateDisp(y, design, robust = TRUE)
  fit <- glmQLFit(y, design, robust = TRUE)
  test <- glmQLFTest(fit, coef = "group")
  result <- topTags(test, n = Inf, sort.by = "none")$table
  result$gene <- rownames(result)
  result$fdr <- p.adjust(result$PValue, method = "BH")
  result$truth <- true_log2fc[match(result$gene, rownames(synthetic))]
  result
}

null_result <- fit_synthetic(FALSE, 2026081501L)
signal_result <- fit_synthetic(TRUE, 2026081502L)
signal_rows <- signal_result$truth > 0
signal_calls <- signal_result$fdr < 0.05
null_fpr <- mean(null_result$PValue < 0.05)
null_median_log2fc <- median(null_result$logFC)
signal_median_log2fc <- median(signal_result$logFC[signal_rows])
signal_sign_concordance <- mean(signal_result$logFC[signal_rows] > 0)
signal_sensitivity <- mean(signal_result$fdr[signal_rows] < 0.05)
signal_empirical_fdr <- if (sum(signal_calls) == 0L) 1 else {
  sum(signal_calls & !signal_rows) / sum(signal_calls)
}

checks <- list(
  all_frozen_imports = list(
    pass = all_imports_pass,
    detail = sprintf("%d main plus %d source-label matrices", length(main_imports), length(source_imports))
  ),
  null_type1 = list(pass = null_fpr <= 0.08, detail = sprintf("P<0.05 fraction %.4f <= 0.0800", null_fpr)),
  null_bias = list(pass = abs(null_median_log2fc) <= 0.10, detail = sprintf("median log2FC %.4f; |value| <= 0.10", null_median_log2fc)),
  signal_effect_recovery = list(pass = signal_median_log2fc >= 0.80, detail = sprintf("median recovered log2FC %.4f >= 0.80", signal_median_log2fc)),
  signal_direction = list(pass = signal_sign_concordance >= 0.95, detail = sprintf("sign concordance %.4f >= 0.95", signal_sign_concordance)),
  signal_sensitivity = list(pass = signal_sensitivity >= 0.80, detail = sprintf("BH sensitivity %.4f >= 0.80", signal_sensitivity)),
  signal_empirical_fdr = list(pass = signal_empirical_fdr <= 0.10, detail = sprintf("empirical FDR %.4f <= 0.10", signal_empirical_fdr))
)
qualification_pass <- all(vapply(checks, function(item) isTRUE(item$pass), logical(1)))

session_path <- file.path(run_dir, "01_R_sessionInfo.txt")
sink(session_path)
cat("Gate C5B statistical-engine qualification\n")
cat("Generated: ", format(Sys.time(), "%Y-%m-%dT%H:%M:%S%z"), "\n\n", sep = "")
print(sessionInfo())
cat("\nRepositories:\n")
print(getOption("repos"))
cat("\nBioconductor version:\n")
print(as.character(BiocManager::version()))
sink()
session_lines <- readLines(session_path, warn = FALSE)
writeLines(sub("[[:space:]]+$", "", session_lines), session_path, useBytes = TRUE)

result <- list(
  created_at = format(Sys.time(), "%Y-%m-%dT%H:%M:%S%z"),
  status = if (qualification_pass) "PASS_C5B_EDGER_QUALIFICATION" else "HOLD_C5B_EDGER_QUALIFICATION",
  real_effect_estimates_inspected = FALSE,
  r_version = R.version.string,
  bioconductor_version = as.character(BiocManager::version()),
  package_versions = list(
    edgeR = as.character(packageVersion("edgeR")),
    limma = as.character(packageVersion("limma")),
    Matrix = as.character(packageVersion("Matrix")),
    statmod = as.character(packageVersion("statmod")),
    jsonlite = as.character(packageVersion("jsonlite"))
  ),
  import_audits = all_imports,
  checks = checks,
  synthetic_metrics = list(
    null_type1_fraction = null_fpr,
    null_median_log2fc = null_median_log2fc,
    signal_median_log2fc = signal_median_log2fc,
    signal_sign_concordance = signal_sign_concordance,
    signal_bh_sensitivity = signal_sensitivity,
    signal_empirical_fdr = signal_empirical_fdr
  )
)
write_json(result, output_json, pretty = TRUE, auto_unbox = TRUE, digits = 8)

markdown_path <- sub("[.]json$", ".md", output_json)
markdown <- c(
  "# Gate C5B edgeR/limma qualification",
  "",
  paste0("- Status: `", result$status, "`"),
  "- Real external disease effects inspected: **no**",
  paste0("- R: `", R.version.string, "`"),
  paste0("- edgeR: `", result$package_versions$edgeR, "`; limma: `", result$package_versions$limma, "`"),
  "",
  "| Check | Pass | Detail |",
  "|---|---:|---|"
)
for (name in names(checks)) {
  item <- checks[[name]]
  markdown <- c(markdown, paste0("| ", name, " | ", if (item$pass) "PASS" else "FAIL", " | ", item$detail, " |"))
}
markdown <- c(
  markdown,
  "",
  "All 13 real matrices were imported only for dimensions and count conservation. No real disease coefficient was fitted before this decision."
)
writeLines(markdown, markdown_path, useBytes = TRUE)
cat(toJSON(result, pretty = TRUE, auto_unbox = TRUE), "\n")

if (!qualification_pass) quit(status = 2L)
