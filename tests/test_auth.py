
def test_login_and_logout(client, make_user):
    make_user("staff", password="long-test-password")

    response = client.post(
        "/auth/login",
        data={
            "identity": "staff",
            "password": "long-test-password",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Welcome back" in response.data

    response = client.post("/auth/logout", follow_redirects=True)
    assert response.status_code == 200


def test_invalid_login_does_not_reveal_account(client):
    response = client.post(
        "/auth/login",
        data={"identity": "missing", "password": "wrong"},
        follow_redirects=True,
    )
    assert b"Unable to sign in with those details" in response.data


def test_registration_is_disabled(client):
    response = client.get("/auth/register")
    assert response.status_code == 403
    assert b"Public registration is disabled" in response.data

    response = client.post(
        "/auth/register",
        data={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "some-test-password",
        },
    )
    assert response.status_code == 403
