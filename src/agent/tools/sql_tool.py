"""Ferramentas de leitura e consulta dos dados operacionais da Empório da Música."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"


def _table_name(csv_path: Path) -> str:
    return csv_path.stem.split(" - ")[-1].strip().lower()


@lru_cache(maxsize=1)
def _load_tables() -> Dict[str, pd.DataFrame]:
    tables: Dict[str, pd.DataFrame] = {}
    for csv_path in sorted(DATA_DIR.glob("*.csv")):
        tables[_table_name(csv_path)] = pd.read_csv(csv_path)
    return tables


def list_tables() -> List[str]:
    """Retorna os nomes das tabelas/carregamentos disponíveis."""
    return sorted(_load_tables().keys())


def search_products(query: str, category: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
    """Busca produtos por nome ou descrição (case-insensitive)."""
    products = _load_tables()["products"]
    q = str(query).lower()
    mask = products["name"].astype(str).str.lower().str.contains(q) | products["description"].astype(str).str.lower().str.contains(q)
    if category:
        mask &= products["category_id"].astype(str) == str(category)
    return products.loc[mask].head(int(limit)).to_dict(orient="records")


def get_product(product_id: int) -> Optional[Dict[str, Any]]:
    """Retorna os dados completos de um produto (preço, estoque, status)."""
    products = _load_tables()["products"]
    rows = products[products["product_id"] == int(product_id)]
    if rows.empty:
        return None
    return rows.to_dict(orient="records")[0]


def get_order_status(order_id: int) -> Optional[Dict[str, Any]]:
    """Retorna o status de um pedido (situação, pagamento, frete e entrega)."""
    orders = _load_tables()["orders"]
    rows = orders[orders["order_id"] == int(order_id)]
    if rows.empty:
        return None
    return rows.to_dict(orient="records")[0]


def get_customer_orders(customer_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Retorna os pedidos de um cliente (histórico)."""
    orders = _load_tables()["orders"]
    rows = orders[orders["customer_id"] == int(customer_id)].head(int(limit))
    return rows.to_dict(orient="records")


def check_stock(product_id: int) -> bool:
    """Verifica se um produto está em estoque (disponível para venda)."""
    products = _load_tables()["products"]
    row = products[products["product_id"] == int(product_id)]
    if row.empty:
        return False
    return bool(row.iloc[0]["stock_quantity"] > 0)


def list_categories() -> List[Dict[str, Any]]:
    """Retorna todas as categorias de instrumentos musicais."""
    return _load_tables()["categories"].to_dict(orient="records")
