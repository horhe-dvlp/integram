from app.services.term_builder import build_terms_from_rows


def test_build_terms_from_rows():
    rows = [
        {"id": 1, "up": 0, "base": 2, "obj": "User", "req_id": 101, "req_val": "Name", "req_t": 32, "ord": 1, "obj_mods": ["UNIQUE"]},
        {"id": 1, "up": 0, "base": 2, "obj": "User", "req_id": 102, "req_val": "Age", "req_t": 33, "ord": 2, "obj_mods": ["UNIQUE"]},
    ]
    terms = build_terms_from_rows(rows)
    assert terms[0]["id"] == 1
    assert len(terms[0]["reqs"]) == 2
    assert terms[0]["unique"] == 1
