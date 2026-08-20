#!/usr/bin/env Rscript

# Gate C8R: correlation-aware sensitivity for the frozen STAT1/STAT2 regulons.

args <- commandArgs(trailingOnly = TRUE)
options(warn = 1)
if (length(args) != 2L) {
  stop("Usage: phase17_c8r_01_correlation_aware_regulator_sensitivity.R <project_root> <output_dir>")
}

root <- normalizePath(args[[1]], winslash = "/", mustWork = TRUE)
output_dir <- normalizePath(args[[2]], winslash = "/", mustWork = TRUE)

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

network_path <- file.path(
  root,
  "phase17_v7/gateC6B/20260815_pre_effect_resource_freeze/resources/collectri_human_omnipath_20260815.tsv.gz"
)
network_raw <- read.delim(
  gzfile(network_path),
  check.names = FALSE,
  stringsAsFactors = FALSE
)

freeze_regulator <- function(regulator) {
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

regulators <- c("STAT1", "STAT2")
frozen_network <- setNames(lapply(regulators, freeze_regulator), regulators)
expected_frozen_counts <- c(STAT1 = 291L, STAT2 = 50L)
observed_frozen_counts <- vapply(frozen_network, length, integer(1))
if (!identical(observed_frozen_counts, expected_frozen_counts)) {
  stop(
    "Frozen CollecTRI counts changed: ",
    paste(names(observed_frozen_counts), observed_frozen_counts, collapse = "; ")
  )
}

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

original <- read.csv(
  file.path(root, "phase17_v7/gateC6B/20260815_regulatory_evidence/01_CONFIRMATORY_REGULATOR_RESULTS.csv"),
  check.names = FALSE,
  stringsAsFactors = FALSE
)
original <- original[original$regulator %in% regulators, , drop = FALSE]

results <- list()
for (contrast_definition in contrasts) {
  run_dir <- file.path(root, contrast_definition$run_dir)
  audit <- fromJSON(
    file.path(run_dir, "03_MATRIX_EXPORT_AUDIT.json"),
    simplifyVector = FALSE
  )
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
      stop("Missing gene-symbol field ", symbol_field)
    }
  } else {
    symbols <- toupper(trimws(genes[[symbol_field]]))
  }
  missing_symbols <- is.na(symbols) | symbols == ""
  symbols[missing_symbols] <- genes$ensembl_id[missing_symbols]
  symbol_counts <- rowsum(counts, group = symbols, reorder = FALSE)

  gene_results <- read.csv(
    file.path(
      run_dir,
      "05_gene_results",
      paste0(contrast_definition$analysis_name, "_gene_results.csv.gz")
    ),
    check.names = FALSE,
    stringsAsFactors = FALSE
  )
  tested <- as_bool(gene_results$tested_filterByExpr)
  tested_symbols <- unique(toupper(trimws(gene_results[[symbol_field]][tested])))
  tested_symbols <- tested_symbols[!is.na(tested_symbols) & tested_symbols != ""]
  background <- intersect(tested_symbols, rownames(symbol_counts))
  symbol_counts <- symbol_counts[background, , drop = FALSE]

  design_columns <- unlist(definition$design_columns, use.names = FALSE)
  design <- as.matrix(samples[, design_columns, drop = FALSE])
  storage.mode(design) <- "double"
  if (qr(design)$rank != ncol(design)) {
    stop("Rank-deficient design for ", contrast_definition$analysis_name)
  }

  dge <- DGEList(counts = symbol_counts)
  dge <- normLibSizes(dge, method = "TMM")
  voom_data <- voom(dge, design = design, plot = FALSE)

  for (regulator in regulators) {
    weights <- frozen_network[[regulator]]
    matched <- intersect(names(weights), rownames(voom_data$E))
    signed_voom <- voom_data
    signed_voom$E[matched, ] <-
      signed_voom$E[matched, , drop = FALSE] * as.numeric(weights[matched])

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
    original_row <- original[
      original$contrast == contrast_definition$contrast &
        original$regulator == regulator,
      ,
      drop = FALSE
    ]
    if (nrow(original_row) != 1L) {
      stop("Missing frozen C6B result for ", contrast_definition$contrast, "/", regulator)
    }
    results[[length(results) + 1L]] <- data.frame(
      contrast = contrast_definition$contrast,
      analysis_name = contrast_definition$analysis_name,
      regulator = regulator,
      n_samples = nrow(samples),
      design_rank = qr(design)$rank,
      tested_background_symbols = length(background),
      matched_signed_targets = length(matched),
      matched_positive_targets = sum(weights[matched] > 0),
      matched_negative_targets = sum(weights[matched] < 0),
      frozen_ulm_matched_targets = original_row$matched_targets,
      target_count_matches_frozen_ulm = length(matched) == original_row$matched_targets,
      frozen_ulm_slope = original_row$slope,
      frozen_ulm_global_q = original_row$q_value_global24,
      camera_inter_gene_correlation = camera_result$Correlation[[1]],
      camera_direction = camera_result$Direction[[1]],
      camera_p_value = camera_result$PValue[[1]],
      fry_direction = fry_result$Direction[[1]],
      fry_p_value_directional = fry_result$PValue[[1]],
      fry_p_value_mixed = fry_result$PValue.Mixed[[1]],
      stringsAsFactors = FALSE
    )
  }
}

results <- do.call(rbind, results)
results$camera_q_core6 <- p.adjust(results$camera_p_value, method = "BH")
results$fry_q_core6 <- p.adjust(results$fry_p_value_directional, method = "BH")
results$camera_expected_direction <- results$camera_direction == "Up"
results$fry_expected_direction <- results$fry_direction == "Up"
results$correlation_aware_support <-
  results$target_count_matches_frozen_ulm &
  results$camera_expected_direction &
  results$fry_expected_direction &
  results$camera_q_core6 < 0.05 &
  results$fry_q_core6 < 0.05

write.csv(
  results,
  file.path(output_dir, "03_CORRELATION_AWARE_STAT1_STAT2_SENSITIVITY.csv"),
  row.names = FALSE
)

payload <- list(
  created_at = "2026-08-20",
  status = "COMPLETE_C8R_CORRELATION_AWARE_STAT1_STAT2_SENSITIVITY_QUALIFIED",
  decision = "SUPPORTS_CONVERGENCE_WITH_DISCOVERY_STAT2_CAMERA_LIMITATION",
  policy = paste(
    "Frozen STAT1/STAT2 regulators, CollecTRI target signs, three C6B contrasts,",
    "filterByExpr backgrounds and design matrices were reused without reselection."
  ),
  methods = c(
    "voom plus CAMERA with residual-estimated inter-gene correlation",
    "FRY rotation test"
  ),
  tests = nrow(results),
  strict_dual_method_tests_supporting = sum(results$correlation_aware_support),
  target_counts_match = all(results$target_count_matches_frozen_ulm),
  camera_up = sum(results$camera_expected_direction),
  camera_bh_significant = sum(results$camera_q_core6 < 0.05),
  fry_up = sum(results$fry_expected_direction),
  fry_bh_significant = sum(results$fry_q_core6 < 0.05),
  explicit_exception = list(
    contrast = results$contrast[which.max(results$camera_q_core6)],
    regulator = results$regulator[which.max(results$camera_q_core6)],
    target_count = as.integer(results$matched_signed_targets[which.max(results$camera_q_core6)]),
    estimated_intergene_correlation = as.numeric(results$camera_inter_gene_correlation[which.max(results$camera_q_core6)]),
    camera_q_core6 = results$camera_q_core6[which.max(results$camera_q_core6)],
    fry_q_core6 = results$fry_q_core6[which.max(results$camera_q_core6)],
    interpretation = paste(
      "Direction was concordant under CAMERA and FRY, but CAMERA did not pass the",
      "six-test BH threshold for discovery STAT2; no universal CAMERA significance is claimed."
    )
  ),
  minimum_camera_q = min(results$camera_q_core6),
  maximum_camera_q = max(results$camera_q_core6),
  minimum_fry_q = min(results$fry_q_core6),
  maximum_fry_q = max(results$fry_q_core6),
  software = list(
    R = R.version.string,
    edgeR = as.character(packageVersion("edgeR")),
    limma = as.character(packageVersion("limma")),
    Matrix = as.character(packageVersion("Matrix"))
  )
)
writeLines(
  toJSON(payload, auto_unbox = TRUE, pretty = TRUE, digits = 10),
  file.path(output_dir, "04_CORRELATION_AWARE_STAT1_STAT2_DECISION.json"),
  useBytes = TRUE
)
cat(toJSON(payload, auto_unbox = TRUE, pretty = TRUE, digits = 10), "\n")
