from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from common.config import DATABASE_URL


# Создаем асинхронный движок для работы с базой данных
async_engine = create_async_engine(
    DATABASE_URL, echo=True
)

# Создаем фабрику асинхронных сессий
async_session = async_sessionmaker(
    bind=async_engine, expire_on_commit=False, autoflush=False
)


# Генератор для предоставления сессии базы данных в FastAPI через зависимость
async def get_async_session() -> AsyncGenerator:
    async with async_session() as session:
        yield session
