from decimal import Decimal

from flask import jsonify, request

from auth_utils import require_auth
from extensions import db
from models import Order, Product
from routes import bp


@bp.route("/products", methods=["GET"])
def list_products():
    rows = Product.query.order_by(Product.id.desc()).limit(200).all()
    return jsonify({"items": [p.to_dict() for p in rows]})


@bp.route("/products", methods=["POST"])
@require_auth
def create_product():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name or len(name) > 200:
        return jsonify({"error": "名称为空或过长（最多 200 字）"}), 400
    try:
        price = Decimal(str(data.get("price", 0)))
    except Exception:
        return jsonify({"error": "价格格式无效"}), 400
    if price < 0 or price > Decimal("9999999.99"):
        return jsonify({"error": "价格超出范围"}), 400
    try:
        stock = int(data.get("stock", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "库存必须是整数"}), 400
    if stock < 0 or stock > 10_000_000:
        return jsonify({"error": "库存数量无效"}), 400
    desc = (data.get("description") or "").strip() or None
    if desc and len(desc) > 5000:
        return jsonify({"error": "商品描述过长"}), 400
    image_url = (data.get("image_url") or "").strip() or None
    if image_url and len(image_url) > 512:
        return jsonify({"error": "图片地址过长"}), 400

    p = Product(
        name=name,
        description=desc,
        price=price,
        stock=stock,
        image_url=image_url,
    )
    db.session.add(p)
    db.session.commit()
    return jsonify(p.to_dict()), 201


@bp.route("/orders", methods=["POST"])
@require_auth
def place_order():
    data = request.get_json(silent=True) or {}
    try:
        product_id = int(data.get("product_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "请选择有效商品"}), 400
    try:
        quantity = int(data.get("quantity", 1))
    except (TypeError, ValueError):
        return jsonify({"error": "购买数量无效"}), 400
    if quantity < 1 or quantity > 99_999:
        return jsonify({"error": "购买数量不在允许范围内"}), 400

    try:
        p = Product.query.filter_by(id=product_id).with_for_update().first()
        if p is None:
            return jsonify({"error": "商品不存在"}), 404
        if p.stock < quantity:
            return jsonify({"error": f"库存不足，当前可售 {p.stock} 件"}), 400

        line_total = (p.price * Decimal(quantity)).quantize(Decimal("0.01"))
        p.stock -= quantity
        order = Order(
            product_id=product_id,
            quantity=quantity,
            total=line_total,
        )
        db.session.add(order)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return (
        jsonify(
            {
                "order": order.to_dict(),
                "product": p.to_dict(),
                "message": "下单成功",
            }
        ),
        201,
    )


@bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})
