def test_employee_cannot_create_operation(client, make_user):
    make_user("staff", role="Employee", password="long-test-password")
    client.post("/auth/login", data={"identity":"staff", "password":"long-test-password"})
    response = client.get("/operations/new")
    assert response.status_code == 403
