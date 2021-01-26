def test_default_route(client):
    res = client.get('/')

    assert res.status_code == 200
