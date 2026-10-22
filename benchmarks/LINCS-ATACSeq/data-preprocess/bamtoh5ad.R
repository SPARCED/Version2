library(stringr)
library(ArchR)
set.seed(1)
addArchRThreads(threads = 1) 
addArchRGenome("hg38")
args <- commandArgs(trailingOnly = TRUE)

file_path <- args[1]

data_id <- str_split_i(file_path, pattern = ".", i = 1)

inputFiles <- c(data_id = file_path)
outDir <- "./GeneScoreMatricies/"
outputMatrix <- sprintf("%s_gene_scores.mtx", data_id)
outputGenes <- sprintf("%s_genes.tsv", data_id)
outputCells <- sprintf("%s_cells.tsv", data_id)

ArrowFiles <- createArrowFiles(
  inputFiles = inputFiles,
  sampleNames = names(inputFiles),
  minTSS = 0,        
  minFrags = 1000,   
  maxFrags = 1e8,         
  addTileMat = TRUE,
  addGeneScoreMat = TRUE ,
  force= TRUE
)

proj <- ArchRProject(
  ArrowFiles = ArrowFiles, 
  outputDirectory = outDir, 
  copyArrows = TRUE 
)

gene_score_se <- getMatrixFromProject(proj, useMatrix = "GeneScoreMatrix")
count_matrix <- assay(gene_score_se)
gene_names <- rowData(gene_score_se)$name
cell_names <- colnames(gene_score_se)

library(Matrix)
writeMM(count_matrix, file=paste0(outDir, outputMatrix))
write.table(gene_names, file=paste0(outDir, outputGenes), sep="\t", quote=FALSE, row.names=FALSE, col.names=FALSE)
write.table(cell_names, file=paste0(outDir, outputCells), sep="\t", quote=FALSE, row.names=FALSE, col.names=FALSE)

