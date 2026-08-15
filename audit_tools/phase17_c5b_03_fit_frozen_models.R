#!/usr/bin/env Rscript

# Gate C5B-03: fit the authorized frozen GSE135779 external models.

args <- commandArgs(trailingOnly = TRUE)
options(warn = 1)
if (length(args) != 2L) {
  stop("Usage: phase17_c5b_03_fit_frozen_models.R <run_dir> <gate_c5a_dir>")
}
run_dir <- normalizePath(args[[1]], winslash = "/", mustWork = TRUE)
c5a_dir <- normalizePath(args[[2]], winslash = "/", mustWork = TRUE)

suppressPackageStartupMessages({
  library(Matrix)
  library(edgeR)
  library(limma)
  library(jsonlite)
  library(statmod)
})

qualification <- fromJSON(file.path(run_dir, "04_EDGER_QUALIFICATION.json"), simplifyVector = FALSE)
if (!identical(qualification$status, "PASS_C5B_EDGER_QUALIFICATION")) {
  stop("The C5B edgeR qualification gate has not passed; real effects remain locked")
}
if (!identical(qualification$real_effect_estimates_inspected, FALSE)) {
  stop("C5B qualification contract is inconsistent")
}

export_audit <- fromJSON(file.path(run_dir, "03_MATRIX_EXPORT_AUDIT.json"), simplifyVector = FALSE)
genes <- read.csv(
  file.path(run_dir, export_audit$gene_metadata_relative_path),
  check.names = FALSE,
  stringsAsFactors = FALSE
)
programs <- read.csv(
  file.path(c5a_dir, "10_FROZEN_PROGRAM_DICTIONARY.csv"),
  check.names = FALSE,
  stringsAsFactors = FALSE,
  fileEncoding = "UTF-8-BOM"
)
if (!all(c("program_id", "analysis_family", "gene_symbol", "sign") %in% names(programs))) {
  stop("C5A program dictionary columns were not decoded correctly")
}
flag_columns <- c("is_mitochondrial", "is_ribosomal", "is_hemoglobin", "is_immunoglobulin")
for (column in flag_columns) {
  genes[[column]] <- tolower(as.character(genes[[column]])) %in% c("true", "1", "yes")
}

gene_output_dir <- file.path(run_dir, "05_gene_results")
dir.create(gene_output_dir, recursive = TRUE, showWarnings = FALSE)

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
  fitted <- as.numeric(design %*% beta)
  residual <- response - fitted
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

score_programs <- function(symbol_logcpm, samples, design, effect_column, analysis_name) {
  output <- list()
  score_values <- list()
  for (program_id in unique(programs$program_id)) {
    dictionary <- programs[programs$program_id == program_id, , drop = FALSE]
    positive <- unique(dictionary$gene_symbol[dictionary$sign == 1])
    negative <- unique(dictionary$gene_symbol[dictionary$sign == -1])
    positive_available <- intersect(positive, rownames(symbol_logcpm))
    negative_available <- intersect(negative, rownames(symbol_logcpm))
    positive_fraction <- if (length(positive) == 0L) 1 else length(positive_available) / length(positive)
    negative_fraction <- if (length(negative) == 0L) 1 else length(negative_available) / length(negative)
    availability_pass <- positive_fraction >= 0.8 && negative_fraction >= 0.8

    signed_parts <- list()
    if (length(positive_available) > 0L) {
      values <- symbol_logcpm[positive_available, , drop = FALSE]
      deviations <- sqrt(rowSums((values - rowMeans(values)) ^ 2) / (ncol(values) - 1))
      values <- values[deviations > 0, , drop = FALSE]
      z_values <- (values - rowMeans(values)) /
        sqrt(rowSums((values - rowMeans(values)) ^ 2) / (ncol(values) - 1))
      signed_parts$positive <- colMeans(z_values)
    }
    if (length(negative_available) > 0L) {
      values <- symbol_logcpm[negative_available, , drop = FALSE]
      deviations <- sqrt(rowSums((values - rowMeans(values)) ^ 2) / (ncol(values) - 1))
      values <- values[deviations > 0, , drop = FALSE]
      z_values <- (values - rowMeans(values)) /
        sqrt(rowSums((values - rowMeans(values)) ^ 2) / (ncol(values) - 1))
      signed_parts$negative <- colMeans(z_values)
    }
    score <- rep(0, nrow(samples))
    if (!is.null(signed_parts$positive)) score <- score + signed_parts$positive
    if (!is.null(signed_parts$negative)) score <- score - signed_parts$negative
    fit <- hc3_fit(score, design, effect_column)
    output[[length(output) + 1L]] <- data.frame(
      analysis_name = analysis_name,
      program_id = program_id,
      program_label = dictionary$program_label[[1]],
      analysis_family = dictionary$analysis_family[[1]],
      publication_role = dictionary$publication_role[[1]],
      positive_available = length(positive_available),
      positive_total = length(positive),
      negative_available = length(negative_available),
      negative_total = length(negative),
      availability_pass = availability_pass,
      effect = fit$effect,
      se_hc3 = fit$se_hc3,
      ci_low = fit$ci_low,
      ci_high = fit$ci_high,
      statistic = fit$statistic,
      df = fit$df,
      p_value = fit$p_value,
      stringsAsFactors = FALSE
    )
    score_values[[length(score_values) + 1L]] <- data.frame(
      analysis_name = analysis_name,
      sample_id = samples$sample_id,
      donor_name = samples$donor_name,
      cohort = samples$cohort,
      disease_group = samples$disease_group,
      program_id = program_id,
      score = score,
      stringsAsFactors = FALSE
    )
  }
  table <- do.call(rbind, output)
  table$q_value_primary4 <- NA_real_
  primary_rows <- table$analysis_family == "primary_confirmatory"
  table$q_value_primary4[primary_rows] <- p.adjust(table$p_value[primary_rows], method = "BH")
  list(results = table, scores = do.call(rbind, score_values))
}

prepare_symbol_logcpm <- function(counts, y_all) {
  symbol_group <- as.character(genes$gene_symbol)
  missing <- is.na(symbol_group) | symbol_group == ""
  symbol_group[missing] <- genes$ensembl_id[missing]
  symbol_counts <- rowsum(counts, group = symbol_group, reorder = FALSE)
  effective_library <- y_all$samples$lib.size * y_all$samples$norm.factors
  cpm(symbol_counts, log = TRUE, prior.count = 2, lib.size = effective_library)
}

fit_one_analysis <- function(definition) {
  analysis_name <- definition$analysis_name
  cat("[C5B] Fitting ", analysis_name, "\n", sep = "")
  counts <- as.matrix(read_sparse(file.path(run_dir, definition$matrix_relative_path)))
  samples <- read.csv(
    file.path(run_dir, definition$sample_relative_path),
    check.names = FALSE,
    stringsAsFactors = FALSE
  )
  rownames(counts) <- genes$ensembl_id
  colnames(counts) <- samples$sample_id
  design_columns <- unlist(definition$design_columns, use.names = FALSE)
  design <- as.matrix(samples[, design_columns, drop = FALSE])
  storage.mode(design) <- "double"
  if (qr(design)$rank != ncol(design)) stop("Rank-deficient model: ", analysis_name)

  y_all <- DGEList(counts = counts)
  y_all <- normLibSizes(y_all, method = "TMM")
  keep <- filterByExpr(y_all, design = design)
  y <- y_all[keep, , keep.lib.sizes = FALSE]
  y <- estimateDisp(y, design, robust = TRUE)
  fit <- glmQLFit(y, design, robust = TRUE)
  test <- glmQLFTest(fit, coef = definition$effect_column)
  tested <- topTags(test, n = Inf, sort.by = "none")$table
  tested$ensembl_id <- rownames(tested)
  tested$FDR <- p.adjust(tested$PValue, method = "BH")
  complete <- merge(genes, tested, by = "ensembl_id", all.x = TRUE, sort = FALSE)
  complete <- complete[match(genes$ensembl_id, complete$ensembl_id), , drop = FALSE]
  complete$tested_filterByExpr <- complete$ensembl_id %in% rownames(y)
  complete$analysis_name <- analysis_name
  complete <- complete[, c(
    "analysis_name", "ensembl_id", "gene_symbol", "gene_symbol_upper",
    "is_mitochondrial", "is_ribosomal", "is_hemoglobin", "is_immunoglobulin",
    "tested_filterByExpr", "logFC", "logCPM", "F", "PValue", "FDR"
  )]
  gene_path <- file.path(gene_output_dir, paste0(analysis_name, "_gene_results.csv.gz"))
  connection <- gzfile(gene_path, open = "wt", compression = 6)
  write.csv(complete, connection, row.names = FALSE, na = "")
  close(connection)

  top <- complete[complete$tested_filterByExpr, , drop = FALSE]
  top <- head(top[order(top$PValue), , drop = FALSE], 100L)
  symbol_logcpm <- prepare_symbol_logcpm(counts, y_all)
  scored <- score_programs(symbol_logcpm, samples, design, definition$effect_column, analysis_name)

  tested_for_camera <- complete[complete$tested_filterByExpr, , drop = FALSE]
  signed_statistic <- sign(tested_for_camera$logFC) * sqrt(pmax(tested_for_camera$F, 0))
  arm_results <- list()
  for (program_id in unique(programs$program_id)) {
    dictionary <- programs[programs$program_id == program_id, , drop = FALSE]
    for (arm_sign in c(1, -1)) {
      arm_genes <- unique(dictionary$gene_symbol[dictionary$sign == arm_sign])
      if (length(arm_genes) == 0L) next
      index <- which(tested_for_camera$gene_symbol %in% arm_genes)
      if (length(index) < 2L) next
      camera <- cameraPR(
        statistic = signed_statistic,
        index = list(frozen_arm = index),
        use.ranks = TRUE,
        inter.gene.cor = 0.01,
        sort = FALSE,
        directional = TRUE
      )
      expected_sign <- if (arm_sign == 1) 1 else -1
      arm_results[[length(arm_results) + 1L]] <- data.frame(
        analysis_name = analysis_name,
        program_id = program_id,
        program_label = dictionary$program_label[[1]],
        analysis_family = dictionary$analysis_family[[1]],
        arm = if (arm_sign == 1) "positive" else "negative",
        n_genes = length(index),
        camera_direction = camera$Direction[[1]],
        camera_p_value = camera$PValue[[1]],
        expected_direction_fraction = mean(sign(tested_for_camera$logFC[index]) == expected_sign),
        median_expected_logFC = median(tested_for_camera$logFC[index] * expected_sign),
        stringsAsFactors = FALSE
      )
    }
  }
  arms <- do.call(rbind, arm_results)
  arms$camera_fdr_within_analysis <- p.adjust(arms$camera_p_value, method = "BH")

  summary <- data.frame(
    analysis_name = analysis_name,
    analysis_role = definition$analysis_role,
    n_samples = nrow(samples),
    reference_n = nrow(samples) - sum(samples[[definition$effect_column]]),
    exposed_n = sum(samples[[definition$effect_column]]),
    design_rank = qr(design)$rank,
    design_columns = paste(design_columns, collapse = ";"),
    tested_genes = sum(keep),
    fdr_0_05_genes = sum(tested$FDR < 0.05),
    up_fdr_0_05 = sum(tested$FDR < 0.05 & tested$logFC > 0),
    down_fdr_0_05 = sum(tested$FDR < 0.05 & tested$logFC < 0),
    common_dispersion = y$common.dispersion,
    median_tagwise_dispersion = median(y$tagwise.dispersion),
    stringsAsFactors = FALSE
  )
  list(
    summary = summary,
    complete = complete,
    top = top,
    programs = scored$results,
    scores = scored$scores,
    pathways = arms,
    design = design,
    samples = samples,
    symbol_logcpm = symbol_logcpm
  )
}

fits <- list()
for (definition in export_audit$analyses) {
  fits[[definition$analysis_name]] <- fit_one_analysis(definition)
}

model_summary <- do.call(rbind, lapply(fits, `[[`, "summary"))
top_genes <- do.call(rbind, lapply(fits, `[[`, "top"))
program_results <- do.call(rbind, lapply(fits, `[[`, "programs"))
program_scores <- do.call(rbind, lapply(fits, `[[`, "scores"))
pathway_results <- do.call(rbind, lapply(fits, `[[`, "pathways"))
write.csv(model_summary, file.path(run_dir, "05_MODEL_SUMMARY.csv"), row.names = FALSE)
write.csv(top_genes, file.path(run_dir, "06_TOP100_GENE_RESULTS.csv"), row.names = FALSE)
write.csv(program_results, file.path(run_dir, "07_PROGRAM_RESULTS.csv"), row.names = FALSE)
score_connection <- gzfile(file.path(run_dir, "08_PROGRAM_SAMPLE_SCORES.csv.gz"), open = "wt")
write.csv(program_scores, score_connection, row.names = FALSE)
close(score_connection)
write.csv(pathway_results, file.path(run_dir, "09_FROZEN_PROGRAM_ARM_CAMERA.csv"), row.names = FALSE)

# Donor influence in the frozen childhood primary analysis.
primary_fit <- fits$childhood_min50
primary_rows <- program_results$analysis_name == "childhood_min50"
loo_program <- list()
for (program_id in unique(program_results$program_id[primary_rows])) {
  full <- program_results[primary_rows & program_results$program_id == program_id, , drop = FALSE]
  score <- primary_fit$scores$score[primary_fit$scores$program_id == program_id]
  estimates <- numeric(length(score))
  for (index in seq_along(score)) {
    estimates[index] <- hc3_fit(
      score[-index], primary_fit$design[-index, , drop = FALSE], "is_sle"
    )$effect
  }
  full_effect <- full$effect[[1]]
  loo_program[[length(loo_program) + 1L]] <- data.frame(
    program_id = program_id,
    program_label = full$program_label[[1]],
    analysis_family = full$analysis_family[[1]],
    full_effect = full_effect,
    loo_min_effect = min(estimates),
    loo_max_effect = max(estimates),
    loo_max_absolute_delta = max(abs(estimates - full_effect)),
    loo_sign_concordance = mean(sign(estimates) == sign(full_effect)),
    loo_any_sign_flip = any(sign(estimates) != sign(full_effect)),
    most_influential_sample_id = primary_fit$samples$sample_id[[which.max(abs(estimates - full_effect))]],
    stringsAsFactors = FALSE
  )
}
loo_program <- do.call(rbind, loo_program)
write.csv(loo_program, file.path(run_dir, "10_PRIMARY_PROGRAM_DONOR_LOO.csv"), row.names = FALSE)

confirmatory_symbols <- unique(programs$gene_symbol[programs$analysis_family == "primary_confirmatory"])
confirmatory_symbols <- intersect(confirmatory_symbols, rownames(primary_fit$symbol_logcpm))
loo_genes <- list()
for (symbol in confirmatory_symbols) {
  expression <- primary_fit$symbol_logcpm[symbol, ]
  full <- hc3_fit(expression, primary_fit$design, "is_sle")
  estimates <- numeric(length(expression))
  for (index in seq_along(expression)) {
    estimates[index] <- hc3_fit(
      expression[-index], primary_fit$design[-index, , drop = FALSE], "is_sle"
    )$effect
  }
  loo_genes[[length(loo_genes) + 1L]] <- data.frame(
    gene_symbol = symbol,
    full_logcpm_effect_hc3 = full$effect,
    full_p_value_hc3 = full$p_value,
    loo_min_effect = min(estimates),
    loo_max_effect = max(estimates),
    loo_max_absolute_delta = max(abs(estimates - full$effect)),
    loo_sign_concordance = mean(sign(estimates) == sign(full$effect)),
    loo_any_sign_flip = any(sign(estimates) != sign(full$effect)),
    most_influential_sample_id = primary_fit$samples$sample_id[[which.max(abs(estimates - full$effect))]],
    stringsAsFactors = FALSE
  )
}
loo_genes <- do.call(rbind, loo_genes)
loo_genes$q_value_confirmatory_genes <- p.adjust(loo_genes$full_p_value_hc3, method = "BH")
write.csv(loo_genes, file.path(run_dir, "11_PRIMARY_CONFIRMATORY_GENE_DONOR_LOO.csv"), row.names = FALSE)

# Source-label omission retains the primary donor set and refits program normalization.
source_label_results <- list()
for (definition in export_audit$source_label_sensitivities) {
  counts <- as.matrix(read_sparse(file.path(run_dir, definition$matrix_relative_path)))
  samples <- read.csv(
    file.path(run_dir, definition$sample_relative_path), check.names = FALSE, stringsAsFactors = FALSE
  )
  rownames(counts) <- genes$ensembl_id
  colnames(counts) <- samples$sample_id
  design_columns <- unlist(definition$design_columns, use.names = FALSE)
  design <- as.matrix(samples[, design_columns, drop = FALSE])
  storage.mode(design) <- "double"
  y_all <- normLibSizes(DGEList(counts = counts), method = "TMM")
  symbol_logcpm <- prepare_symbol_logcpm(counts, y_all)
  scored <- score_programs(symbol_logcpm, samples, design, "is_sle", definition$analysis_name)$results
  scored$omitted_source_label <- definition$omitted_source_label
  scored$minimum_cells_after_omission <- definition$minimum_cells_after_omission
  source_label_results[[length(source_label_results) + 1L]] <- scored
}
source_label_results <- do.call(rbind, source_label_results)
write.csv(source_label_results, file.path(run_dir, "12_SOURCE_LABEL_LOO_PROGRAM_RESULTS.csv"), row.names = FALSE)

compare_effects <- function(reference_name, target_name, label, seed) {
  reference <- fits[[reference_name]]$complete
  target <- fits[[target_name]]$complete
  merged <- merge(
    reference[reference$tested_filterByExpr, c("ensembl_id", "gene_symbol", "logFC", "PValue")],
    target[target$tested_filterByExpr, c("ensembl_id", "logFC", "PValue")],
    by = "ensembl_id", suffixes = c("_reference", "_target")
  )
  set.seed(seed)
  correlations <- replicate(500L, {
    index <- sample.int(nrow(merged), replace = TRUE)
    suppressWarnings(cor(merged$logFC_reference[index], merged$logFC_target[index], method = "spearman"))
  })
  leading <- head(merged[order(merged$PValue_reference), , drop = FALSE], 500L)
  concordant <- sign(leading$logFC_reference) == sign(leading$logFC_target)
  interval <- binom.test(sum(concordant), length(concordant))$conf.int
  data.frame(
    comparison = label,
    shared_tested_genes = nrow(merged),
    spearman_rho = suppressWarnings(cor(merged$logFC_reference, merged$logFC_target, method = "spearman")),
    spearman_bootstrap_ci_low = quantile(correlations, 0.025, na.rm = TRUE),
    spearman_bootstrap_ci_high = quantile(correlations, 0.975, na.rm = TRUE),
    leading_primary_n = nrow(leading),
    leading_direction_concordance = mean(concordant),
    leading_concordance_ci_low = interval[[1]],
    leading_concordance_ci_high = interval[[2]],
    stringsAsFactors = FALSE
  )
}
external_concordance <- rbind(
  compare_effects("childhood_min50", "combined_min50", "childhood_vs_combined", 2026081521L),
  compare_effects("childhood_min50", "adult_min50", "childhood_vs_adult", 2026081522L),
  compare_effects("combined_min50", "adult_min50", "combined_vs_adult", 2026081523L)
)
write.csv(external_concordance, file.path(run_dir, "13_EXTERNAL_GENE_EFFECT_CONCORDANCE.csv"), row.names = FALSE)

primary_tested <- primary_fit$complete[primary_fit$complete$tested_filterByExpr, , drop = FALSE]
primary_tested <- primary_tested[order(primary_tested$PValue), , drop = FALSE]
qc_audit <- data.frame(
  rank_cutoff = c(50L, 100L, 500L),
  mitochondrial_fraction = NA_real_, ribosomal_fraction = NA_real_,
  hemoglobin_fraction = NA_real_, immunoglobulin_fraction = NA_real_
)
for (index in seq_len(nrow(qc_audit))) {
  leading <- head(primary_tested, qc_audit$rank_cutoff[[index]])
  qc_audit$mitochondrial_fraction[[index]] <- mean(leading$is_mitochondrial)
  qc_audit$ribosomal_fraction[[index]] <- mean(leading$is_ribosomal)
  qc_audit$hemoglobin_fraction[[index]] <- mean(leading$is_hemoglobin)
  qc_audit$immunoglobulin_fraction[[index]] <- mean(leading$is_immunoglobulin)
}
write.csv(qc_audit, file.path(run_dir, "14_PRIMARY_RANKED_QC_FAMILY_AUDIT.csv"), row.names = FALSE)

status <- list(
  created_at = format(Sys.time(), "%Y-%m-%dT%H:%M:%S%z"),
  status = "C5B_FROZEN_MODELS_COMPLETE_REVIEW_REQUIRED",
  qualification_status = qualification$status,
  real_effect_estimates_inspected = TRUE,
  analyses_completed = names(fits),
  source_label_sensitivities_completed = length(export_audit$source_label_sensitivities),
  model_summary = lapply(seq_len(nrow(model_summary)), function(index) as.list(model_summary[index, ])),
  output_contract = list(
    gene_key = "Ensembl ID",
    normalization = "edgeR TMM",
    filter = "filterByExpr before coefficient testing",
    model = "edgeR robust quasi-likelihood",
    gene_multiplicity = "BH within contrast",
    program_uncertainty = "OLS HC3 sandwich",
    program_multiplicity = "BH across four frozen confirmatory programs within contrast"
  )
)
write_json(status, file.path(run_dir, "15_FROZEN_MODEL_RUN_STATUS.json"), pretty = TRUE, auto_unbox = TRUE)
cat(toJSON(status, pretty = TRUE, auto_unbox = TRUE), "\n")
