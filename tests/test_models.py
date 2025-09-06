# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import pytest
from app import create_app, db
from app.models import Product
from exceptions import DataValidationError

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # in-memory DB for tests
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def sample_product():
    """Return a dictionary of valid product data."""
    return {
        'name': 'Laptop',
        'category': 'Electronics',
        'price': 999.99,
        'description': 'High-end gaming laptop',
        'available': True
    }

def test_create_product(app, sample_product):
    product = Product()
    product.deserialize(sample_product)
    product.create()

    assert product.id is not None
    assert product.name == 'Laptop'
    assert product.available is True

def test_update_product(app, sample_product):
    product = Product()
    product.deserialize(sample_product)
    product.create()

    product.price = 899.99
    product.update()

    updated = Product.query.get(product.id)
    assert updated.price == 899.99

def test_delete_product(app, sample_product):
    product = Product()
    product.deserialize(sample_product)
    product.create()

    product_id = product.id
    product.delete()

    assert Product.query.get(product_id) is None

def test_deserialize_missing_required(app):
    product = Product()
    incomplete_data = {'name': 'Laptop', 'price': 999.99}  # missing category

    with pytest.raises(DataValidationError) as exc:
        product.deserialize(incomplete_data)

    assert 'Missing category' in str(exc.value)

def test_deserialize_optional_fields(app):
    product = Product()
    data = {'name': 'Mouse', 'category': 'Electronics', 'price': 49.99}  # no description, available

    product.deserialize(data)
    product.create()

    assert product.description == ''
    assert product.available is True
