#!/usr/bin/env perl6

=begin pod

=head1 DESCRIPTION

Run Centrifuge

=head1 AUTHOR

Ken Youens-Clark <kyclark@email.arizona.edu>

=end pod

use v6;

constant $CENTRIFUGE = "%*ENV{'WORK'}/tools/centrifuge-1.0.2-beta/centrifuge";
constant $CENTRIFUGE_INDEXES ="%*ENV{'SCRATCH'}/centrifuge-indexes";
constant $LAUNCHER_DIR       = "%*ENV{'HOME'}/src/launcher";

# --------------------------------------------------
sub MAIN (
    Str :$query-dir!,
    Str :$out-dir="centrifuge-out",
    Str :$index='b_compressed+h+v',
) {
    die "Cannot find CENTRIFUGE ($CENTRIFUGE)" unless $CENTRIFUGE.IO.e;
    die "Cannot find CENTRIFUGE_INDEXES ($CENTRIFUGE_INDEXES)" 
        unless $CENTRIFUGE_INDEXES.IO.e;

    my $index-dir = $*SPEC.catdir($CENTRIFUGE_INDEXES, $index);

    die "Bad index dir ($index)" unless $index-dir.IO.d;

    my @fasta = find-fasta($query-dir);
    printf "Found %s file%s in %s\n", 
        @fasta.elems, @fasta.elems == 1 ?? '' !! 's', $query-dir;

    die "Nothing to do" unless @fasta.elems > 0;

    mkdir($out-dir) unless $out-dir.IO.d;

    my $params = open "{$*PID}-params", :w;
    for @fasta -> $file {
        $params.put("CENTRIFUGE_INDEXES=$CENTRIFUGE_INDEXES $CENTRIFUGE -f -x $index-dir -U $file -S $out-dir/{$file.basename}.sum --report-file $out-dir/{$file.basename}.tsv");
    }
    $params.close;


    my $launcher = "{$*PID}-launcher";
    my $launch   = open $launcher, :w;

    put "Writing launcher ($launcher)";
    $launch.put("export LAUNCHER_DIR=$LAUNCHER_DIR");
    $launch.put("export LAUNCHER_PPN=2");
    $launch.put("export LAUNCHER_WORKDIR=$out-dir");
    $launch.put("time $LAUNCHER_DIR/paramrun SLURM $LAUNCHER_DIR/init_launcher $out-dir $params");
    $launch.close;

    put "Launching";

    shell("sh $launcher");
    put "Done. See out-dir ($out-dir)";
}

# --------------------------------------------------
sub find-fasta (Str $dir) {
    die("dir ($dir) is not a directory") unless $dir.IO.d;
    my @bam-files = dir($dir, test => '*.bam');
    if @bam-files.elems > 0 {
        for @bam-files -> $bam {
            (my $basename = $bam.basename) ~~ s/. \w+ $//;
            my $fasta     = $*SPEC.catfile($dir, "$basename.fa");
            shell("samtools fasta -0 $fasta $bam");
        }
    }

    dir($dir, text => !/.bam$/).grep(*.IO.f);
}
