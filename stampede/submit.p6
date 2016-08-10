#!/usr/bin/env perl6

use v6;

sub MAIN (
    Str :$query-dir!,
    Str :$out-dir="centrifuge-out",
    Str :$index='b_compressed+h+v',
    Str :$time="02:00:00",
    Str :$partition="development",
    Str :$job_name="centrifuge"
) {
    die("query-dir ($query-dir) is not a directory") unless $query-dir.IO.d;

    shell "sbatch -A iPlant-Collabs -N 1 -n 4 -t $time -p $partition -J $job_name --mail-type BEGIN,END,FAIL --mail-user kyclark@email.arizona.edu run.p6 --query-dir=$query-dir --out-dir=$out-dir --index=$index";
}
