import os

from flask import Flask
from flask_cors import CORS

from config import Config
from extensions import db
from routes import bp

import models  # noqa: F401 — register SQLAlchemy models before create_all


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.register_blueprint(bp, url_prefix="/api")

    with app.app_context():
        db.create_all()
        _seed_demo_products()
        _seed_demo_user()

    return app


def _seed_demo_products():
    from decimal import Decimal

    from models import Product

    if Product.query.first() is not None:
        return
    demos = [
        Product(
            name="无线蓝牙耳机",
            description="主动降噪，通勤与运动皆宜。",
            price=Decimal("299.00"),
            stock=120,
        ),
        Product(
            name="机械键盘 87 键",
            description="红轴手感，铝合金上盖。",
            price=Decimal("459.00"),
            stock=45,
        ),
        Product(
            name="便携保温杯 500ml",
            description="316 不锈钢内胆，长效保温。",
            price=Decimal("89.90"),
            stock=200,
        ),
    ]
    for p in demos:
        db.session.add(p)
    db.session.commit()


def _seed_demo_user():
    from werkzeug.security import generate_password_hash

    from models import User

    if User.query.first() is not None:
        return
    u = User(
        username="demo",
        password_hash=generate_password_hash("demo123"),
    )
    db.session.add(u)
    db.session.commit()


app = create_app()

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="127.0.0.1", port=int(os.getenv("FLASK_PORT", "5000")), debug=debug)
