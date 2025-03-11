#!/usr/bin/env python3
#
# MIT License
#
# Copyright (c) 2025 GT4SD team
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.#

"""Utilities for handling BLASTP configurations and output formats."""

BLAST_OPTIONS = {
    "db": "BLAST database name",
    "query": "Query file name",
    "query_loc": "Query sequence location",
    "out": "Output file name",
    "evalue": "E-value threshold",
    "subject": "Subject sequences file",
    "subject_loc": "Subject sequence location",
    "show_gis": "Show NCBI GIs",
    "num_descriptions": "Number of descriptions",
    "num_alignments": "Number of alignments",
    "max_target_seqs": "Max sequences to keep",
    "max_hsps": "Max HSPs per pair",
    "html": "HTML output",
    "gilist": "GI list filter",
    "negative_gilist": "Negative GI filter",
    "entrez_query": "Entrez query filter",
    "culling_limit": "Hit culling threshold",
    "best_hit_overhang": "Best hit overhang",
    "best_hit_score_edge": "Best hit score edge",
    "dbsize": "Database size",
    "searchsp": "Search space length",
    "import_search_strategy": "Import strategy",
    "export_search_strategy": "Export strategy",
    "parse_deflines": "Parse deflines",
    "num_threads": "CPU threads",
    "remote": "Remote search",
    "outfmt": "Output format",
}

BLAST_OUTPUT_FORMATS = {
    "0": "Pairwise",
    "1": "Query-anchored with identities",
    "2": "Query-anchored no identities",
    "3": "Flat query-anchored with identities",
    "4": "Flat query-anchored no identities",
    "5": "XML",
    "6": "Tabular",
    "7": "Tabular with comments",
    "8": "Text ASN.1",
    "9": "Binary ASN.1",
    "10": "CSV",
    "11": "ASN.1 archive",
    "12": "Seqalign JSON",
    "13": "Multiple-file JSON",
    "14": "Multiple-file XML2",
    "15": "Single-file JSON",
    "16": "Single-file XML2",
    "17": "SAM",
    "18": "Organism Report",
}

BLAST_SPECIFIERS = {
    "qseqid": "Query Seq-id",
    "qgi": "Query GI",
    "qacc": "Query accession",
    "sseqid": "Subject Seq-id",
    "sallseqid": "All subject Seq-ids",
    "sgi": "Subject GI",
    "sallgi": "All subject GIs",
    "sacc": "Subject accession",
    "sallacc": "All subject accessions",
    "qstart": "Query start position",
    "qend": "Query end position",
    "sstart": "Subject start position",
    "send": "Subject end position",
    "qseq": "Query sequence",
    "sseq": "Subject sequence",
    "evalue": "E-value",
    "bitscore": "Bit score",
    "score": "Raw score",
    "length": "Alignment length",
    "pident": "Percentage identity",
    "nident": "Number of identities",
    "mismatch": "Number of mismatches",
    "positive": "Positive-scoring matches",
    "gapopen": "Gap openings",
    "gaps": "Total gaps",
    "ppos": "Percentage positives",
    "frames": "Query/subject frames",
    "qframe": "Query frame",
    "sframe": "Subject frame",
    "btop": "BLAST traceback",
    "staxids": "Subject taxonomy IDs",
    "sscinames": "Subject scientific names",
    "scomnames": "Subject common names",
    "sblastnames": "Subject BLAST names",
    "sskingdoms": "Subject super kingdoms",
    "stitle": "Subject title",
    "salltitles": "All subject titles",
    "sstrand": "Subject strand",
    "qcovs": "Query coverage per subject",
    "qcovhsp": "Query coverage per HSP",
}
