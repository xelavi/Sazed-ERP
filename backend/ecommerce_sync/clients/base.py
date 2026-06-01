"""
Interfaz común de los clientes de e-commerce.

Permite que el resto del módulo (sync_service, signals, comandos) sea
agnóstico a la plataforma: hoy PrestaShop, mañana Shopify/WooCommerce
sin tocar la lógica de negocio.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class EcommerceConnectionError(Exception):
    """Error de conexión o autenticación con la tienda."""


class EcommerceClient(ABC):
    """Contrato mínimo que debe cumplir cualquier cliente de tienda."""

    #: nombre de plataforma (para logging/diagnóstico)
    platform: str = 'generic'

    # ── Conexión ────────────────────────────────────────
    @abstractmethod
    def test_connection(self) -> dict[str, Any]:
        """Verifica credenciales. Devuelve `{ok, shop_name, resources, ...}`."""

    # ── Productos ───────────────────────────────────────
    @abstractmethod
    def list_products(self, **filters) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    def get_product(self, store_id: int) -> dict[str, Any]:
        ...

    @abstractmethod
    def find_product_by_reference(self, reference: str) -> int | None:
        ...

    @abstractmethod
    def create_product(self, payload: dict[str, Any]) -> int:
        ...

    @abstractmethod
    def update_product(self, store_id: int, payload: dict[str, Any]) -> None:
        ...

    @abstractmethod
    def set_stock(self, store_id: int, quantity: int) -> None:
        ...

    # ── Clientes ────────────────────────────────────────
    @abstractmethod
    def find_customer_by_email(self, email: str) -> int | None:
        ...

    @abstractmethod
    def create_customer(self, payload: dict[str, Any]) -> int:
        ...

    @abstractmethod
    def update_customer(self, store_id: int, payload: dict[str, Any]) -> None:
        ...

    # ── Pedidos (tienda → ERP) ──────────────────────────
    @abstractmethod
    def list_orders_since(self, since, **filters) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    def get_order(self, store_id: int) -> dict[str, Any]:
        ...
