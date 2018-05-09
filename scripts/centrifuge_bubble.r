#!/usr/bin/env Rscript

# Authors: Jimmy Thornton <jamesthornton@email.arizona.edu>,
#          Ken Youens-Clark <kyclark@email.arizona.edu>

suppressMessages(library("optparse"))
suppressMessages(library("plyr"))
suppressMessages(library("ggplot2"))
suppressMessages(library("R.utils"))

args = commandArgs(trailingOnly=TRUE)

option_list = list(
  make_option(
    c("-d", "--dir"),
    default = "",
    type = "character",
    help = "Centrifuge outdir",
    metavar = "character"
  ),
  make_option(
    c("-e", "--exclude"),
    default = "",
    type = "character",
    help = "Species to exclude",
    metavar = "character"
  ),
  make_option(
    c("-o", "--outdir"),
    default = file.path(getwd(), "plots"),
    type = "character",
    help = "Out directory",
    metavar = "character"
  ),
  make_option(
    c("-f", "--outfile"),
    default = 'bubble',
    type = "character",
    help = "Out file",
    metavar = "character"
  ),
  make_option(
    c("-p", "--proportion"),
    default = 0.02,
    type = "double",
    help = "Minimum proportion",
    metavar = "float"
  ),
  make_option(
    c("-t", "--title"),
    default = 'bubble',
    type = "character",
    help = "plot title",
    metavar = "character"
  )
);

opt.parser = OptionParser(option_list = option_list);
opt        = parse_args(opt.parser);
cent.dir   = opt$dir
out.dir    = opt$outdir
file.name  = opt$outfile
plot.title = opt$title
min.prop   = opt$proportion
exclude    = unlist(strsplit(opt$exclude,"[[:space:]]*,[[:space:]]*"))

#
# SETWD: Location of centrifuge_report.tsv files. 
# Should all be in same directory
#
if (nchar(cent.dir) == 0) {
  stop("--dir is required");
}

if (!dir.exists(cent.dir)) {
  stop(paste("Bad centrifuge directory: ", cent.dir))
}

if (min.prop > 1) {
  min.prop = min.prop / 100
}

tsv.files = list.files(path = cent.dir, pattern = "*.tsv", full.names = T)
num.files = length(tsv.files)

if (num.files == 0) {
  stop(paste("Found no *.tsv files in ", cent.dir))
} else {
  printf("I found %s file%s\n", num.files, if (num.files==1) '' else 's')
}

if (!dir.exists(out.dir)) {
  printf("Creating outdir '%s'\n", out.dir)
  dir.create(out.dir)
}

all.data     = lapply(tsv.files, read.delim)
sample.names = as.list(sub(".tsv", "", Map(basename, tsv.files)))
num.samples  = length(sample.names)
all.data     = Map(cbind, all.data, sample = sample.names)

#
# Remove unwanted species
#
for (species.name in exclude) {
  printf("Removing %s\n", species.name)
  all.data <- llply(all.data, function(x) { x[x$name != species.name,] })
}

#
# Proportion calculations: Each species "Number of Unique Reads" 
# is divided by total "Unique Reads"
#
props = lapply(all.data, function(x) { 
  x$proportion = x$numUniqueReads / sum(x$numUniqueReads)
  return(x[, c("name", "proportion", "sample")])
})

#
# Final dataframe created for plotting,
# can change proportion value (Default 1%)
#
final    = llply(props, subset, proportion > min.prop)
df       = ldply(final, data.frame)
num_orgs = nrow(df)

printf("At a proportion of %s, %s sample%s were included.\n",
       min.prop, num_orgs, if (num_orgs==1) '' else 's')

max_orgs = 1000
if (num_orgs > max_orgs) {
  printf("That is too many (max %s), I have to trim it down\n", max_orgs)
  df = df[1:max_orgs,]
} else if (num_orgs == 0) {
  stop("There is nothing to show")
}

height = 7
extra.rows = nrow(df) - 25
if (extra.rows > 0) {
  height = height + (extra.rows * .2)
}

width = 7
extra.samples = num.samples - 5
if (extra.samples > 0) {
  width = width + (extra.samples * .6)
}

bplot = ggplot(df, aes(as.factor(sample), as.factor(name))) + 
  geom_point(aes(size = proportion)) + 
  labs(y = "Organism", x = "Sample") + 
  ggtitle(plot.title) + 
  guides(color = FALSE) +
  theme(text = element_text(size=20), 
        legend.position = "bottom",
        axis.text.x = element_text(angle = 45, hjust = 1))

ggsave(filename=file.path(out.dir, paste0(file.name, ".png")), plot=bplot, 
       width = width, height = height, units="in")

write.csv(df, file = file.path(out.dir, paste0(file.name, ".csv")))
printf("Done, see %s\n", out.dir)
