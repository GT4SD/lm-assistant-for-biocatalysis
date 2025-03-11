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
"""Examples config ."""

TOOL_EXAMPLES = [
    {
        "name": "GetElementsOfReaction",
        "id": "get_elements",
        "emoji": "🧬",
        "example_input": """Extract components from this reaction: CC(=O)Nc1ccc(cc1)S(=O)(=O)N|MVEAFCATWKLTNSQNFDEYMKALGVGFATRQVGNVTKPTVIISQEGDKVVIRTLSTFKNTEISFQLGEEFDETTADDRNCKSVVSLDGDKLVHIQKWDGKETNFVREIKDGKMVMTLTFGDVVAVRHYEKA>>CC(=O)Nc1ccc(cc1)S(=O)(=O)O""",
    },
    {
        "name": "ExtractBindingSites",
        "id": "get_binding_sites",
        "emoji": "🎯",
        "example_input": """Extract binding sites from this reaction: CC(=O)Nc1ccc(cc1)S(=O)(=O)N|MVEAFCATWKLTNSQNFDEYMKALGVGFATRQVGNVTKPTVIISQEGDKVVIRTLSTFKNTEISFQLGEEFDETTADDRNCKSVVSLDGDKLVHIQKWDGKETNFVREIKDGKMVMTLTFGDVVAVRHYEKA>>CC(=O)Nc1ccc(cc1)S(=O)(=O)O""",
    },
    {
        "name": "OptimizeEnzymeSequences",
        "id": "optimize",
        "emoji": "⚡",
        "example_input": """Optimize this enzyme sequence for the following reaction:
Sequence: MVEAFCATWKLTNSQNFDEYMKALGVGFATRQVGNVTKPTVIISQEGDKVVIRTLSTFKNTEISFQLGEEFDETTADDRNCKSVVSLDGDKLVHIQKWDGKETNFVREIKDGKMVMTLTFGDVVAVRHYEKA
Substrate: CC(=O)Nc1ccc(cc1)S(=O)(=O)N
Product: CC(=O)Nc1ccc(cc1)S(=O)(=O)O""",
    },
    {
        "name": "Blastp",
        "id": "blastp",
        "emoji": "🔍",
        "example_input": """Run a BLASTP search for the protein sequence:
Sequence: MVEAFCATWKLTNSQNFDEYMKALGVGFATRQVGNVTKPTVIISQEGDKVVIRTLSTFKNTEISFQLGEEFDETTADDRNCKSVVSLDGDKLVHIQKWDGKETNFVREIKDGKMVMTLTFGDVVAVRHYEKA""",
    },
    {
        "name": "FindPDBStructure",
        "id": "find_pdb_structure",
        "emoji": "🧬",
        "example_input": """Find PDB structure for protein sequence:
Sequence: MVEAFCATWKLTNSQNFDEYMKALGVGFATRQVGNVTKPTVIISQEGDKVVIRTLSTFKNTEISFQLGEEFDETTADDRNCKSVVSLDGDKLVHIQKWDGKETNFVREIKDGKMVMTLTFGDVVAVRHYEKA""",
    },
    {
        "name": "DownloadPDBStructure",
        "id": "download_pdb_structure",
        "emoji": "📥",
        "example_input": """Download PDB structure with code "8IVL".""",
    },
    {
        "name": "Mutagenesis",
        "id": "mutagenesis",
        "emoji": "🧪",
        "example_input": """Perform a mutation on the PDB structure with code "8IVL" to match the following sequence: MASLGHILVFCVTLLTMAKAESPKEHDPFTYDYQSLQIGGLLIAGILFILGILILLSRRCRCKFNQQQRTGEPDEEEGTFRSSIRRLSTRRR.""",
    },
    {
        "name": "MDSimulation",
        "id": "md_simulation",
        "emoji": "💻",
        "example_input": """Run MD simulation for the structure 8ivl_mutated using standard parameters (Minimization, NVT, NPT).""",
    },
]
