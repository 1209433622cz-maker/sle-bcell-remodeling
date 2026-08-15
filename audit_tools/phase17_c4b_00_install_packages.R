#!/usr/bin/env Rscript

# Install only the packages required by the Gate C4B edgeR qualification suite.

cran <- 'https://cloud.r-project.org'
if (!requireNamespace('BiocManager', quietly = TRUE)) {
  install.packages('BiocManager', repos = cran)
}
cran_packages <- c('jsonlite', 'statmod')
missing_cran <- cran_packages[
  !vapply(cran_packages, requireNamespace, logical(1), quietly = TRUE)
]
if (length(missing_cran) > 0L) {
  install.packages(missing_cran, repos = cran)
}
bioc_packages <- c('edgeR', 'limma')
missing_bioc <- bioc_packages[
  !vapply(bioc_packages, requireNamespace, logical(1), quietly = TRUE)
]
if (length(missing_bioc) > 0L) {
  BiocManager::install(missing_bioc, ask = FALSE, update = FALSE)
}

required <- c('Matrix', 'edgeR', 'limma', 'statmod', 'jsonlite')
missing <- required[!vapply(required, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing) > 0L) {
  stop('Required packages remain missing: ', paste(missing, collapse = ', '))
}
cat(R.version.string, '\n')
cat('Bioconductor', as.character(BiocManager::version()), '\n')
for (package in required) {
  cat(package, as.character(packageVersion(package)), '\n')
}
