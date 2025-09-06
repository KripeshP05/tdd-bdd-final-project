######################################################################
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
######################################################################
"""
Product API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN

  While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_service.py:TestProductService
"""
import pytest
import json
from app import create_app, db
from app.models import Product

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Return a test client for the app."""
    return app.test_client()

@pytest.fixture
def sample_product_data():
    return {
        'name': 'Laptop',
        'category': 'Electronics',
        'price': 999.99,
        'description': 'High-end gaming laptop',
        'available': True
    }

def test_create_product_route(client, sample_product_data):
    response = client.post('/products', json=sample_product_data)
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'Laptop'
    assert 'id' in data

def test_get_product_route(client, sample_product_data):
    # Create a product first
    post_resp = client.post('/products', json=sample_product_data)
    product_id = post_resp.get_json()['id']

    # Fetch the product
    get_resp = client.get(f'/products/{product_id}')
    assert get_resp.status_code == 200
    data = get_resp.get_json()
    assert data['id'] == product_id
    assert data['name'] == 'Laptop'

def test_update_product_route(client, sample_product_data):
    # Create product
    post_resp = client.post('/products', json=sample_product_data)
    product_id = post_resp.get_json()['id']

    # Update product
    updated_data = {'name': 'Gaming Laptop', 'category': 'Electronics', 'price': 1099.99}
    put_resp = client.put(f'/products/{product_id}', json=updated_data)
    assert put_resp.status_code == 200
    data = put_resp.get_json()
    assert data['name'] == 'Gaming Laptop'
    assert data['price'] == 1099.99

def test_delete_product_route(client, sample_product_data):
    # Create product
    post_resp = client.post('/products', json=sample_product_data)
    product_id = post_resp.get_json()['id']

    # Delete product
    del_resp = client.delete(f'/products/{product_id}')
    assert del_resp.status_code == 204

    # Ensure product no longer exists
    get_resp = client.get(f'/products/{product_id}')
    assert get_resp.status_code == 404

def test_get_all_products_route(client, sample_product_data):
    # Create multiple products
    client.post('/products', json=sample_product_data)
    client.post('/products', json={**sample_product_data, 'name': 'Mouse', 'price': 49.99})

    resp = client.get('/products')
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 2
    names = [p['name'] for p in data]
    assert 'Laptop' in names
    assert 'Mouse' in names
