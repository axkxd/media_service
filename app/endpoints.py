import os
import uuid
import aiofiles

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from app.schemas import MediaFileCreate, MediaFile
from app.crud import MediaFileDAL
from app.cloud_storage import upload_to_cloud


# Создаем маршрутизаторы для загрузки и получения файлов
upload_media = APIRouter()
get_media = APIRouter()


@get_media.get("/{uid}")
async def get_file(uid: str, db: AsyncSession = Depends(get_async_session)):
    """Эндпоинт для получения файла по уникальному идентификатору."""

    try:
        gfile = MediaFileDAL(db)
        db_file = await gfile.get_media_file(uid)

        if db_file is None:
            raise HTTPException(status_code=404, detail="File not found")

        file_path = f"file_storage/{uid}_{db_file.filename}"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404,
                                detail="File not found on disk")

        return FileResponse(path=file_path,
                            filename=db_file.filename,
                            media_type=db_file.file_format)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@upload_media.post("/", response_model=MediaFile)
async def upload_file(file: UploadFile = File(...),
                      db: AsyncSession = Depends(get_async_session)):
    """Эндпоинт для загрузки файла."""

    try:
        uid = str(uuid.uuid4())
        storage_directory = "file_storage"
        if not os.path.exists(storage_directory):
            os.makedirs(storage_directory)

        file_location = os.path.join(storage_directory,
                                     f"{uid}_{file.filename}")

        async with aiofiles.open(file_location, "wb") as f:
            await f.write(await file.read())

        file_size = os.path.getsize(file_location)
        file_extension = os.path.splitext(file.filename)[1].replace(".", "")
        file_format = file.content_type

        media_file = MediaFileCreate(
            filename=file.filename,
            file_size=file_size,
            file_format=file_format,
            file_extension=file_extension,
        )

        # Сохраняем информацию о файле в базе данных
        new_file = MediaFileDAL(db)
        db_file = await new_file.create_media_file(media_file, uid)

        # Загружаем файл в облачное хранилище
        await upload_to_cloud(file_location, uid)

        return db_file
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
