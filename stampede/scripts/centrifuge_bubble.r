#!/usr/bin/env Rscript

# Authors: Jimmy Thornton <jamesthornton@email.arizona.edu>,
#          Ken Youens-Clark <kyclark@email.arizona.edu>

library("optparse")
library("plyr")
library("ggplot2")
library("R.utils")

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
    default = "",
    type = "character",
    help = "out directory",
    metavar = "character"
  ),
  make_option(
    c("-f", "--outfile"),
    default = 'bubble',
    type = "character",
    help = "out file",
    metavar = "character"
  ),
  make_option(
    c("-t", "--title"),
    default = 'bubble',
    type = "character",
    help = "plot title",
    metavar = "character"
  )
);

opt_parser = OptionParser(option_list = option_list);
opt        = parse_args(opt_parser);
cent.dir   = opt$dir
out.dir    = opt$outdir
file_name  = opt$outfile
plot_title = opt$title
exclude    = unlist(strsplit(opt$exclude,","))

#
# SETWD: Location of centrifuge_report.tsv files. 
# Should all be in same directory
#
if (!dir.exists(cent.dir)) {
  stop(paste("Bad centrifuge directory: ", cent.dir))
}

setwd(cent.dir)

if (!dir.exists(out.dir)) {
  printf("Creating outdir '%s'\n", out.dir)
  dir.create(out.dir)
}

temp         = list.files(pattern="*.tsv")
myfiles      = lapply(temp, read.delim)
sample_names = as.list(sub(".tsv", "", temp))
myfiles      = Map(cbind, myfiles, sample = sample_names)

#
# Remove unwanted species
#
for (i in exclude) {
    myfiles <- llply(myfiles, function(x)x[x$name!=i,])
}

#
# Proportion calculations: Each species "Number of Unique Reads" 
# is divided by total "Unique Reads"
#
props = lapply(myfiles, function(x) { 
    x$proportion <- (x$numUniqueReads / sum(x$numUniqueReads))
    return(x[,c("name","proportion","sample")])
})

#
# Final dataframe created for plotting,
# can change proportion value (Default 1%)
#
final     = llply(props, subset, proportion > 0.02)
df        = ldply(final, data.frame)
names(df) = c("x", "Proportion", "z")

options(bitmapType='cairo')
png(filename=file.path(out.dir, paste0(file_name,".png")), width = 800, height = 800)
p2 = ggplot(df, aes(as.factor(z), as.factor(x))) + geom_point(aes(size = Proportion))
p2 = p2 + theme(text = element_text(size=20), axis.text.x = element_text(angle = 90, hjust = 1))
p2 = p2 + labs(y = "Organism", x = "Sample")
p2 = p2 + ggtitle(plot_title) + theme(plot.title = element_text(hjust = 0.5))
p2 = p2 + guides(color=F)
print(p2)
dev.off()

write.csv(df, file = file.path(out.dir, paste0(file_name, ".csv")))
printf("Done, see %s\n", out.dir)
