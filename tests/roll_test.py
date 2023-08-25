import pytest
import pytest_asyncio
from roll import roll_using_notation, prepare_roll


async def test_roll_no_modifier():
    assert 1 <= await roll_using_notation("d10") <= 10
    assert 2 <= await roll_using_notation("2d4") <= 8


async def test_roll_with_modifier():
    assert 6 <= await roll_using_notation("2d4+4") <= 12
    assert 1 <= await roll_using_notation("2d4-1") <= 7


async def test_invalid_roll():
    assert await roll_using_notation("2") is False
    assert await roll_using_notation("2+1") is False
    assert await roll_using_notation("2d") is False
    assert await roll_using_notation("d") is False


async def test_roll_object():
    roll_object = await prepare_roll("5d7")
    assert roll_object.num_of_rolls == 5
    assert roll_object.faces == 7
    assert roll_object.modifier == 0

    roll_object_2 = await prepare_roll("10d3+4")
    assert roll_object_2.num_of_rolls == 10
    assert roll_object_2.faces == 3
    assert roll_object_2.modifier == 4
