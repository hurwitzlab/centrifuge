import io
from run_centrifuge import guess_file_format, get_extension, get_file_formats, group_input_files


# --------------------------------------------------
def test_guess_file_format():
    """Test guess_file_format"""

    assert guess_file_format('') == ''
    assert guess_file_format('.fa') == 'fasta'
    assert guess_file_format('.fna') == 'fasta'
    assert guess_file_format('.fasta') == 'fasta'
    assert guess_file_format('.fq') == 'fastq'
    assert guess_file_format('.fastq') == 'fastq'
    assert guess_file_format('.xyz') == 'xyz'


# --------------------------------------------------
def test_get_extension():
    """Test get_extension"""

    assert get_extension('') == ''
    assert get_extension('foo') == ''
    assert get_extension('foo.txt') == '.txt'
    assert get_extension('foo.txt.gz') == '.gz'


# --------------------------------------------------
def test_get_file_formats():
    """Test get_file_formats"""

    assert get_file_formats([]) is None

    assert get_file_formats(['/x/y/z.abc']) == 'abc'

    assert get_file_formats(['/x/foo.fa', '/foo/bar.fasta',
                             '/x/baz.fna']) == 'fasta'

    assert get_file_formats(['/x/foo.fq', '/foo/bar.fastq']) == 'fastq'

    assert get_file_formats(['/x/foo.fa', '/foo/bar.fastq']) is None


# --------------------------------------------------
def test_group_input_files():
    """Test group_input_files"""

    gr1 = group_input_files(['foo_1.fasta'])
    assert gr1['unpaired'] == ['foo_1.fasta']
    assert not gr1['forward']
    assert not gr1['reverse']

    gr2 = group_input_files(['foo_1.fa', 'foo_2.fa'])
    assert not gr2['unpaired']
    assert not gr2['forward'] == ['foo_1.fasta']
    assert not gr2['reverse'] == ['foo_2.fasta']

    gr3 = group_input_files(['foo_1.fa', 'foo_2.fa'], reads_not_paired=True)
    assert gr3['unpaired'] == ['foo_1.fa', 'foo_2.fa']
    assert not gr3['forward']
    assert not gr3['reverse']

    gr4 = group_input_files(
        ['foo_1.fna', 'foo_2.fna', 'bar_R1.fna', 'bar_r2.fna', 'baz.fa'])
    assert gr4['unpaired'] == ['baz.fa']
    assert not gr4['forward'] == ['foo_1.fasta', 'bar_R1.fna']
    assert not gr4['reverse'] == ['foo_2.fasta', 'bar_r2.fna']
