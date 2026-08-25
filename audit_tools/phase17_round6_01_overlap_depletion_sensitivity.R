#!/usr/bin/env Rscript

# Round 6: prespecified STAT1/STAT2 IFN-overlap depletion sensitivity.

args <- commandArgs(trailingOnly = TRUE)
options(warn = 1)
if (length(args) != 2L) {
  stop("Usage: phase17_round6_01_overlap_depletion_sensitivity.R <project_root> <output_dir>")
}

root <- normalizePath(args[[1]], winslash = "/", mustWork = TRUE)
output_dir <- normalizePath(args[[2]], winslash = "/", mustWork = FALSE)
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

suppressPackageStartupMessages({
  library(Matrix)
  library(edgeR)
  library(limma)
  library(jsonlite)
})

as_bool <- function(value) {
  tolower(as.character(value)) %in% c("true", "1", "yes")
}

read_sparse <- function(path) {
  connection <- gzfile(path, open = "rt")
  on.exit(close(connection), add = TRUE)
  as(readMM(connection), "CsparseMatrix")
}

find_definition <- function(audit, analysis_name) {
  definitions <- audit$analyses
  if (!is.null(audit$source_label_sensitivities)) {
    definitions <- c(definitions, audit$source_label_sensitivities)
  }
  matches <- vapply(
    definitions,
    function(definition) identical(definition$analysis_name, analysis_name),
    logical(1)
  )
  if (sum(matches) != 1L) {
    stop("Expected one matrix definition for ", analysis_name, "; found ", sum(matches))
  }
  definitions[[which(matches)]]
}

freeze_regulator <- function(network_raw, regulator) {
  selected <- network_raw[network_raw$source_genesymbol == regulator, , drop = FALSE]
  targets <- split(selected, toupper(trimws(selected$target_genesymbol)))
  frozen <- lapply(targets, function(rows) {
    signs <- numeric(0)
    if (any(as_bool(rows$consensus_stimulation))) signs <- c(signs, 1)
    if (any(as_bool(rows$consensus_inhibition))) signs <- c(signs, -1)
    signs <- unique(signs)
    if (length(signs) == 1L) signs[[1]] else NA_real_
  })
  frozen <- unlist(frozen)
  frozen[is.finite(frozen)]
}

read_ranked_statistics <- function(path, symbol_field) {
  table <- read.csv(path, check.names = FALSE, stringsAsFactors = FALSE)
  tested <- as_bool(table$tested_filterByExpr)
  if (!(symbol_field %in% names(table))) {
    if (identical(symbol_field, "gene_symbol_upper") && "gene_symbol" %in% names(table)) {
      symbols <- toupper(trimws(table$gene_symbol))
    } else {
      stop("Missing ranked-statistic symbol field ", symbol_field, " in ", path)
    }
  } else {
    symbols <- toupper(trimws(table[[symbol_field]]))
  }
  valid <- tested & !is.na(symbols) & symbols != "" & is.finite(table$logFC) & is.finite(table$F)
  if (any(table$F[valid] < 0)) stop("Negative F statistic in ", path)
  statistic <- sign(table$logFC[valid]) * sqrt(table$F[valid])
  averaged <- tapply(statistic, symbols[valid], mean)
  averaged[sort(names(averaged))]
}

fit_ulm <- function(statistics, weights) {
  symbols <- names(statistics)
  matched <- intersect(names(weights), symbols)
  x <- numeric(length(statistics))
  names(x) <- symbols
  x[matched] <- weights[matched]
  n <- length(x)
  centered_x <- x - mean(x)
  centered_y <- statistics - mean(statistics)
  sxx <- sum(centered_x^2)
  if (!is.finite(sxx) || sxx <= 0) stop("ULM predictor has zero variance")
  slope <- sum(centered_x * centered_y) / sxx
  intercept <- mean(statistics) - slope * mean(x)
  residual <- statistics - intercept - slope * x
  degrees_freedom <- n - 2L
  standard_error <- sqrt((sum(residual^2) / degrees_freedom) / sxx)
  t_statistic <- slope / standard_error
  critical <- qt(0.975, df = degrees_freedom)
  list(
    matched = matched,
    estimate = slope,
    standard_error = standard_error,
    statistic = t_statistic,
    degrees_freedom = degrees_freedom,
    ci_low = slope - critical * standard_error,
    ci_high = slope + critical * standard_error,
    p_value = 2 * pt(abs(t_statistic), df = degrees_freedom, lower.tail = FALSE)
  )
}

network_path <- file.path(
  root,
  "phase17_v7/gateC6B/20260815_pre_effect_resource_freeze/resources/collectri_human_omnipath_20260815.tsv.gz"
)
network_raw <- read.delim(gzfile(network_path), check.names = FALSE, stringsAsFactors = FALSE)
regulators <- c("STAT1", "STAT2")
frozen_network <- setNames(lapply(regulators, function(x) freeze_regulator(network_raw, x)), regulators)
expected_frozen_counts <- c(STAT1 = 291L, STAT2 = 50L)
observed_frozen_counts <- vapply(frozen_network, length, integer(1))
if (!identical(observed_frozen_counts, expected_frozen_counts)) {
  stop("Frozen CollecTRI counts changed: ", paste(names(observed_frozen_counts), observed_frozen_counts, collapse = "; "))
}

program_dictionary <- read.csv(
  file.path(root, "phase17_v7/gateC4A/20260815_raw_pseudobulk_freeze/11_program_dictionary.csv"),
  check.names = FALSE,
  stringsAsFactors = FALSE
)
program_ids <- as.character(program_dictionary[[1]])
ifn12 <- unique(toupper(program_dictionary$gene_symbol[
  program_ids == "IFN_ISG" & program_dictionary$sign > 0
]))
if (length(ifn12) != 12L) stop("Expected exactly 12 frozen positive IFN/ISG genes")

m5911_table <- read.csv(
  file.path(root, "phase17_v7/gateC6B/20260815_pre_effect_resource_freeze/05_MSIGDB_M5911_GENE_SET.csv"),
  check.names = FALSE,
  stringsAsFactors = FALSE
)
m5911 <- unique(toupper(trimws(m5911_table$gene_symbol)))
if (length(m5911) != 97L || any(m5911 == "")) stop("Expected exactly 97 unique M5911 genes")

branches <- list(
  baseline = character(0),
  frozen_ifn12_depleted = ifn12,
  m5911_depleted = m5911
)

contrasts <- list(
  list(
    contrast = "gse174188_primary",
    run_dir = "phase17_v7/gateC4B/20260815_edger_transcription",
    analysis_name = "primary_base",
    symbol_field = "feature_name"
  ),
  list(
    contrast = "gse174188_internal_nonoverlap",
    run_dir = "phase17_v7/gateC4B/20260815_edger_transcription",
    analysis_name = "validation_nonoverlap",
    symbol_field = "feature_name"
  ),
  list(
    contrast = "gse135779_childhood",
    run_dir = "phase17_v7/gateC5B/20260815_gse135779_external_validation",
    analysis_name = "childhood_min50",
    symbol_field = "gene_symbol_upper"
  )
)

frozen_ulm <- read.csv(
  file.path(root, "phase17_v7/gateC6B/20260815_regulatory_evidence/01_CONFIRMATORY_REGULATOR_RESULTS.csv"),
  check.names = FALSE,
  stringsAsFactors = FALSE
)
frozen_ulm <- frozen_ulm[frozen_ulm$regulator %in% regulators, , drop = FALSE]

result_rows <- list()
loo_rows <- list()
input_audit <- list()

for (contrast_definition in contrasts) {
  run_dir <- file.path(root, contrast_definition$run_dir)
  audit <- fromJSON(file.path(run_dir, "03_MATRIX_EXPORT_AUDIT.json"), simplifyVector = FALSE)
  definition <- find_definition(audit, contrast_definition$analysis_name)
  genes <- read.csv(
    file.path(run_dir, audit$gene_metadata_relative_path),
    check.names = FALSE,
    stringsAsFactors = FALSE
  )
  counts <- as.matrix(read_sparse(file.path(run_dir, definition$matrix_relative_path)))
  samples <- read.csv(
    file.path(run_dir, definition$sample_relative_path),
    check.names = FALSE,
    stringsAsFactors = FALSE
  )
  rownames(counts) <- genes$ensembl_id

  symbol_field <- contrast_definition$symbol_field
  if (!(symbol_field %in% names(genes))) {
    if (identical(symbol_field, "gene_symbol_upper") && "gene_symbol" %in% names(genes)) {
      symbols <- toupper(trimws(genes$gene_symbol))
    } else {
      stop("Missing count-matrix symbol field ", symbol_field)
    }
  } else {
    symbols <- toupper(trimws(genes[[symbol_field]]))
  }
  missing_symbols <- is.na(symbols) | symbols == ""
  symbols[missing_symbols] <- genes$ensembl_id[missing_symbols]
  symbol_counts <- rowsum(counts, group = symbols, reorder = FALSE)

  ranked_path <- file.path(
    run_dir,
    "05_gene_results",
    paste0(contrast_definition$analysis_name, "_gene_results.csv.gz")
  )
  ranked <- read_ranked_statistics(ranked_path, symbol_field)
  background <- intersect(names(ranked), rownames(symbol_counts))
  symbol_counts <- symbol_counts[background, , drop = FALSE]

  design_columns <- unlist(definition$design_columns, use.names = FALSE)
  design <- as.matrix(samples[, design_columns, drop = FALSE])
  storage.mode(design) <- "double"
  if (qr(design)$rank != ncol(design)) stop("Rank-deficient design")
  dge <- DGEList(counts = symbol_counts)
  dge <- normLibSizes(dge, method = "TMM")
  voom_data <- voom(dge, design = design, plot = FALSE)

  input_audit[[length(input_audit) + 1L]] <- list(
    contrast = contrast_definition$contrast,
    analysis_name = contrast_definition$analysis_name,
    n_samples = nrow(samples),
    design_rank = qr(design)$rank,
    ranked_symbols = length(ranked),
    camera_fry_background_symbols = length(background),
    effect_column = definition$effect_column
  )

  for (regulator in regulators) {
    base_weights <- frozen_network[[regulator]]
    baseline_ulm <- fit_ulm(ranked, base_weights)
    frozen_row <- frozen_ulm[
      frozen_ulm$contrast == contrast_definition$contrast & frozen_ulm$regulator == regulator,
      ,
      drop = FALSE
    ]
    if (nrow(frozen_row) != 1L) stop("Missing frozen ULM row")
    if (length(baseline_ulm$matched) != frozen_row$matched_targets) stop("Baseline ULM target count mismatch")
    if (abs(baseline_ulm$estimate - frozen_row$slope) > 1e-8) stop("Baseline ULM slope mismatch")

    for (branch_name in names(branches)) {
      depleted_genes <- branches[[branch_name]]
      branch_weights <- base_weights[!(names(base_weights) %in% depleted_genes)]
      ulm_result <- fit_ulm(ranked, branch_weights)
      removed_ulm <- intersect(names(base_weights), intersect(names(ranked), depleted_genes))

      matched <- intersect(names(branch_weights), rownames(voom_data$E))
      removed_camera <- intersect(names(base_weights), intersect(rownames(voom_data$E), depleted_genes))
      if (length(matched) != length(ulm_result$matched)) {
        stop("ULM and CAMERA/FRY target counts differ for ", contrast_definition$contrast, "/", regulator, "/", branch_name)
      }
      signed_voom <- voom_data
      signed_voom$E[matched, ] <- signed_voom$E[matched, , drop = FALSE] * as.numeric(branch_weights[matched])
      camera_result <- camera(
        signed_voom,
        index = list(frozen_signed_regulon = matched),
        design = design,
        contrast = definition$effect_column,
        use.ranks = TRUE,
        allow.neg.cor = FALSE,
        inter.gene.cor = NA,
        sort = FALSE,
        directional = TRUE
      )
      fry_result <- fry(
        signed_voom,
        index = list(frozen_signed_regulon = matched),
        design = design,
        contrast = definition$effect_column,
        sort = FALSE
      )

      shared <- list(
        branch = branch_name,
        contrast = contrast_definition$contrast,
        regulator = regulator,
        matched_targets_before = length(baseline_ulm$matched),
        removed_targets = length(removed_ulm),
        matched_targets_after = length(ulm_result$matched),
        target_retention_fraction = length(ulm_result$matched) / length(baseline_ulm$matched),
        baseline_ulm_slope = baseline_ulm$estimate
      )
      result_rows[[length(result_rows) + 1L]] <- data.frame(
        shared,
        method = "ULM",
        estimate = ulm_result$estimate,
        standard_error = ulm_result$standard_error,
        ci_low = ulm_result$ci_low,
        ci_high = ulm_result$ci_high,
        direction = if (ulm_result$estimate > 0) "Up" else if (ulm_result$estimate < 0) "Down" else "Flat",
        p_value = ulm_result$p_value,
        inter_gene_correlation = NA_real_,
        attenuation_ratio_vs_baseline = ulm_result$estimate / baseline_ulm$estimate,
        stringsAsFactors = FALSE
      )
      result_rows[[length(result_rows) + 1L]] <- data.frame(
        shared,
        method = "CAMERA",
        estimate = NA_real_,
        standard_error = NA_real_,
        ci_low = NA_real_,
        ci_high = NA_real_,
        direction = camera_result$Direction[[1]],
        p_value = camera_result$PValue[[1]],
        inter_gene_correlation = camera_result$Correlation[[1]],
        attenuation_ratio_vs_baseline = NA_real_,
        stringsAsFactors = FALSE
      )
      result_rows[[length(result_rows) + 1L]] <- data.frame(
        shared,
        method = "FRY",
        estimate = NA_real_,
        standard_error = NA_real_,
        ci_low = NA_real_,
        ci_high = NA_real_,
        direction = fry_result$Direction[[1]],
        p_value = fry_result$PValue[[1]],
        inter_gene_correlation = NA_real_,
        attenuation_ratio_vs_baseline = NA_real_,
        stringsAsFactors = FALSE
      )

      if (!identical(branch_name, "baseline") && length(ulm_result$matched) >= 10L) {
        for (deleted_target in ulm_result$matched) {
          loo_weights <- branch_weights[names(branch_weights) != deleted_target]
          loo_result <- fit_ulm(ranked, loo_weights)
          loo_rows[[length(loo_rows) + 1L]] <- data.frame(
            branch = branch_name,
            contrast = contrast_definition$contrast,
            regulator = regulator,
            deleted_target = deleted_target,
            matched_targets_after_depletion = length(ulm_result$matched),
            loo_slope = loo_result$estimate,
            same_direction_as_depleted = sign(loo_result$estimate) == sign(ulm_result$estimate),
            stringsAsFactors = FALSE
          )
        }
      }
      if (!identical(sort(removed_ulm), sort(removed_camera))) {
        stop("Removed target identity differs between ULM and CAMERA/FRY")
      }
    }
  }
}

results <- do.call(rbind, result_rows)
results$q_value <- NA_real_
results$multiplicity_family <- NA_character_
for (branch_name in names(branches)) {
  for (method_name in c("ULM", "CAMERA", "FRY")) {
    selected <- results$branch == branch_name & results$method == method_name
    if (sum(selected) != 6L) stop("Expected six tests per branch and method")
    if (identical(branch_name, "baseline") && identical(method_name, "ULM")) {
      lookup <- paste(frozen_ulm$contrast, frozen_ulm$regulator, sep = "|")
      current <- paste(results$contrast[selected], results$regulator[selected], sep = "|")
      results$q_value[selected] <- frozen_ulm$q_value_global24[match(current, lookup)]
      results$multiplicity_family[selected] <- "frozen_global_24"
    } else {
      results$q_value[selected] <- p.adjust(results$p_value[selected], method = "BH")
      results$multiplicity_family[selected] <- if (
        identical(branch_name, "baseline")
      ) "baseline_core_6" else paste0(branch_name, "_", tolower(method_name), "_core_6")
    }
  }
}
results$expected_direction <- results$direction == "Up"
results$ci_excludes_zero <- ifelse(
  results$method == "ULM",
  results$ci_low > 0 | results$ci_high < 0,
  NA
)

write.csv(results, file.path(output_dir, "01_OVERLAP_DEPLETION_RESULTS.csv"), row.names = FALSE)

if (length(loo_rows)) {
  loo <- do.call(rbind, loo_rows)
  write.csv(loo, file.path(output_dir, "02_ULM_LEAVE_ONE_TARGET.csv"), row.names = FALSE)
  loo_summary <- do.call(
    rbind,
    lapply(split(loo, list(loo$branch, loo$contrast, loo$regulator), drop = TRUE), function(rows) {
      data.frame(
        branch = rows$branch[[1]],
        contrast = rows$contrast[[1]],
        regulator = rows$regulator[[1]],
        matched_targets_after_depletion = rows$matched_targets_after_depletion[[1]],
        loo_tests = nrow(rows),
        minimum_loo_slope = min(rows$loo_slope),
        maximum_loo_slope = max(rows$loo_slope),
        same_direction_fraction = mean(rows$same_direction_as_depleted),
        all_same_direction = all(rows$same_direction_as_depleted),
        stringsAsFactors = FALSE
      )
    })
  )
  rownames(loo_summary) <- NULL
  write.csv(loo_summary, file.path(output_dir, "03_ULM_LEAVE_ONE_TARGET_SUMMARY.csv"), row.names = FALSE)
} else {
  loo_summary <- data.frame()
}

depleted <- results[results$branch != "baseline", , drop = FALSE]
method_summary <- do.call(
  rbind,
  lapply(split(depleted, list(depleted$branch, depleted$method), drop = TRUE), function(rows) {
    data.frame(
      branch = rows$branch[[1]],
      method = rows$method[[1]],
      tests = nrow(rows),
      directions_up = sum(rows$expected_direction),
      q_below_0_05 = sum(rows$q_value < 0.05),
      minimum_target_retention = min(rows$target_retention_fraction),
      minimum_ulm_attenuation = if (rows$method[[1]] == "ULM") min(rows$attenuation_ratio_vs_baseline) else NA_real_,
      stringsAsFactors = FALSE
    )
  })
)
rownames(method_summary) <- NULL
write.csv(method_summary, file.path(output_dir, "04_METHOD_SUMMARY.csv"), row.names = FALSE)

payload <- list(
  created_at = "2026-08-25",
  status = "COMPLETE_ROUND6_OVERLAP_DEPLETION_REVIEW_REQUIRED",
  governance = "post-freeze sensitivity; original primary results and multiplicity families unchanged",
  depletion_sets = list(
    frozen_ifn12 = sort(ifn12),
    frozen_ifn12_count = length(ifn12),
    m5911 = "HALLMARK_INTERFERON_ALPHA_RESPONSE",
    m5911_count = length(m5911)
  ),
  tests = nrow(results),
  depletion_tests = nrow(depleted),
  dedicated_families = 6L,
  all_depleted_directions_up = all(depleted$expected_direction),
  ulm_depleted_ci_excludes_zero = sum(depleted$method == "ULM" & depleted$ci_excludes_zero),
  ulm_depleted_tests = sum(depleted$method == "ULM"),
  minimum_ulm_attenuation = min(depleted$attenuation_ratio_vs_baseline[depleted$method == "ULM"]),
  minimum_target_retention = min(depleted$target_retention_fraction),
  method_summary = method_summary,
  leave_one_target = list(
    eligibility_threshold = 10L,
    eligible_models = nrow(loo_summary),
    all_eligible_models_preserve_direction = if (nrow(loo_summary)) all(loo_summary$all_same_direction) else NA
  ),
  interpretation_policy = paste(
    "Review direction, ULM attenuation and confidence intervals, target retention,",
    "dedicated six-test BH q values and CAMERA/FRY agreement; do not use P<0.05 alone."
  ),
  software = list(
    R = R.version.string,
    edgeR = as.character(packageVersion("edgeR")),
    limma = as.character(packageVersion("limma")),
    Matrix = as.character(packageVersion("Matrix"))
  ),
  input_audit = input_audit
)
writeLines(
  toJSON(payload, auto_unbox = TRUE, pretty = TRUE, digits = 12, na = "null"),
  file.path(output_dir, "05_OVERLAP_DEPLETION_STATUS.json"),
  useBytes = TRUE
)
cat(toJSON(payload, auto_unbox = TRUE, pretty = TRUE, digits = 12, na = "null"), "\n")
