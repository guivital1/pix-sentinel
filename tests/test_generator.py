from pix_sentinel.generator import generate_transactions


def test_generator_is_deterministic() -> None:
    first = generate_transactions(10, seed=7)
    second = generate_transactions(10, seed=7)
    assert first == second
    assert len({item.transaction_id for item in first}) == 10


def test_generator_rejects_empty_batch() -> None:
    try:
        generate_transactions(0)
    except ValueError as error:
        assert "greater than zero" in str(error)
    else:
        raise AssertionError("Expected ValueError")

