AUTH = {"Authorization": "token abcdef0123456789"}


# A vegetarian request gets a named pizza with vegetarian ingredients only.
def test_vegetarian_pizza(api):
    res = api.post("/api/pizza", json={"mustBeVegetarian": True}, headers=AUTH)
    assert res.status_code == 200
    pizza = res.json()["pizza"]
    assert pizza["name"] != ""
    for ingredient in pizza["ingredients"]:
        assert ingredient["vegetarian"] is True, ingredient["name"]


# A request without a token is refused with 401 and an error message.
def test_pizza_without_token_is_refused(api):
    res = api.post("/api/pizza", json={"mustBeVegetarian": True})
    assert res.status_code == 401
    assert res.json() == {"error": "authentication failed"}
