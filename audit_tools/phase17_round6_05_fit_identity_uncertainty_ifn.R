#!/usr/bin/env Rscript

# Refit frozen IFN/ISG program effects after each R1 boundary exchange.

args <- commandArgs(trailingOnly = TRUE)
options(warn = 1)
if (length(args) != 3L) {
  stop("Usage: phase17_round6_05_fit_identity_uncertainty_ifn.R <integration_dir> <c4b_dir> <c4a_dir>")
}
integration_dir <- normalizePath(args[[1]], winslash = "/", mustWork = TRUE)
c4b_dir <- normalizePath(args[[2]], winslash = "/", mustWork = TRUE)
c4a_dir <- normalizePath(args[[3]], winslash = "/", mustWork = TRUE)

suppressPackageStartupMessages({
  library(Matrix)
  library(edgeR)
  library(jsonlite)
})

read_sparse <- function(path) {
  connection <- gzfile(path, open = "rt")
  on.exit(close(connection), add = TRUE)
  as(readMM(connection), "CsparseMatrix")
}

hc3_fit <- function(response, design, coefficient) {
  design <- as.matrix(design)
  response <- as.numeric(response)
  bread <- solve(crossprod(design))
  beta <- as.numeric(bread %*% crossprod(design, response))
  residual <- response - as.numeric(design %*% beta)
  leverage <- rowSums((design %*% bread) * design)
  adjusted <- residual / pmax(1 - leverage, 1e-8)
  meat <- crossprod(design, design * as.numeric(adjusted ^ 2))
  covariance <- bread %*% meat %*% bread
  index <- match(coefficient, colnames(design))
  standard_error <- sqrt(max(covariance[index, index], 0))
  degrees_freedom <- nrow(design) - ncol(design)
  statistic <- beta[index] / standard_error
  p_value <- 2 * pt(abs(statistic), df = degrees_freedom, lower.tail = FALSE)
  critical <- qt(0.975, df = degrees_freedom)
  list(
    effect = beta[index],
    se_hc3 = standard_error,
    statistic = statistic,
    df = degrees_freedom,
    p_value = p_value,
    ci_low = beta[index] - critical * standard_error,
    ci_high = beta[index] + critical * standard_error
  )
}

genes <- read.csv(
  gzfile(file.path(c4b_dir, "02_matrix_exports", "gene_metadata.csv.gz")),
  stringsAsFactors = FALSE,
  check.names = FALSE
)
programs <- read.csv(
  file.path(c4a_dir, "11_program_dictionary.csv"),
  stringsAsFactors = FALSE,
  check.names = FALSE,
  fileEncoding = "UTF-8-BOM"
)
ifn_genes <- unique(programs$gene_symbol[programs$program_id == "IFN_ISG" & programs$sign == 1])
if (length(ifn_genes) != 12L) stop("Frozen IFN/ISG program is not the expected 12-gene arm")

definitions <- list(
  primary_base = list(
    samples = "primary_base_samples.csv",
    base_matrix = "primary_base_counts.mtx.gz",
    design = c("intercept", "is_managed", "age_centered", "ethnicity_asian"),
    effect = "is_managed",
    expected_effect = 0.83655647643597297
  ),
  validation_nonoverlap = list(
    samples = "validation_nonoverlap_samples.csv",
    base_matrix = "validation_nonoverlap_counts.mtx.gz",
    design = c("intercept", "is_managed", "age_centered"),
    effect = "is_managed",
    expected_effect = 1.0862405010921401
  )
)

score_ifn <- function(counts, samples, definition) {
  counts <- as.matrix(counts)
  y <- DGEList(counts = counts)
  y <- normLibSizes(y, method = "TMM")
  symbol_counts <- rowsum(counts, group = genes$feature_name, reorder = FALSE)
  effective_library <- y$samples$lib.size * y$samples$norm.factors
  symbol_logcpm <- cpm(symbol_counts, log = TRUE, prior.count = 2, lib.size = effective_library)
  available <- intersect(ifn_genes, rownames(symbol_logcpm))
  if (length(available) != 12L) stop("Corrected matrix lacks frozen IFN genes")
  values <- symbol_logcpm[available, , drop = FALSE]
  deviations <- sqrt(rowSums((values - rowMeans(values)) ^ 2) / (ncol(values) - 1))
  if (any(deviations <= 0)) stop("A frozen IFN gene has zero cross-sample variance")
  z_values <- (values - rowMeans(values)) / deviations
  score <- colMeans(z_values)
  design <- as.matrix(samples[, definition$design, drop = FALSE])
  storage.mode(design) <- "double"
  if (qr(design)$rank != ncol(design)) stop("Corrected design is rank deficient")
  hc3_fit(score, design, definition$effect)
}

rows <- list()
for (analysis in names(definitions)) {
  definition <- definitions[[analysis]]
  samples <- read.csv(
    file.path(c4b_dir, "02_matrix_exports", definition$samples),
    stringsAsFactors = FALSE,
    check.names = FALSE
  )
  base <- read_sparse(file.path(c4b_dir, "02_matrix_exports", definition$base_matrix))
  baseline <- score_ifn(base, samples, definition)
  rows[[length(rows) + 1L]] <- data.frame(
    replicate = 0L,
    analysis = analysis,
    n_samples = nrow(samples),
    effect = baseline$effect,
    se_hc3 = baseline$se_hc3,
    ci_low = baseline$ci_low,
    ci_high = baseline$ci_high,
    statistic = baseline$statistic,
    df = baseline$df,
    p_value = baseline$p_value,
    stringsAsFactors = FALSE
  )
  if (abs(baseline$effect - definition$expected_effect) > 1e-10) {
    stop("Frozen baseline IFN effect did not reproduce for ", analysis)
  }
  for (replicate in seq_len(20L)) {
    path <- file.path(
      integration_dir,
      "matrix_exports",
      sprintf("replicate_%03d_%s_counts.mtx.gz", replicate, analysis)
    )
    corrected <- read_sparse(path)
    if (!identical(dim(corrected), dim(base))) stop("Corrected matrix shape differs")
    fit <- score_ifn(corrected, samples, definition)
    rows[[length(rows) + 1L]] <- data.frame(
      replicate = replicate,
      analysis = analysis,
      n_samples = nrow(samples),
      effect = fit$effect,
      se_hc3 = fit$se_hc3,
      ci_low = fit$ci_low,
      ci_high = fit$ci_high,
      statistic = fit$statistic,
      df = fit$df,
      p_value = fit$p_value,
      stringsAsFactors = FALSE
    )
  }
}

results <- do.call(rbind, rows)
write.csv(results, file.path(integration_dir, "10_IFN_UNCERTAINTY_RESULTS.csv"), row.names = FALSE)
sensitivity <- results[results$replicate > 0L, , drop = FALSE]
summary <- do.call(
  rbind,
  lapply(split(sensitivity, sensitivity$analysis), function(table) {
    baseline <- results$effect[results$replicate == 0L & results$analysis == table$analysis[[1]]]
    data.frame(
      analysis = table$analysis[[1]],
      replicates = nrow(table),
      baseline_effect = baseline,
      minimum_effect = min(table$effect),
      median_effect = median(table$effect),
      maximum_effect = max(table$effect),
      minimum_attenuation = min(table$effect / baseline),
      all_effects_positive = all(table$effect > 0),
      all_intervals_above_zero = all(table$ci_low > 0),
      stringsAsFactors = FALSE
    )
  })
)
write.csv(summary, file.path(integration_dir, "11_IFN_UNCERTAINTY_SUMMARY.csv"), row.names = FALSE)
checks <- list(
  baseline_effects_reproduced = TRUE,
  twenty_replicates_per_analysis = all(summary$replicates == 20L),
  all_effects_positive = all(summary$all_effects_positive),
  all_intervals_above_zero = all(summary$all_intervals_above_zero)
)
if (!all(unlist(checks))) stop("IFN uncertainty propagation checks failed")
status <- list(
  created_at = format(Sys.time(), "%Y-%m-%dT%H:%M:%S%z"),
  status = "PASS_R1_IDENTITY_UNCERTAINTY_IFN_PROPAGATION",
  method = "full-data frozen B_CONV counts plus replicate-specific boundary-cell deltas; edgeR TMM logCPM; frozen 12-gene z-score; OLS HC3",
  sample_selection = "frozen; no sample or gene re-selection",
  summary = lapply(seq_len(nrow(summary)), function(index) as.list(summary[index, ])),
  checks = checks,
  interpretation = "R1 state-membership uncertainty did not reverse or erase the frozen B_CONV IFN/ISG effects. This is a sensitivity analysis, not independent replication."
)
write_json(status, file.path(integration_dir, "12_IFN_UNCERTAINTY_STATUS.json"), pretty = TRUE, auto_unbox = TRUE)
cat(toJSON(status, pretty = TRUE, auto_unbox = TRUE), "\n")
