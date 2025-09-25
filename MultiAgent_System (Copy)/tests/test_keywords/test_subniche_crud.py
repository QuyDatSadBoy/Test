import uuid

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.keywords.models import Domain, Niche, Subniche
from tests.conftest import MOCK_USER_ID

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.keywords,
]


@pytest.fixture
async def setup_test_data(session: AsyncSession):
    """Setup test data for subniche tests."""
    # Create domain
    domain = Domain(id=uuid.uuid4(), name="Test Domain for Subniche")
    session.add(domain)
    await session.commit()
    await session.refresh(domain)

    # Create niche
    niche = Niche(id=uuid.uuid4(), name="Test Niche for Subniche", domain_id=domain.id)
    session.add(niche)
    await session.commit()
    await session.refresh(niche)

    return domain, niche


async def test_create_subniche_status_code(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_data,
) -> None:
    """Test creating a subniche returns correct status code."""
    domain, niche = setup_test_data

    subniche_data = {
        "name": "Test Subniche",
        "niche_id": str(niche.id),
    }

    response = await client.post(
        "/keywords/subniches/",
        json=subniche_data,
    )

    assert response.status_code == status.HTTP_201_CREATED


async def test_create_subniche_saved_in_db(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_data,
) -> None:
    """Test created subniche is properly saved in database."""
    domain, niche = setup_test_data

    subniche_data = {
        "name": "Test Subniche DB",
        "niche_id": str(niche.id),
    }

    response = await client.post(
        "/keywords/subniches/",
        json=subniche_data,
    )

    created_subniche = await session.scalar(
        select(Subniche).where(Subniche.name == subniche_data["name"])
    )
    assert created_subniche is not None
    assert created_subniche.name == subniche_data["name"]
    assert created_subniche.created_by == MOCK_USER_ID


async def test_get_subniche_status_code(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_data,
) -> None:
    """Test getting a subniche returns correct status code."""
    domain, niche = setup_test_data

    # Create test subniche first
    subniche = Subniche(id=uuid.uuid4(), name="Test Subniche Get", niche_id=niche.id)
    session.add(subniche)
    await session.commit()

    response = await client.get(
        f"/keywords/subniches/{subniche.id}",
    )

    assert response.status_code == status.HTTP_200_OK


async def test_get_subniche_data(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_data,
) -> None:
    """Test getting a subniche returns correct data."""
    domain, niche = setup_test_data

    # Create test subniche first
    subniche = Subniche(
        id=uuid.uuid4(), name="Test Subniche Get Data", niche_id=niche.id
    )
    session.add(subniche)
    await session.commit()

    response = await client.get(
        f"/keywords/subniches/{subniche.id}",
    )

    subniche_data = response.json()
    assert subniche_data["name"] == subniche.name
    assert subniche_data["id"] == str(subniche.id)
    assert subniche_data["niche_id"] == str(niche.id)


async def test_update_subniche_status_code(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_data,
) -> None:
    """Test updating a subniche returns correct status code."""
    domain, niche = setup_test_data

    # Create test subniche first
    subniche = Subniche(id=uuid.uuid4(), name="Test Subniche Update", niche_id=niche.id)
    session.add(subniche)
    await session.commit()

    update_data = {
        "name": "Updated Subniche Name",
    }

    response = await client.patch(
        f"/keywords/subniches/{subniche.id}",
        json=update_data,
    )

    assert response.status_code == status.HTTP_200_OK


async def test_update_subniche_in_db(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_data,
) -> None:
    """Test subniche is properly updated in database."""
    domain, niche = setup_test_data

    # Create test subniche first
    subniche = Subniche(
        id=uuid.uuid4(), name="Test Subniche Update DB", niche_id=niche.id
    )
    session.add(subniche)
    await session.commit()

    update_data = {
        "name": "Updated Subniche Name DB",
    }

    await client.patch(
        f"/keywords/subniches/{subniche.id}",
        json=update_data,
    )

    updated_subniche = await session.get(Subniche, subniche.id)
    assert updated_subniche is not None
    assert updated_subniche.name == update_data["name"]
    assert updated_subniche.updated_by == MOCK_USER_ID


async def test_delete_subniche_status_code(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_data,
) -> None:
    """Test deleting a subniche returns correct status code."""
    domain, niche = setup_test_data

    # Create test subniche first
    subniche = Subniche(id=uuid.uuid4(), name="Test Subniche Delete", niche_id=niche.id)
    session.add(subniche)
    await session.commit()

    response = await client.delete(
        f"/keywords/subniches/{subniche.id}",
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_delete_subniche_from_db(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_data,
) -> None:
    """Test subniche is properly deleted from database."""
    domain, niche = setup_test_data

    # Create test subniche first
    subniche = Subniche(
        id=uuid.uuid4(), name="Test Subniche Delete DB", niche_id=niche.id
    )
    session.add(subniche)
    await session.commit()

    await client.delete(
        f"/keywords/subniches/{subniche.id}",
    )

    deleted_subniche = await session.get(Subniche, subniche.id)
    assert deleted_subniche is None


async def test_list_subniches_status_code(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
) -> None:
    """Test listing subniches returns correct status code."""
    response = await client.get(
        "/keywords/subniches/",
    )

    assert response.status_code == status.HTTP_200_OK


async def test_list_subniches_data(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_data,
) -> None:
    """Test listing subniches returns correct data."""
    domain, niche = setup_test_data

    # Create test subniches first
    subniches = [
        Subniche(id=uuid.uuid4(), name=f"Test Subniche List {i}", niche_id=niche.id)
        for i in range(3)
    ]
    for subniche in subniches:
        session.add(subniche)
    await session.commit()

    response = await client.get(
        "/keywords/subniches/",
    )

    subniches_data = response.json()
    assert len(subniches_data) >= 3  # There might be other subniches from other tests
    assert all(isinstance(s["id"], str) for s in subniches_data)
    assert all(isinstance(s["name"], str) for s in subniches_data)
    # Verify our test subniches are in the list
    subniche_names = [s["name"] for s in subniches_data]
    assert all(s.name in subniche_names for s in subniches)


async def test_get_subniches_by_niche_status_code(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_data,
) -> None:
    """Test getting subniches by niche returns correct status code."""
    domain, niche = setup_test_data

    response = await client.get(
        f"/keywords/niches/{niche.id}/subniches/",
    )

    assert response.status_code == status.HTTP_200_OK


async def test_get_subniches_by_niche_data(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_data,
) -> None:
    """Test getting subniches by niche returns correct data."""
    domain, niche = setup_test_data

    # Create test subniches first
    subniches = [
        Subniche(id=uuid.uuid4(), name=f"Test Subniche Niche {i}", niche_id=niche.id)
        for i in range(3)
    ]
    for subniche in subniches:
        session.add(subniche)
    await session.commit()

    response = await client.get(
        f"/keywords/niches/{niche.id}/subniches/",
    )

    subniches_data = response.json()
    assert len(subniches_data) >= 3  # There might be other subniches from other tests
    assert all(isinstance(s["id"], str) for s in subniches_data)
    assert all(isinstance(s["name"], str) for s in subniches_data)
    assert all(s["niche_id"] == str(niche.id) for s in subniches_data)
    # Verify our test subniches are in the list
    subniche_names = [s["name"] for s in subniches_data]
    assert all(s.name in subniche_names for s in subniches)
