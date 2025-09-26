import uuid

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.keywords.models import Domain, Niche
from tests.conftest import MOCK_USER_ID

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.keywords,
]


@pytest.fixture
async def setup_test_domain(session: AsyncSession):
    """Setup test domain for niche tests."""
    domain = Domain(id=uuid.uuid4(), name="Test Domain for Niche")
    session.add(domain)
    await session.commit()
    await session.refresh(domain)
    return domain


async def test_create_niche_status_code(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_domain,
) -> None:
    """Test creating a niche returns correct status code."""
    domain = setup_test_domain

    niche_data = {
        "name": "Test Niche",
        "domain_id": str(domain.id),
    }

    response = await client.post(
        "/keywords/niches/",
        json=niche_data,
    )

    assert response.status_code == status.HTTP_201_CREATED


async def test_create_niche_saved_in_db(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_domain,
) -> None:
    """Test created niche is properly saved in database."""
    domain = setup_test_domain

    niche_data = {
        "name": "Test Niche DB",
        "domain_id": str(domain.id),
    }

    response = await client.post(
        "/keywords/niches/",
        json=niche_data,
    )

    created_niche = await session.scalar(
        select(Niche).where(Niche.name == niche_data["name"])
    )
    assert created_niche is not None
    assert created_niche.name == niche_data["name"]
    assert created_niche.created_by == MOCK_USER_ID


async def test_get_niche_status_code(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_domain,
) -> None:
    """Test getting a niche returns correct status code."""
    domain = setup_test_domain

    # Create test niche first
    niche = Niche(id=uuid.uuid4(), name="Test Niche Get", domain_id=domain.id)
    session.add(niche)
    await session.commit()

    response = await client.get(
        f"/keywords/niches/{niche.id}",
    )

    assert response.status_code == status.HTTP_200_OK


async def test_get_niche_data(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_domain,
) -> None:
    """Test getting a niche returns correct data."""
    domain = setup_test_domain

    # Create test niche first
    niche = Niche(id=uuid.uuid4(), name="Test Niche Get Data", domain_id=domain.id)
    session.add(niche)
    await session.commit()

    response = await client.get(
        f"/keywords/niches/{niche.id}",
    )

    niche_data = response.json()
    assert niche_data["name"] == niche.name
    assert niche_data["id"] == str(niche.id)
    assert niche_data["domain_id"] == str(domain.id)


async def test_update_niche_status_code(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_domain,
) -> None:
    """Test updating a niche returns correct status code."""
    domain = setup_test_domain

    # Create test niche first
    niche = Niche(id=uuid.uuid4(), name="Test Niche Update", domain_id=domain.id)
    session.add(niche)
    await session.commit()

    update_data = {
        "name": "Updated Niche Name",
    }

    response = await client.patch(
        f"/keywords/niches/{niche.id}",
        json=update_data,
    )

    assert response.status_code == status.HTTP_200_OK


async def test_update_niche_in_db(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_domain,
) -> None:
    """Test niche is properly updated in database."""
    domain = setup_test_domain

    # Create test niche first
    niche = Niche(id=uuid.uuid4(), name="Test Niche Update DB", domain_id=domain.id)
    session.add(niche)
    await session.commit()

    update_data = {
        "name": "Updated Niche Name DB",
    }

    await client.patch(
        f"/keywords/niches/{niche.id}",
        json=update_data,
    )

    updated_niche = await session.get(Niche, niche.id)
    assert updated_niche is not None
    assert updated_niche.name == update_data["name"]
    assert updated_niche.updated_by == MOCK_USER_ID


async def test_delete_niche_status_code(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_domain,
) -> None:
    """Test deleting a niche returns correct status code."""
    domain = setup_test_domain

    # Create test niche first
    niche = Niche(id=uuid.uuid4(), name="Test Niche Delete", domain_id=domain.id)
    session.add(niche)
    await session.commit()

    response = await client.delete(
        f"/keywords/niches/{niche.id}",
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_delete_niche_from_db(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_domain,
) -> None:
    """Test niche is properly deleted from database."""
    domain = setup_test_domain

    # Create test niche first
    niche = Niche(id=uuid.uuid4(), name="Test Niche Delete DB", domain_id=domain.id)
    session.add(niche)
    await session.commit()

    await client.delete(
        f"/keywords/niches/{niche.id}",
    )

    deleted_niche = await session.get(Niche, niche.id)
    assert deleted_niche is None


async def test_list_niches_status_code(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
) -> None:
    """Test listing niches returns correct status code."""
    response = await client.get(
        "/keywords/niches/",
    )

    assert response.status_code == status.HTTP_200_OK


async def test_list_niches_data(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_domain,
) -> None:
    """Test listing niches returns correct data."""
    domain = setup_test_domain

    # Create test niches first
    niches = [
        Niche(id=uuid.uuid4(), name=f"Test Niche List {i}", domain_id=domain.id)
        for i in range(3)
    ]
    for niche in niches:
        session.add(niche)
    await session.commit()

    response = await client.get(
        "/keywords/niches/",
    )

    niches_data = response.json()
    assert len(niches_data) >= 3  # There might be other niches from other tests
    assert all(isinstance(n["id"], str) for n in niches_data)
    assert all(isinstance(n["name"], str) for n in niches_data)
    # Verify our test niches are in the list
    niche_names = [n["name"] for n in niches_data]
    assert all(n.name in niche_names for n in niches)


async def test_get_niches_by_domain_status_code(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_domain,
) -> None:
    """Test getting niches by domain returns correct status code."""
    domain = setup_test_domain

    response = await client.get(
        f"/keywords/domains/{domain.id}/niches/",
    )

    assert response.status_code == status.HTTP_200_OK


async def test_get_niches_by_domain_data(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_domain,
) -> None:
    """Test getting niches by domain returns correct data."""
    domain = setup_test_domain

    # Create test niches first
    niches = [
        Niche(id=uuid.uuid4(), name=f"Test Niche Domain {i}", domain_id=domain.id)
        for i in range(3)
    ]
    for niche in niches:
        session.add(niche)
    await session.commit()

    response = await client.get(
        f"/keywords/domains/{domain.id}/niches/",
    )

    niches_data = response.json()
    assert len(niches_data) >= 3  # There might be other niches from other tests
    assert all(isinstance(n["id"], str) for n in niches_data)
    assert all(isinstance(n["name"], str) for n in niches_data)
    assert all(n["domain_id"] == str(domain.id) for n in niches_data)
    # Verify our test niches are in the list
    niche_names = [n["name"] for n in niches_data]
    assert all(n.name in niche_names for n in niches)
