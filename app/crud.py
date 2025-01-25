from typing import Type, TypeVar, Optional, List

from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from pydantic import BaseModel
from app.models import MediaFile
from app.schemas import MediaFileCreate
from app.models import Base


T = TypeVar("T", bound=Base)
P = TypeVar("P", bound=BaseModel)


class BaseCRUD:
    """
    Универсальный базовый класс CRUD (Create, Read, Update, Delete)
    для обработки операций С базой данных.
    Предоставляет общие функции CRUD для любой модели SQLAlchemy.
    """
    def __init__(self, model: Type[Base], db: AsyncSession):
        """
        Инициализация операций CRUD.

        Аргументы:
        - model: класс модели SQLAlchemy.
        - db: Асинхронная сессия SQLAlchemy для выполнения операций с БД.
        """
        self.model = model
        self.db = db

    async def create(self, obj_in: P) -> Base:
        """
        Создает новую запись в базе данных.

        Аргументы:
        - obj_in: Схема Pydantic, содержащая входные данные.

        Возвращает:
        - Экземпляр созданного элемента.
        """
        db_obj = self.model(**obj_in.model_dump())
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def get(self, obj_id: int) -> Optional[Base]:
        """
        Извлекает одну запись по id.

        Аргументы:
        - obj_id: id обекта.

        Возвращает:
        - Возвращает нужный объект или None,
        если запрашиваемый объект не найден.
        """
        query = select(self.model).filter(
            self.model.id == obj_id)  # type: ignore
        result = await self.db.execute(query)
        db_obj = result.scalar_one_or_none()
        return db_obj

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Base]:
        """
        Извлекает несколько записей с пагинацией.

        Аргументы:
        - skip: Количество записей для пропуска (по умолчанию 0).
        - limit: Максимальное количество записей для извлечения
        (по умолчанию 100).

        Возвращает:
        - Список объектов.
        """

        query = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result. scalars().all()  # type: ignore

    async def update(self, obj_id: int, obj_in: P) -> Base:
        """
        Обновляет существующую запись по id.

        Аргументы:
        - obj_id: id объекта для обновления.
        - obj_in: Схема Pydantic, содержащая данные обновления.

        Возвращает:
        - обновленный экземпляр модели SQLAlchemy:

        Вызывает:
        - HTTPException 404, если запись не найдена.
        """
        query = select(self.model).filter(
            self.model.id == obj_id)  # type: ignore
        result = await self.db.execute(query)
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Item not found."
            )
        for var, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(db_obj, var, value)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, obj_id: int) -> Base:
        """
        Удаляет запись по id.
        -Аргументы:
        - obj_id: id обьекта для удаления.

        Возвращает:
        - Удаленный объект.

        Вызывает:
        - HTTPException 404, если запись не найдена.
        """
        query = select(self.model).filter(
            self.model.id == obj_id)  # type: ignore
        result = await self.db.execute(query)
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Item not found."
            )
        await self.db.delete(db_obj)
        await self.db.commit()
        return db_obj


class MediaFileCRUD(BaseCRUD):
    def __init__(self, db: AsyncSession) -> None:
        """
        Инициализация MediaFileCRUD.
        """
        super().__init__(MediaFile, db)

    async def create_media_file(self,
                                media: MediaFileCreate,
                                uid: str) -> MediaFile:
        """Создает новый медиафайл и сохраняет его в базе данных.

        Args:
            media (MediaFileCreate): Объект с данными медиафайла для создания.
            uid (str): Уникальный идентификатор для медиафайла.

        Returns:
            MediaFile: Созданный объект медиафайла.
        """
        try:
            db_media = MediaFile(
                uid=uid,
                filename=media.filename,
                file_size=media.file_size,
                file_format=media.file_format,
                file_extension=media.file_extension
            )
            self.db.add(db_media)
            await self.db.commit()
            await self.db.refresh(db_media)
            return db_media
        except Exception as e:
            await self.db.rollback()
            raise e

    async def get_media_file(self, uid: str) -> MediaFile | None:
        """Получает медиафайл по уникальному идентификатору.

        Args:
            uid (str): Уникальный идентификатор медиафайла.

        Returns:
            MediaFile | None: Объект медиафайла или None, если файл не найден.
        """
        query = select(MediaFile).where(MediaFile.uid == uid)
        result = await self.db.execute(query)
        return result.scalars().first()
