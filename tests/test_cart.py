import pytest

from shop.cart import Cart


def test_add_item(cart: Cart) -> None:
    cart.add("Apple", 10, 2)

    assert cart.items_count() == 2


def test_add_multiple_items(cart: Cart) -> None:
    cart.add("Apple", 10, 2)
    cart.add("Banana", 20, 3)

    assert cart.items_count() == 5


def test_add_same_item_increases_quantity(cart: Cart) -> None:
    cart.add("Apple", 10, 2)
    cart.add("Apple", 10, 3)

    assert cart.items_count() == 5


def test_remove_item(cart: Cart) -> None:
    cart.add("Apple", 10)

    cart.remove("Apple")

    assert cart.items_count() == 0


def test_total_empty_cart(cart: Cart) -> None:
    assert cart.total() == 0


def test_total(cart: Cart) -> None:
    cart.add("Apple", 10, 2)
    cart.add("Banana", 20, 3)

    assert cart.total() == 80


def test_add_negative_price_raises(cart: Cart) -> None:
    with pytest.raises(ValueError, match="price"):
        cart.add("Apple", -10)


def test_add_zero_quantity_raises(cart: Cart) -> None:
    with pytest.raises(ValueError, match="qty"):
        cart.add("Apple", 10, 0)


def test_remove_missing_item_raises(cart: Cart) -> None:
    with pytest.raises(KeyError):
        cart.remove("Apple")


def test_invalid_discount_raises(cart: Cart) -> None:
    with pytest.raises(ValueError, match="discount"):
        cart.total(discount_percent=101)


class FakeRateProvider:
    def get_rate(self, currency: str) -> float:
        return 40.0


def test_total_in(cart: Cart) -> None:
    cart.add("Apple", 100, 2)

    result = cart.total_in("USD", FakeRateProvider())

    assert result == pytest.approx(5.0)


def test_total_in_invalid_rate(cart: Cart) -> None:
    class BadRateProvider:
        def get_rate(self, currency: str) -> float:
            return 0.0

    cart.add("Apple", 100, 2)

    with pytest.raises(ValueError, match="rate"):
        cart.total_in("USD", BadRateProvider())


@pytest.mark.parametrize(
    ("discount", "expected"),
    [
        (0, 400.0),
        (10, 360.0),
        (50, 200.0),
        (100, 0.0),
    ],
)
def test_discounts(cart: Cart, discount: int, expected: float) -> None:
    cart.add("book", price=200.0, qty=2)

    assert cart.total(discount_percent=discount) == pytest.approx(expected)


def test_most_expensive(cart: Cart) -> None:
    cart.add("Apple", 100, 2)
    cart.add("Banana", 200, 1)

    item = cart.most_expensive()

    assert item is not None
    assert item.name == "Banana"
    assert item.price == 200


def test_add_same_item_with_different_price_keeps_original_price(
    cart: Cart,
) -> None:
    cart.add("Apple", 100, 1)
    cart.add("Apple", 200, 1)

    assert cart.total() == 200


def test_most_expensive_empty_cart(cart: Cart) -> None:
    assert cart.most_expensive() is None
