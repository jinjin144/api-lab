# The list of pizza names answers 200 and holds Margherita.
def test_names_are_listed(api):
    res = api.get("/api/names")
    assert res.status_code == 200
    assert "Margherita" in res.json()["names"]
