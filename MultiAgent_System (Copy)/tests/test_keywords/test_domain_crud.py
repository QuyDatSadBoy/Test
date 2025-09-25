import uuid

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.keywords.models import Domain
from tests.conftest import MOCK_USER_ID

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.keywords,
]


async def test_create_domain_status_code(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
) -> None:
    """Test creating a domain returns correct status code."""
    domain_data = {
        "name": "Test Domain 111",
    }

    response = await client.post(
        "/keywords/domains/",
        json=domain_data,
    )
    print("response", response)
    assert response.status_code == status.HTTP_201_CREATED


async def test_create_domain_saved_in_db(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
) -> None:
    """Test created domain is properly saved in database."""
    domain_data = {
        "name": "Test Domain DB",
    }

    response = await client.post(
        "/keywords/domains/",
        json=domain_data,
    )

    created_domain = await session.scalar(
        select(Domain).where(Domain.name == domain_data["name"])
    )
    assert created_domain is not None
    assert created_domain.name == domain_data["name"]
    assert created_domain.created_by == MOCK_USER_ID


async def test_get_domain_status_code(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
) -> None:
    """Test getting a domain returns correct status code."""
    # Create test domain first
    domain = Domain(id=uuid.uuid4(), name="Test Domain Get")
    session.add(domain)
    await session.commit()

    response = await client.get(
        f"/keywords/domains/{domain.id}",
    )

    assert response.status_code == status.HTTP_200_OK


async def test_get_domain_data(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
) -> None:
    """Test getting a domain returns correct data."""
    # Create test domain first
    domain = Domain(id=uuid.uuid4(), name="Test Domain Get Data")
    session.add(domain)
    await session.commit()

    response = await client.get(
        f"/keywords/domains/{domain.id}",
    )

    domain_data = response.json()
    assert domain_data["name"] == domain.name
    assert domain_data["id"] == str(domain.id)


async def test_update_domain_status_code(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
) -> None:
    """Test updating a domain returns correct status code."""
    # Create test domain first
    domain = Domain(id=uuid.uuid4(), name="Test Domain Update")
    session.add(domain)
    await session.commit()

    update_data = {
        "name": "Updated Domain Name",
    }

    response = await client.patch(
        f"/keywords/domains/{domain.id}",
        json=update_data,
    )

    assert response.status_code == status.HTTP_200_OK


async def test_update_domain_in_db(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
) -> None:
    """Test domain is properly updated in database."""
    # Create test domain first
    domain = Domain(id=uuid.uuid4(), name="Test Domain Update DB")
    session.add(domain)
    await session.commit()

    update_data = {
        "name": "Updated Domain Name DB",
    }

    await client.patch(
        f"/keywords/domains/{domain.id}",
        json=update_data,
    )

    updated_domain = await session.get(Domain, domain.id)
    assert updated_domain is not None
    assert updated_domain.name == update_data["name"]
    assert updated_domain.updated_by == MOCK_USER_ID


async def test_delete_domain_status_code(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
) -> None:
    """Test deleting a domain returns correct status code."""
    # Create test domain first
    domain = Domain(id=uuid.uuid4(), name="Test Domain Delete")
    session.add(domain)
    await session.commit()

    response = await client.delete(
        f"/keywords/domains/{domain.id}",
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_delete_domain_from_db(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
) -> None:
    """Test domain is properly deleted from database."""
    # Create test domain first
    domain = Domain(id=uuid.uuid4(), name="Test Domain Delete DB")
    session.add(domain)
    await session.commit()

    await client.delete(
        f"/keywords/domains/{domain.id}",
    )

    deleted_domain = await session.get(Domain, domain.id)
    assert deleted_domain is None


async def test_list_domains_status_code(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
) -> None:
    """Test listing domains returns correct status code."""
    response = await client.get(
        "/keywords/domains/",
    )

    assert response.status_code == status.HTTP_200_OK


async def test_list_domains_data(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
) -> None:
    """Test listing domains returns correct data."""
    # Create test domains first
    domains = [Domain(id=uuid.uuid4(), name=f"Test Domain List {i}") for i in range(3)]
    for domain in domains:
        session.add(domain)
    await session.commit()

    response = await client.get(
        "/keywords/domains/",
    )

    domains_data = response.json()
    assert len(domains_data) >= 3  # There might be other domains from other tests
    assert all(isinstance(d["id"], str) for d in domains_data)
    assert all(isinstance(d["name"], str) for d in domains_data)
    # Verify our test domains are in the list
    domain_names = [d["name"] for d in domains_data]
    assert all(d.name in domain_names for d in domains)
