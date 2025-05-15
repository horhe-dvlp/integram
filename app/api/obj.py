from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import json

from app.auth.auth import verify_token
from app.db.db import engine
from app.models.object import ObjectCreateRequest, ObjectCreateResponse
from app.logger import db_logger

router = APIRouter()


@router.post(
    "/object", response_model=ObjectCreateResponse, dependencies=[Depends(verify_token)]
)
async def create_object(payload: ObjectCreateRequest) -> ObjectCreateResponse:
    """
    Create a new object of a given term type with specified attributes.

    Args:
        payload: ObjectCreateRequest containing the type ID, parent ID, and attributes (attrs).

    Returns:
        ObjectCreateResponse: Object metadata and optional warning message.

    Raises:
        HTTPException: For invalid parameters or unexpected DB errors.
    """
    query = text(
        """
        SELECT * FROM post_objects(:db, :up, :type, :attrs)
    """
    )

    try:
        async with engine.begin() as conn:
            result = await conn.execute(
                query,
                {
                    "db": "rep",
                    "up": payload.up,
                    "type": payload.id,
                    "attrs": json.dumps(payload.attrs),
                },
            )
            row = result.fetchone()

        if not row:
            db_logger.exception(
                f"Empty response from post_objects: id={payload.id}, up={payload.up}, attrs_keys={list(payload.attrs.keys())}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        obj_id, res = row

        # Успешное добавление
        if res == "1":
            return ObjectCreateResponse(
                id=obj_id,
                up=payload.up,
                t=payload.id,
                val=payload.attrs[f"t{payload.id}"],
            )

        # Повторяющийся объект при UNIQUE
        if res == "err_non_unique_val":
            return ObjectCreateResponse(
                id=obj_id,
                up=payload.up,
                t=payload.id,
                val=payload.attrs[f"t{payload.id}"],
                warning="The record already exists",
            )

        # Невалидный тип или реквизит
        if res.startswith("err_type_not_found") or res.startswith("err_invalid_ref"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid type or reference",
            )

        # Пустое значение
        if res == "err_empty_val":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Empty object value",
            )

        db_logger.exception(
            f"Unexpected response from post_objects: res='{res}', id={payload.id}, up={payload.up}, attrs_keys={list(payload.attrs.keys())}"
        )

        # Непредусмотренная ошибка
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    except SQLAlchemyError as _e:
        db_logger.exception(f"Database error while executing post_object: {_e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error"
        )
