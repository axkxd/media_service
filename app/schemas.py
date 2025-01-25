from pydantic import BaseModel


class MediaFileBase(BaseModel):
    """
    Базовая модель для хранения информации о медиафайле.
    """
    filename: str
    file_size: int
    file_format: str
    file_extension: str


class MediaFileCreate(MediaFileBase):
    """
    Модель для создания нового медиафайла, наследует базовые атрибуты.
    """
    pass


class MediaFile(MediaFileBase):
    """
    Полная модель медиафайла, включает ID и UID,
    используется для чтения из базы данных
    """
    id: int
    uid: str

    # Настройки конфигурации Pydantic модели
    class ConfigDict:
        # Включаем поддержку ORM-сущностей,
        # чтобы работать с объектами из баз данных
        orm_mode = True
