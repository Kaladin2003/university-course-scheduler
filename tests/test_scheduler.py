import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scheduler import DEFAULT_DATA, compute_enrollments, load_data, solve  # noqa: E402


@pytest.fixture
def data():
    return load_data(DEFAULT_DATA)


def by_course(assignments):
    return {c: (t, r) for t, r, c, _ in assignments}


def test_every_course_scheduled_once(data):
    result = solve(data)
    assert result is not None
    courses = [c for _, _, c, _ in result]
    assert sorted(courses) == sorted(data["courses"])


def test_no_room_double_booked(data):
    result = solve(data)
    slots = [(t, r) for t, r, _, _ in result]
    assert len(slots) == len(set(slots))


def test_room_capacity_respected(data):
    for _, room, _, enrolled in solve(data):
        assert enrolled <= data["rooms"][room]


def test_no_student_conflicts(data):
    placed = by_course(solve(data))
    for student_courses in data["students"].values():
        times = [placed[c][0] for c in student_courses]
        assert len(times) == len(set(times))


def test_theory_before_lab(data):
    placed = by_course(solve(data))
    for before, after in data["precedence"]:
        assert placed[before][0] < placed[after][0]


def test_teacher_availability(data):
    placed = by_course(solve(data))
    for course, blocked in data["teacher_unavailable"].items():
        assert placed[course][0] not in blocked


def test_enrollments_include_extra(data):
    enrollments = compute_enrollments(data)
    assert enrollments["C4_CSP_Theory"] == 32


def test_infeasible_returns_none(data):
    impossible = copy.deepcopy(data)
    impossible["timeslots"] = [0]  # 6 courses cannot fit in 3 rooms x 1 slot
    assert solve(impossible) is None
