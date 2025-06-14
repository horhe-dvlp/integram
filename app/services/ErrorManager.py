# app/core/error_manager.py

from fastapi import HTTPException, status
from app.logger import db_logger as logger


class ErrorManager:
    _instance = None

    _KNOWN_ERRORS: dict[str, tuple[int, str]] = {
        "err_empty_val": (status.HTTP_422_UNPROCESSABLE_ENTITY, "Empty value"),
        "err_non_unique_val": (status.HTTP_200_OK, "Value is not unique"),
        "err_type_not_found": (status.HTTP_400_BAD_REQUEST, "Invalid type"),
        "err_invalid_ref": (status.HTTP_400_BAD_REQUEST, "Invalid reference"),
        "warn_record_exists": (status.HTTP_200_OK, "Record already exists"),
        "err_obj_not_found": (status.HTTP_404_NOT_FOUND, "Object not found"),
        "err_is_metadata": (status.HTTP_400_BAD_REQUEST, "Object is metadata"),
        "err_is_referenced": (status.HTTP_400_BAD_REQUEST, "Object is referenced"),
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ErrorManager, cls).__new__(cls)
        return cls._instance

    def raise_if_error(self, res: str, *, log_context: str = "") -> None:
        """
        Raises HTTPException if `res` is a known error with 4xx/5xx status.
        Returns None if OK/warning.
        """
        for prefix, (code, message) in self._KNOWN_ERRORS.items():
            if res.startswith(prefix):
                if code >= 400:
                    logger.warning(f"{log_context} — DB returned known error: {res}")
                    raise HTTPException(status_code=code, detail=message)
                return  # known benign (e.g., 200 OK warning)
        
        logger.error(f"{log_context} — Unknown DB error: {res}")
        raise HTTPException(status_code=500, detail="Unexpected database response")

    def get_status_and_message(self, res: str) -> tuple[int, str] | None:
        for prefix, (code, message) in self._KNOWN_ERRORS.items():
            if res.startswith(prefix):
                return code, message
        return None

    def is_warning(self, res: str) -> bool:
        data = self.get_status_and_message(res)
        return data is not None and data[0] == status.HTTP_200_OK



error_manager = ErrorManager()
