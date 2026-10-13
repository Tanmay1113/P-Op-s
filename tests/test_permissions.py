def test_employee_cannot_access_admin_users(client, make_user):
    make_user("staff", role="Employee", password="long-test-password")
    client.post("/auth/login", data={"identity":"staff", "password":"long-test-password"})
    response = client.get("/admin/users")
    assert response.status_code == 403

def test_anonymous_dashboard_redirects(client):
    response = client.get("/dashboard/")
    assert response.status_code in (302, 401)
