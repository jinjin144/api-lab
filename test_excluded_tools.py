import pytest


# A pizza never uses an excluded tool, covering zero, one and two exclusions.
@pytest.mark.parametrize("excluded", [[], ["Knife"], ["Scissors"], ["Knife", "Scissors"]])
def test_excluded_tool_is_not_used(api, auth, excluded):
    res = api.post("/api/pizza", json={"excludedTools": excluded}, headers=auth)
    assert res.status_code == 200
    assert res.json()["pizza"]["tool"] not in excluded


# An impossible request must return a client error and a useful JSON message.
@pytest.mark.xfail(reason="Defect 1: excluding all tools returns 500 with an empty body", strict=True)
def test_all_tools_excluded_is_refused(api, auth):
    res = api.post("/api/pizza", json={"excludedTools": ["Knife", "Pizza cutter", "Scissors"]}, headers=auth)
    assert res.status_code == 400
    assert res.headers["Content-Type"].startswith("application/json")
    assert isinstance(res.json().get("error"), str)
    assert res.json()["error"].strip()
