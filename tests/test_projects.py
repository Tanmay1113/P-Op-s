def test_employee_cannot_create_project(client, make_user):
    make_user("staff", role="Employee", password="long-test-password")
    client.post("/auth/login", data={"identity":"staff", "password":"long-test-password"})
    response = client.get("/projects/new")
    assert response.status_code == 403
