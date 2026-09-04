"""PSM data structure — Peptide Spectrum Matches."""

from qpx.core.data.base import BaseStructure
from qpx.core.data.loader import load_schema
from qpx.core.query import _escape_sql_string

PsmSchema = load_schema("psm")


class PSM(BaseStructure):
    """Peptide Spectrum Matches from identification searches."""

    _schema_class = PsmSchema

    def by_protein(self, protein: str) -> "PSM":
        """Filter PSMs by protein accession (searches within array)."""
        return self.filter(f"list_contains(protein_accessions, '{_escape_sql_string(protein)}')")

    def by_run(self, run_file_name: str) -> "PSM":
        """Filter PSMs by run file."""
        return self.filter(f"run_file_name = '{_escape_sql_string(run_file_name)}'")

    def targets_only(self) -> "PSM":
        """Filter to target PSMs only (exclude decoys)."""
        return self.filter("is_decoy = false")

    def quantified(self) -> "PSM":
        """Filter to PSMs that are linked to a quantified feature.

        ``feature_id`` is null when the identification maps to no feature — in
        OpenMS terms an *unassigned* PeptideIdentification, where the spectrum was
        identified but no MS1 feature was detected or mapped at that RT and m/z.
        Those rows are about **quantification**, not identification quality: they
        carry a sequence, a score and a spectrum reference like any other PSM.

        Use this before joining ``psm`` to ``feature``, which is otherwise a
        partial join — on a representative label-free dataset 41% of PSM rows have
        no feature (bigbio/qpx#299).
        """
        return self.filter("feature_id IS NOT NULL")

    def unquantified(self) -> "PSM":
        """Filter to identified PSMs that have no quantified feature.

        The complement of :meth:`quantified`. These are identifications without
        quantification, not failed identifications — their median posterior error
        probability is typically better than that of quantified PSMs, and some of
        their peptidoforms appear nowhere else in the file.
        """
        return self.filter("feature_id IS NULL")
