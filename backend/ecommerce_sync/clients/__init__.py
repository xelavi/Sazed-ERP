from .base import EcommerceClient, EcommerceConnectionError
from .prestashop import PrestaShopClient

__all__ = [
    'EcommerceClient',
    'EcommerceConnectionError',
    'PrestaShopClient',
    'get_client_for',
]


def get_client_for(connection):
    """Construye el cliente concreto según `connection.platform`.

    Args:
        connection: instancia de `StoreConnection`.

    Returns:
        EcommerceClient: cliente listo para usar.

    Raises:
        NotImplementedError: si la plataforma aún no tiene cliente.
    """
    if connection.platform == 'prestashop':
        return PrestaShopClient(
            base_url=connection.base_url,
            api_key=connection.api_key,
        )
    raise NotImplementedError(
        f'No hay cliente implementado para la plataforma "{connection.platform}".'
    )
