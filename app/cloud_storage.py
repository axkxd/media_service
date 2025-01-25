import aiohttp

from common.config import CLOUD_URL


async def upload_to_cloud(file_path: str, uid: str) -> None:
    """
    Загружает файл в облачное хранилище.

    Аргументы:
    - file_path (str): Путь к файлу, который требуется загрузить.
    - uid (str): Уникальный идентификатор файла.

    Возвращает:
    - None
    """
    try:
        async with aiohttp.ClientSession() as session:
            with open(file_path, 'rb') as file_data:
                async with session.post(
                    CLOUD_URL, data={'file': file_data}
                ) as response:
                    response.raise_for_status()
                    print(f"Файл {uid} загружен в облако.")
    except aiohttp.ClientError as e:
        print(f"Ошибка загрузки файла {uid}: {e}")
