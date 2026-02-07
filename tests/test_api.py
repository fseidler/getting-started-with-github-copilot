import copy
import os
import sys

from fastapi.testclient import TestClient


sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from app import activities, app  # noqa: E402


client = TestClient(app)


def reset_activities():
    original = copy.deepcopy(activities)

    def _restore():
        activities.clear()
        activities.update(original)

    return _restore


def test_get_activities():
    restore = reset_activities()
    try:
        response = client.get("/activities")
        assert response.status_code == 200
        payload = response.json()
        assert isinstance(payload, dict)
        assert "Soccer Club" in payload
    finally:
        restore()


def test_signup_adds_participant():
    restore = reset_activities()
    try:
        response = client.post(
            "/activities/Soccer%20Club/signup",
            params={"email": "newstudent@mergington.edu"},
        )
        assert response.status_code == 200
        assert "newstudent@mergington.edu" in activities["Soccer Club"]["participants"]
    finally:
        restore()


def test_signup_duplicate_participant():
    restore = reset_activities()
    try:
        activities["Soccer Club"]["participants"].append("dupe@mergington.edu")
        response = client.post(
            "/activities/Soccer%20Club/signup",
            params={"email": "dupe@mergington.edu"},
        )
        assert response.status_code == 400
    finally:
        restore()


def test_unregister_removes_participant():
    restore = reset_activities()
    try:
        activities["Soccer Club"]["participants"].append("remove@mergington.edu")
        response = client.delete(
            "/activities/Soccer%20Club/participants",
            params={"email": "remove@mergington.edu"},
        )
        assert response.status_code == 200
        assert "remove@mergington.edu" not in activities["Soccer Club"]["participants"]
    finally:
        restore()


def test_unregister_missing_participant():
    restore = reset_activities()
    try:
        response = client.delete(
            "/activities/Soccer%20Club/participants",
            params={"email": "missing@mergington.edu"},
        )
        assert response.status_code == 404
    finally:
        restore()
