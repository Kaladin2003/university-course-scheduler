"""University course scheduler using the OR-Tools CP-SAT solver.

Assigns every course to exactly one (room, timeslot) pair while respecting
room capacity, room exclusivity, student conflicts, theory-before-lab
precedence and teacher availability.

Usage:
    python scheduler.py                    # uses data/sample.json
    python scheduler.py path/to/data.json
"""

import argparse
import json
import sys
from pathlib import Path

from ortools.sat.python import cp_model

DEFAULT_DATA = Path(__file__).parent / "data" / "sample.json"


def load_data(path):
    """Load a scheduling problem from a JSON file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def compute_enrollments(data):
    """Count students per course, plus any extra (non-listed) enrollments."""
    enrollments = {c: 0 for c in data["courses"]}
    for student_courses in data["students"].values():
        for c in student_courses:
            enrollments[c] += 1
    for c, extra in data.get("extra_enrollments", {}).items():
        enrollments[c] += extra
    return enrollments


def solve(data):
    """Solve the timetable.

    Returns a list of (timeslot, room, course, enrolled) tuples sorted by
    timeslot and room, or None if no valid schedule exists.
    """
    courses = data["courses"]
    rooms = data["rooms"]  # room name -> capacity
    timeslots = data["timeslots"]
    enrollments = compute_enrollments(data)

    model = cp_model.CpModel()

    # x[c, r, t] == 1 if course c is held in room r at timeslot t
    x = {
        (c, r, t): model.new_bool_var(f"x_{c}_{r}_{t}")
        for c in courses
        for r in rooms
        for t in timeslots
    }

    # 1. Every course is scheduled exactly once.
    for c in courses:
        model.add_exactly_one(x[c, r, t] for r in rooms for t in timeslots)

    # 2. A room hosts at most one course per timeslot.
    for r in rooms:
        for t in timeslots:
            model.add_at_most_one(x[c, r, t] for c in courses)

    # 3. A course never goes into a room that is too small.
    for c in courses:
        for r, capacity in rooms.items():
            if enrollments[c] > capacity:
                for t in timeslots:
                    model.add(x[c, r, t] == 0)

    # 4. A student cannot attend two courses at the same time.
    for student_courses in data["students"].values():
        for i, c1 in enumerate(student_courses):
            for c2 in student_courses[i + 1:]:
                for t in timeslots:
                    model.add(
                        sum(x[c1, r, t] for r in rooms)
                        + sum(x[c2, r, t] for r in rooms)
                        <= 1
                    )

    # 5. Precedence: the first course of each pair runs before the second.
    def time_of(c):
        return sum(t * x[c, r, t] for r in rooms for t in timeslots)

    for before, after in data.get("precedence", []):
        model.add(time_of(before) < time_of(after))

    # 6. Teacher availability.
    for c, blocked in data.get("teacher_unavailable", {}).items():
        for t in blocked:
            for r in rooms:
                model.add(x[c, r, t] == 0)

    solver = cp_model.CpSolver()
    status = solver.solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None

    assignments = [
        (t, r, c, enrollments[c])
        for t in timeslots
        for r in rooms
        for c in courses
        if solver.value(x[c, r, t])
    ]
    return sorted(assignments, key=lambda a: (a[0], a[1]))


def print_schedule(assignments):
    print("\nSolution found!\n")
    print(f"{'TIME':<5} | {'ROOM':<15} | {'COURSE':<15} | {'ENROLLED':<5}")
    print("-" * 50)
    for t, r, c, enrolled in assignments:
        print(f"{t:<5} | {r:<15} | {c:<15} | {enrolled:<5}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate a conflict-free university timetable.")
    parser.add_argument("data", nargs="?", default=DEFAULT_DATA, help="path to a JSON problem file")
    args = parser.parse_args(argv)

    assignments = solve(load_data(args.data))
    if assignments is None:
        print("No valid schedule exists for these constraints.")
        return 1
    print_schedule(assignments)
    return 0


if __name__ == "__main__":
    sys.exit(main())
