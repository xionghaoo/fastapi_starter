from typing import Generic, Optional, Type, TypeVar, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import select


T = TypeVar('T')


class Repository(Generic[T]):
    def __init__(self, db: Session, model: Type[T]) -> None:
        self.db = db
        self.model = model

    def find_by_id(self, entity_id: Any) -> Optional[T]:
        return self.db.get(self.model, entity_id)

    def find_one_by(self, **filters: Any) -> Optional[T]:
        return self.db.execute(select(self.model).filter_by(**filters)).scalar_one_or_none()

    def list(self, offset: int = 0, limit: int = 100, order_by: Optional[Any] = None, descending: bool = False) -> List[T]:
        stmt = select(self.model).offset(offset).limit(limit)
        if order_by is not None:
            stmt = stmt.order_by(order_by.desc() if descending else order_by.asc())
        return list(self.db.execute(stmt).scalars().all())

    def create(self, **fields: Any) -> T:
        entity = self.model(**fields)
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def update(self, entity: T) -> T:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def find_one_where(self, *where_clauses: Any) -> Optional[T]:
        stmt = select(self.model)
        for clause in where_clauses:
            stmt = stmt.where(clause)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_where(self, *where_clauses: Any, offset: int = 0, limit: Optional[int] = None) -> List[T]:
        stmt = select(self.model)
        for clause in where_clauses:
            stmt = stmt.where(clause)
        if limit is not None:
            stmt = stmt.offset(offset).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def exists_where(self, *where_clauses: Any) -> bool:
        stmt = select(self.model)
        for clause in where_clauses:
            stmt = stmt.where(clause)
        stmt = stmt.limit(1)
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def find_max_of(self, column: Any, *where_clauses: Any) -> Optional[T]:
        stmt = select(self.model)
        for clause in where_clauses:
            stmt = stmt.where(clause)
        stmt = stmt.order_by(column.desc()).limit(1)
        return self.db.execute(stmt).scalar_one_or_none()

    def delete(self, entity: T) -> None:
        self.db.delete(entity)
        self.db.commit()

    def delete_by_id(self, entity_id: Any) -> bool:
        entity = self.find_by_id(entity_id)
        if entity is None:
            return False
        self.db.delete(entity)
        self.db.commit()
        return True


