"""Mini API FastAPI pour le projet DevOps.

Expose un service HTTP minimaliste avec gestion d'items en mémoire.
"""
from __future__ import annotations

import os
from typing import Dict, List

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

APP_NAME = os.getenv("APP_NAME", "efrei-devops-api")
APP_ENV = os.getenv("APP_ENV", "development")

app = FastAPI(title=APP_NAME, version="0.1.0")

# Stockage en mémoire (remplaçable par MySQL plus tard)
_items: Dict[int, "Item"] = {}
_next_id: int = 1


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)


class Item(ItemCreate):
    id: int


@app.get("/", tags=["root"])
def root() -> dict:
    return {"app": APP_NAME, "env": APP_ENV, "status": "ok"}


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "healthy"}


@app.get("/items", response_model=List[Item], tags=["items"])
def list_items() -> List[Item]:
    return list(_items.values())


@app.get("/items/{item_id}", response_model=Item, tags=["items"])
def get_item(item_id: int) -> Item:
    if item_id not in _items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return _items[item_id]


@app.post(
    "/items",
    response_model=Item,
    status_code=status.HTTP_201_CREATED,
    tags=["items"],
)
def create_item(payload: ItemCreate) -> Item:
    global _next_id
    item = Item(id=_next_id, **payload.model_dump())
    _items[_next_id] = item
    _next_id += 1
    return item


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["items"])
def delete_item(item_id: int) -> None:
    if item_id not in _items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    del _items[item_id]
