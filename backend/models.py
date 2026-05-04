from datetime import datetime, timezone

from extensions import db
from sqlalchemy import Numeric


def _utc_now():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=_utc_now, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "created_at": _iso_utc(self.created_at),
        }


def _iso_utc(ts):
    if ts is None:
        return None
    if ts.tzinfo is None:
        s = ts.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
    else:
        s = ts.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return s


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    image_url = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime, default=_utc_now, nullable=False)

    def to_dict(self):
        p = self.price
        return {
            "id": self.id,
            "name": self.name,
            "description": (self.description or "")[:2000],
            "price": float(p) if p is not None else 0.0,
            "stock": self.stock,
            "image_url": self.image_url,
            "created_at": _iso_utc(self.created_at),
        }


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total = db.Column(Numeric(12, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=_utc_now, nullable=False)

    def to_dict(self):
        t = self.total
        return {
            "id": self.id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "total": float(t) if t is not None else 0.0,
            "created_at": _iso_utc(self.created_at),
        }
