from pytest import mark


@mark.parametrize("check_type, expected_value", [
    ('token', 'tokenId'),
    ('currency', 'currencyId'),
    ('price_positive', 'price'),
    ('quantity_positive', 'quantity')
], ids=['token_check', 'currency_check', 'price_check', 'quantity_check'])
def test_offers_data(crypto_data, check_type, expected_value):
    """
    Универсальный тест для проверки всех параметров ордеров
    """
    items = crypto_data['items']
    token = crypto_data['token']

    if check_type == 'token':
        for offer in items:
            assert offer[expected_value] == token, (
                f"Неверный токен: {offer[expected_value]}. Ожидался: {token}"
            )

    elif check_type == 'currency':
        for offer in items:
            assert offer[expected_value] == 'RUB', (
                f"Неверная валюта: {offer[expected_value]}"
            )

    else:
        for offer in items:
            assert float(offer[expected_value]) > 0, (
                f"Цена или количество {token} должны быть положительными"
            )


def test_offers_count(crypto_data):
    """
    Проверяем количество предложений для каждой криптовалюты
    """
    items = crypto_data['items']
    token = crypto_data['token']

    assert len(items) == 10, (
        f"Для {token} выводится {len(items)} предложений вместо 10"
        )