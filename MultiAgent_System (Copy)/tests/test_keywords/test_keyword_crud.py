import uuid

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.keywords.models import Domain, Keyword, Niche, Subniche
from tests.conftest import MOCK_USER_ID

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.keywords,
]


@pytest.fixture
async def setup_test_data(session: AsyncSession):
    """Setup test data for keyword tests."""
    # Create domain
    domain = Domain(id=uuid.uuid4(), name="Test Domain")
    session.add(domain)
    await session.commit()
    await session.refresh(domain)

    # Create niche
    niche = Niche(id=uuid.uuid4(), name="Test Niche", domain_id=domain.id)
    session.add(niche)
    await session.commit()
    await session.refresh(niche)

    # Create subniche
    subniche = Subniche(id=uuid.uuid4(), name="Test Subniche", niche_id=niche.id)
    session.add(subniche)
    await session.commit()
    await session.refresh(subniche)

    return domain, niche, subniche


async def test_create_keyword_status_code(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_data,
) -> None:
    """Test creating a keyword returns correct status code."""
    domain, niche, subniche = setup_test_data

    keyword_data = {
        "prefix": "test",
        "main_keyword": "keyword",
        "suffix": "example",
        "domain_id": str(domain.id),
        "niche_id": str(niche.id),
        "list_sub_niche_id": [str(subniche.id)],
    }

    response = await client.post(
        "/keywords/",
        json=keyword_data,
    )

    assert response.status_code == status.HTTP_201_CREATED


async def test_create_keyword_saved_in_db(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_data,
) -> None:
    """Test created keyword is properly saved in database."""
    domain, niche, subniche = setup_test_data

    keyword_data = {
        "prefix": "test",
        "main_keyword": "keyword",
        "suffix": "example",
        "domain_id": str(domain.id),
        "niche_id": str(niche.id),
        "list_sub_niche_id": [str(subniche.id)],
    }

    response = await client.post(
        "/keywords/",
        json=keyword_data,
    )

    created_keyword = await session.scalar(
        select(Keyword).where(Keyword.main_keyword == keyword_data["main_keyword"])
    )
    assert created_keyword is not None
    assert created_keyword.main_keyword == keyword_data["main_keyword"]
    assert created_keyword.list_sub_niche_id == [uuid.UUID(subniche.id)]
    assert created_keyword.created_by == MOCK_USER_ID
    assert created_keyword.project_staff_id == MOCK_USER_ID


async def test_get_keyword_status_code(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_data,
) -> None:
    """Test getting a keyword returns correct status code."""
    domain, niche, subniche = setup_test_data

    # Create test keyword first
    keyword = Keyword(
        id=uuid.uuid4(),
        prefix="test",
        main_keyword="keyword",
        suffix="example",
        full_keyword="test keyword get",
        scan_platform=["google"],
        domain_id=domain.id,
        niche_id=niche.id,
        list_sub_niche_id=[subniche.id],
    )
    session.add(keyword)
    await session.commit()

    response = await client.get(
        f"/keywords/{keyword.id}",
    )

    assert response.status_code == status.HTTP_200_OK


async def test_update_keyword_status_code(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_data,
) -> None:
    """Test updating a keyword returns correct status code."""
    domain, niche, subniche = setup_test_data

    # Create test keyword first
    keyword = Keyword(
        id=uuid.uuid4(),
        prefix="test",
        main_keyword="keyword",
        suffix="example",
        full_keyword="test keyword update",
        scan_platform=["google"],
        domain_id=domain.id,
        niche_id=niche.id,
        list_sub_niche_id=[subniche.id],
    )
    session.add(keyword)
    await session.commit()

    update_data = {
        "main_keyword": "updated keyword",
        "full_keyword": "test updated keyword example",
    }

    response = await client.patch(
        f"/keywords/{keyword.id}",
        json=update_data,
    )

    assert response.status_code == status.HTTP_200_OK


async def test_update_keyword_in_db(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_data,
) -> None:
    """Test keyword is properly updated in database."""
    domain, niche, subniche = setup_test_data

    # Create test keyword first
    keyword = Keyword(
        id=uuid.uuid4(),
        prefix="test",
        main_keyword="keyword",
        suffix="example",
        full_keyword="test keyword update db",
        scan_platform=["google"],
        domain_id=domain.id,
        niche_id=niche.id,
        list_sub_niche_id=[subniche.id],
    )
    session.add(keyword)
    await session.commit()

    update_data = {
        "main_keyword": "updated keyword db",
        "full_keyword": "test updated keyword example db",
    }

    await client.patch(
        f"/keywords/{keyword.id}",
        json=update_data,
    )

    updated_keyword = await session.get(Keyword, keyword.id)
    assert updated_keyword is not None
    assert updated_keyword.main_keyword == update_data["main_keyword"]
    assert updated_keyword.full_keyword == update_data["full_keyword"]
    assert updated_keyword.updated_by == MOCK_USER_ID


async def test_delete_keyword_status_code(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_data,
) -> None:
    """Test deleting a keyword returns correct status code."""
    domain, niche, subniche = setup_test_data

    # Create test keyword first
    keyword = Keyword(
        id=uuid.uuid4(),
        prefix="test",
        main_keyword="keyword",
        suffix="example",
        full_keyword="test keyword delete",
        scan_platform=["google"],
        domain_id=domain.id,
        niche_id=niche.id,
        list_sub_niche_id=[subniche.id],
    )
    session.add(keyword)
    await session.commit()

    response = await client.delete(
        f"/keywords/{keyword.id}",
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_delete_keyword_from_db(
    client: AsyncClient,
    auth_settings,
    session: AsyncSession,
    setup_test_data,
) -> None:
    """Test keyword is properly deleted from database."""
    domain, niche, subniche = setup_test_data

    # Create test keyword first
    keyword = Keyword(
        id=uuid.uuid4(),
        prefix="test",
        main_keyword="keyword",
        suffix="example",
        full_keyword="test keyword delete db",
        scan_platform=["google"],
        domain_id=domain.id,
        niche_id=niche.id,
        list_sub_niche_id=[subniche.id],
    )
    session.add(keyword)
    await session.commit()

    await client.delete(
        f"/keywords/{keyword.id}",
    )

    deleted_keyword = await session.get(Keyword, keyword.id)
    assert deleted_keyword is None
