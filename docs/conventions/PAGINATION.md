## Pagination

Pagination system for list endpoints: declarative query parameter definition, automatic filter/search/ordering application to SQL queries, and typed responses.

### Components

| Component | Path | Purpose |
|---|---|---|
| `QueryParams` | `share.pagination.query_params` | Base class for query parameters with a builder |
| `SearchType` | `share.pagination.query_params` | Search type enum (`ILIKE`, `EXACT`) |
| `PaginatedResponse` | `share.pagination.response` | Generic response with pagination metadata |
| `FilterSet` | `share.sqlmodel.filter_set` | Applies query parameters to a SQLModel SELECT |

### Usage

#### 1. Define QueryParams (DTO)

Create a file `domains/dto/<resource>_query_params.py`:

```python
from dddesign.structure.domains.dto import DataTransferObject

from share.pagination import QueryParams, SearchType


class CampaignFilters(DataTransferObject):
    campaign_id: list[CampaignId] | None = None
    state: list[CampaignStateEnum] | None = None


CampaignQueryParams = QueryParams.build(
    'CampaignQueryParams',
    filters=CampaignFilters,
    ordering_fields=('created_at',),
    default_ordering='-created_at',
    search_fields={'name': SearchType.ILIKE},
)
```

**`QueryParams.build()` parameters:**

| Parameter | Type | Description |
|---|---|---|
| `name` | `str` | Name of the generated class |
| `filters` | `type[BaseModel] \| None` | Pydantic model with filters. `list[T]` fields use `IN`, scalar fields use `==` |
| `ordering_fields` | `tuple[str, ...] \| None` | Fields available for sorting |
| `default_ordering` | `str \| None` | Default ordering. Required when `ordering_fields` is set. `-` prefix for descending |
| `search_fields` | `dict[str, SearchType] \| None` | Fields for search. `ILIKE` — substring (case-insensitive), `EXACT` — exact match |

**Built-in fields (always available):**
- `page` — page number (>= 1, default 1)
- `limit` — page size (1–100, default 20)
- `offset` — computed property: `(page - 1) * limit`

**Alias generation:** filters are automatically mapped to `filter[field_name]` format for URLs. Reserved fields (`page`, `limit`, `search`, `ordering`) are passed as-is.

#### 2. HTTP endpoint

```python
from typing import Annotated

from fastapi import APIRouter, Query

from share.pagination import PaginatedResponse


@router.get('/')
async def campaign_list(
    project_id: ProjectId,
    account: CurrentAccountDep,
    params: Annotated[CampaignQueryParams, Query()],
) -> PaginatedResponse[Campaign]:
    return await campaign_crud_app_impl.get_list(project_id, params)
```

**URL examples:**
```
GET /campaigns/?page=1&limit=20
GET /campaigns/?ordering=-created_at
GET /campaigns/?search=newsletter
GET /campaigns/?filter[state]=DRAFT&filter[state]=INACTIVE
GET /campaigns/?search=john&filter[state]=LIVE&ordering=created_at
```

#### 3. Repository — FilterSet

`FilterSet` applies query parameters to a SQLModel SELECT:

```python
from share.sqlmodel.filter_set import FilterSet


class CampaignRepository(Repository):
    @classmethod
    async def get_list(cls, project_id: ProjectId, params: CampaignQueryParams) -> list[Campaign]:
        statement = select(CampaignModel).where(CampaignModel.project_id == project_id)
        filter_set = FilterSet(model=CampaignModel, query_params=params, base_statement=statement)
        statement = filter_set.select()

        async with Atomic() as session:
            result = await session.execute(statement)
            return [Campaign(**row.model_dump()) for row in result.scalars().all()]

    @classmethod
    async def count(cls, project_id: ProjectId, params: CampaignQueryParams) -> int:
        statement = select(CampaignModel).where(CampaignModel.project_id == project_id)
        filter_set = FilterSet(model=CampaignModel, query_params=params, base_statement=statement)
        statement = filter_set.count()

        async with Atomic() as session:
            result = await session.execute(statement)
            return result.scalar() or 0
```

**`FilterSet` parameters:**

| Parameter | Type | Description |
|---|---|---|
| `model` | `type[SQLModel]` | SQLAlchemy model for column access |
| `query_params` | `QueryParams` | Query parameters instance |
| `base_statement` | `Select` | Base SELECT statement |
| `extra_columns` | `dict[str, Any]` | Additional/computed columns for filtering (e.g., `case` expressions) |

**Methods:**
- `select()` — applies filters -> search -> ordering -> limit/offset. Returns SELECT
- `count()` — applies filters -> search, wraps in `func.count()`. Returns SELECT

**`extra_columns`** — for cases when filtering is done on a computed field rather than a model column:

```python
state_expr = case(
    (CampaignModel.is_deleted.is_(True), literal(CampaignStateEnum.ARCHIVED)),
    (active_var.c.campaign_id.is_not(None), literal(CampaignStateEnum.LIVE)),
    else_=literal(CampaignStateEnum.DRAFT),
)

statement = select(CampaignModel, state_expr.label('state'))
extra_columns = {'state': state_expr}

filter_set = FilterSet(
    model=CampaignModel,
    query_params=params,
    base_statement=statement,
    extra_columns=extra_columns,
)
```

#### 4. Application — PaginatedResponse

```python
from share.pagination import PaginatedResponse


async def get_list(self, project_id: ProjectId, params: CampaignQueryParams) -> PaginatedResponse[Campaign]:
    count = await self.campaign_app.count(project_id, params)
    campaigns = await self.campaign_app.get_list(project_id, params)
    return PaginatedResponse.factory(items=campaigns, count=count, page=params.page, limit=params.limit)
```

**Response format:**
```json
{
  "data": [...],
  "meta": {
    "pagination": {
      "count": 42,
      "page": 1,
      "limit": 20
    }
  }
}
```

### Checklist for adding a list endpoint

1. Create `domains/dto/<resource>_query_params.py` with filters and `QueryParams.build()`
2. In Repository — add `get_list` and `count` methods using `FilterSet`
3. In Application — build `PaginatedResponse.factory()`
4. In HTTP endpoint — accept `Annotated[<QueryParams>, Query()]`, return `PaginatedResponse[<Entity>]`
