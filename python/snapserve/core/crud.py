from sqlalchemy import and_
from sqlalchemy.orm import Session
from sulcilab.database import SulciLabBase


def get_all(db: Session, model:SulciLabBase, skip: int = 0, limit: int = 100):
    if limit:
        return db.query(model).offset(skip).limit(limit).all()
    else:
        return db.query(model).offset(skip).all()

def get(db: Session, model:SulciLabBase, id: int):
    return db.query(model).filter(model.id == id).first()

def get_by(db: Session, model:SulciLabBase, skip: int = 0, limit: int = 100, **filters):
    query = db.query(model).filter(and_(getattr(model, field) == value for field, value in filters.items())).offset(skip)
    # for k, v in kwargs.items():
    #     query.filter(getattr(model, k) == v)
    if limit:
        query = query.limit(limit)
    return query.all()

def get_one_by(db: Session, model:SulciLabBase, **filters):
    query = db.query(model)
    query = query.filter(and_(getattr(model, field) == value for field, value in filters.items()))
    # for k, v in kwargs.items():
    #     query.filter(getattr(model, k) == v)
    return query.first()

def create(db: Session, model:SulciLabBase, item: dict=None, commitAndRefresh=True, **kwargs):
    if item is None:
        item = {}
    for k, v in kwargs.items():
        item[k] = v
    db_item = model(**item)
    db.add(db_item)
    if commitAndRefresh:
        db.commit()
        db.refresh(db_item)
    return db_item

def update(db: Session, model:SulciLabBase, **kwargs):
    # if item is None:
    item = {}
    for k, v in kwargs.items():
        item[getattr(model, k)] = v
    #db_item = model(**item)
    query = db.query(model)
    query.filter(model.id == kwargs['id']).update(item)
    db.commit()
    #db.refresh(db_item)
    # raise NotImplementedError()
    #eturn db_item
    return get(db, model, kwargs['id'])

def delete(db: Session, model:SulciLabBase, id: int):
    query = db.query(model)
    query.filter(model.id == id).delete()
    db.commit()
    # raise NotImplementedError()