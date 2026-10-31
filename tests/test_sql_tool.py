from src.agent.tools import sql_tool


def test_list_tables():
    tables = sql_tool.list_tables()
    assert "products" in tables
    assert "orders" in tables
    assert "customers" in tables


def test_get_product_by_id():
    product = sql_tool.get_product(81)
    assert product is not None
    assert product["name"] == "Yamaha C40 Nylon Natural"
    assert product["status"] == "active"


def test_check_stock():
    assert sql_tool.check_stock(81) is True
    assert sql_tool.check_stock(113) is False
    assert sql_tool.check_stock(99999) is False


def test_get_product_availability_distinguishes_exception_paths():
    cases = {
        81: "available",
        96: "out_of_stock",
        113: "discontinued",
        130: "coming_soon",
        99999: "not_found",
    }

    for product_id, expected_availability in cases.items():
        result = sql_tool.get_product_availability(product_id)
        assert result["availability"] == expected_availability
        assert result["available"] is (expected_availability == "available")
        assert result["message"]


def test_search_products():
    results = sql_tool.search_products("Yamaha", limit=3)
    assert len(results) > 0
    assert any("yamaha" in str(r.get("name", "")).lower() for r in results)


def test_get_order_status():
    order = sql_tool.get_order_status(1)
    assert order is not None
    assert order["status"] == "delivered"
