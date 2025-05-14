
def test_basic(request_client):

    client = request_client()

    response = client.get('/', follow=True)

    assert response.content.decode()
