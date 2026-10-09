import pytest

pytest_plugins = [
    'fixtures.fixtures_offers_data',
]

@pytest.fixture
def sample_numbers():
    """Возвращает кортеж с числами для тестирования"""
    return (5, 10, 15)

@pytest.fixture
def temporary_data():
    """
    Фикстура с полным циклом: подготовка -> передача -> очистка
    """
    # ПОДГОТОВКА - выполняется ДО теста
    data = [1, 2, 3, 4, 5]
    print("Данные подготовлены:", data)

    # ПЕРЕДАЧА данных тесту
    yield data

    # ОЧИСТКА - выполняется ПОСЛЕ теста
    data.clear()  # данный метод очищает наш список
    print(f"{data} - пусто, данные очищены!") 