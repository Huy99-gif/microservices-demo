import os
import time

import requests
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError

app = Flask(__name__)

# Bat buoc phai co DATABASE_URL, vd:
# postgresql+psycopg2://product_svc:<password>@localhost:5432/products_db
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:5001")


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    owner_id = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "owner_id": self.owner_id,
        }


def init_db(retries=30, delay=2):
    """Tao bang + du lieu mau. Thu lai neu PostgreSQL chua san sang."""
    for attempt in range(retries):
        try:
            with app.app_context():
                db.create_all()
                if Product.query.count() == 0:
                    db.session.add_all([
                        Product(name="Laptop", price=1200, owner_id=1),
                        Product(name="Chuot khong day", price=25, owner_id=2),
                        Product(name="Ban phim co", price=80, owner_id=1),
                    ])
                    db.session.commit()
            return
        except OperationalError:
            if attempt == retries - 1:
                raise
            time.sleep(delay)


init_db()


def get_owner_name(owner_id):
    """Goi user-service de lay ten chu so huu; loi thi tra ve None."""
    try:
        resp = requests.get(f"{USER_SERVICE_URL}/users/{owner_id}", timeout=2)
        if resp.status_code == 200:
            return resp.json().get("name")
    except requests.RequestException:
        pass
    return None


def with_owner(product):
    item = product.to_dict()
    item["owner_name"] = get_owner_name(product.owner_id)
    return item


@app.route("/health")
def health():
    return jsonify(status="UP", service="product-service")


@app.route("/products", methods=["GET"])
def list_products():
    products = Product.query.order_by(Product.id).all()
    return jsonify([with_owner(p) for p in products])


@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        return jsonify(error="not found"), 404
    return jsonify(with_owner(product))


@app.route("/products", methods=["POST"])
def create_product():
    data = request.get_json(silent=True) or {}
    if not all(k in data for k in ("name", "price", "owner_id")):
        return jsonify(error="name, price, owner_id are required"), 400
    product = Product(name=data["name"], price=data["price"], owner_id=data["owner_id"])
    db.session.add(product)
    db.session.commit()
    return jsonify(with_owner(product)), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
