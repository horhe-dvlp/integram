import pytest
from fastapi import HTTPException
from app.services.error_manager import error_manager


def test_raise_known_error():
    with pytest.raises(HTTPException) as exc:
        error_manager.raise_if_error("err_obj_not_found", log_context="CTX")
    assert exc.value.status_code == 404


def test_warning_no_exception():
    assert error_manager.raise_if_error("warn_term_exists") is None


def test_is_warning():
    assert error_manager.is_warning("warn_term_exists")
    assert not error_manager.is_warning("err_obj_not_found")


def test_unknown_error():
    with pytest.raises(HTTPException) as exc:
        error_manager.raise_if_error("unknown")
    assert exc.value.status_code == 500
