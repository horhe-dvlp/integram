from app.services.filter_builder import FilterBuilder
from app.models.objects import HeaderField


def test_filter_builder():
    header = [HeaderField(id=5, t=5, name="name", base=0)]
    filters = {"name": "%John%", "f7": "Smith"}
    fb = FilterBuilder(filters, term_id=7, term_name="Person", header=header, db_name="tbl")
    joins, where, params = fb.build()

    assert "LEFT JOIN tbl f5" in joins
    assert "LIKE :filter_5" in where
    assert params["filter_5"] == "%john%"
    assert params["filter_7"] == "smith"
