# University Course Scheduler

![tests](https://github.com/Kaladin2003/university-course-scheduler/actions/workflows/tests.yml/badge.svg)

A Constraint Satisfaction Problem (CSP) solver built with Python and **Google OR-Tools**. It generates a conflict-free university timetable by assigning courses to rooms and timeslots based on room capacities, student enrollments and time dependencies.

## Overview

Scheduling university courses is a combinatorial problem. This tool assigns **courses** to **rooms** and **timeslots** while satisfying hard constraints, using Constraint Programming (the CP-SAT solver) to find a valid timetable that would be impractical to build by hand at scale.

## Constraints

1. **Unique scheduling:** every course is scheduled exactly once.
2. **Room exclusivity:** a room hosts at most one course per timeslot.
3. **Capacity:** a course is never placed in a room smaller than its enrollment (a class of 50 cannot go into a room of 15).
4. **Student conflicts:** a student's courses never overlap.
5. **Precedence:** a course can be required to run before another, e.g. theory before its lab (`C3_Cpp_Theory` < `C3_Cpp_Lab`).
6. **Teacher availability:** specific timeslots can be blocked for a course.

## Project structure

```text
scheduler.py          # model, solver and CLI
data/sample.json      # example problem (courses, rooms, students, rules)
tests/                # pytest suite, one test per constraint
```

## Installation & usage

```bash
git clone https://github.com/Kaladin2003/university-course-scheduler.git
cd university-course-scheduler
pip install -r requirements.txt

python scheduler.py                    # solve the sample problem
python scheduler.py my_problem.json    # solve your own problem
pytest                                 # run the tests
```

## Input format

```json
{
  "timeslots": [0, 1, 2],
  "rooms": { "R1_Small": 15, "R3_Large": 50 },
  "courses": ["C1_Prog", "C3_Cpp_Theory", "C3_Cpp_Lab"],
  "students": { "Student_1": ["C1_Prog", "C3_Cpp_Theory"] },
  "extra_enrollments": { "C3_Cpp_Theory": 20 },
  "precedence": [["C3_Cpp_Theory", "C3_Cpp_Lab"]],
  "teacher_unavailable": { "C1_Prog": [0] }
}
```

`extra_enrollments`, `precedence` and `teacher_unavailable` are optional.

## Example output

```text
Solution found!

TIME  | ROOM            | COURSE          | ENROLLED
--------------------------------------------------
0     | R1_Small        | C2_Math         | 2
0     | R2_Medium       | C3_Cpp_Theory   | 22
1     | R2_Medium       | C1_Prog         | 2
1     | R3_Large        | C4_CSP_Theory   | 32
2     | R1_Small        | C3_Cpp_Lab      | 2
2     | R3_Large        | C5_CSP_Lab      | 2
```

The solver returns any valid schedule, so the exact assignment may differ between runs or OR-Tools versions.

## License

This project is licensed under the [MIT License](LICENSE).
