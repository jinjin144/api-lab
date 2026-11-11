"""Run the lab's curl observations once; never modify another user's data."""
import json
from pathlib import Path
import subprocess
import uuid

ROOT = Path(__file__).parent
OUT = ROOT / "evidence"
OUT.mkdir(exist_ok=True)
COOKIE = OUT / "session-cookies.txt"
observations = {}


def curl(label, path, body=None, auth=None, method=None):
    cmd = ["curl.exe", "-sS", "--max-time", "30", "-b", str(COOKIE), "-c", str(COOKIE)]
    stdin = None
    if auth:
        cmd += ["-H", auth]
    if body is not None:
        if "password" in body:
            # Credential request bodies stay in memory, never in published evidence.
            stdin = json.dumps(body)
            cmd += ["-H", "Content-Type: application/json", "-d", "@-"]
        else:
            file = OUT / (label + ".json")
            file.write_text(json.dumps(body), encoding="utf-8")
            cmd += ["-H", "Content-Type: application/json", "-d", "@" + str(file)]
    if method:
        cmd += ["-X", method]
    cmd += ["-w", "\n%{http_code}", "https://quickpizza.grafana.com" + path]
    result = subprocess.run(cmd, input=stdin, capture_output=True, text=True, check=True)
    text, status = result.stdout.rsplit("\n", 1)
    try:
        data = json.loads(text)
    except ValueError:
        data = text
    # Never save login tokens or the potentially sensitive ratings-list body.
    if label == "create_user":
        observations[label] = {"status": int(status), "body_summary": {"keys": list(data)}}
    elif label != "login":
        observations[label] = {"status": int(status), "body": data}
    return int(status), data


curl("names", "/api/names")
curl("tools_without_token", "/api/tools")
public = "Authorization: token abcdef0123456789"
curl("vegetarian", "/api/pizza", {"mustBeVegetarian": True}, public)
user = {"username": "lab-" + uuid.uuid4().hex[:12], "password": uuid.uuid4().hex}
curl("create_user", "/api/users", user)
_, login = curl("login", "/api/users/token/login", user)
mine = "Authorization: token " + login["token"]
_, pizza = curl("own_pizza", "/api/pizza", {}, mine)
pid = pizza["pizza"]["id"]
for label, body, auth in [
    ("decimal", {"pizza_id": pid, "stars": 3.5}, mine),
    ("text", {"pizza_id": pid, "stars": "3"}, mine),
    ("missing", {"pizza_id": pid}, mine),
    ("nonexistent", {"pizza_id": 999999999, "stars": 3}, mine),
    ("no_token", {"pizza_id": pid, "stars": 3}, None),
    ("short_token", {"pizza_id": pid, "stars": 3}, "Authorization: token short"),
]:
    curl(label, "/api/ratings", body, auth)
curl("all_tools_excluded", "/api/pizza", {"excludedTools": ["Knife", "Pizza cutter", "Scissors"]}, mine)
status, data = curl("madeup_read_only", "/api/ratings", auth="Authorization: token 0000000000000000")
observations["madeup_read_only"] = {
    "status": status,
    "body_summary": {"keys": list(data), "ratings_count": len(data.get("ratings", []))} if isinstance(data, dict) else data,
}
(OUT / "curl-observations.json").write_text(json.dumps(observations, indent=2), encoding="utf-8")
COOKIE.unlink(missing_ok=True)
print(json.dumps(observations, indent=2))
