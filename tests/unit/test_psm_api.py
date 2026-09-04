"""PSM.quantified() / PSM.unquantified() — the supported split on feature_id."""

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from qpx.core.data import PSM


@pytest.fixture(name="psm_file")
def _psm_file(tmp_path):
    """A tiny psm.parquet with two quantified rows and one unquantified."""
    from tests.conftest import make_psm_record

    records = []
    for i, feature_id in enumerate((111, 222, None)):
        record = dict(make_psm_record())
        record["psm_id"] = 900 + i
        record["sequence"] = f"PEPTIDE{i}"
        record["feature_id"] = feature_id
        records.append(record)
    schema = PSM._schema_class.get_arrow_schema()
    table = pa.Table.from_pylist([{k: r.get(k) for k in schema.names} for r in records], schema=schema)
    path = tmp_path / "x.psm.parquet"
    pq.write_table(table, path)
    return path


def test_quantified_keeps_only_linked_rows(psm_file):
    psm = PSM.from_file(psm_file)
    assert psm.count() == 3
    assert psm.quantified().count() == 2
    assert psm.quantified().to_df()["feature_id"].notna().all()


def test_unquantified_is_the_complement(psm_file):
    psm = PSM.from_file(psm_file)
    assert psm.unquantified().count() == 1
    # pandas renders a null int64 as NaN, not None.
    assert psm.unquantified().to_df()["feature_id"].isna().all()
    assert psm.quantified().count() + psm.unquantified().count() == psm.count()
