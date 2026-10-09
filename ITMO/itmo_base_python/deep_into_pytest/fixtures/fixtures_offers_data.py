import pytest

from itmo.ITMO.itmo_base_python.deep_into_pytest.utils.btc_response import BTC_RESPONSE
from itmo.ITMO.itmo_base_python.deep_into_pytest.utils.eth_response import ETH_RESPONSE


@pytest.fixture(params=[
    ('BTC', 'BTC_RESPONSE'),
    ('ETH', 'ETH_RESPONSE'),
    ('USDT', 'USDT_RESPONSE')  # ← Вот и ещё одно ветвление в фикстуру, всё!
] , ids=['BTC', 'ETH', 'USDT'], scope="session")
def crypto_data(request):
    """Фикстура возвращает данные для разных криптовалют"""
    token, response_name = request.param

    if response_name == 'BTC_RESPONSE':
        response_data = BTC_RESPONSE
    else:
        response_data = ETH_RESPONSE

    return {
        'token': token,
        'response': response_data,
        'items': response_data['result']['items']
    }