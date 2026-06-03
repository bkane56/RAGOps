from app.core.errors.handlers import AppError


def test_app_error_attributes():
    err = AppError("msg", code="test_code", status_code=404)
    assert err.message == "msg"
    assert err.code == "test_code"
    assert err.status_code == 404
