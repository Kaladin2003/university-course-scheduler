# University Course Scheduler

A Constraint Satisfaction Problem (CSP) solver built with Python and **Google OR-Tools**. This project automatically generates a conflict-free university timetable by optimizing course assignments based on room capacities, student enrollments, and time dependencies.

## Overview

Scheduling university courses is a complex combinatorial problem. This tool assigns **Courses** to **Rooms** and **Timeslots** while satisfying hard constraints. It demonstrates the use of Constraint Programming (CP) to solve logic puzzles that would be impossible to solve manually at scale.

## Constraints Handling

The solver respects the following real-world logic rules:

1.  **Unique Scheduling:** Every course must be scheduled exactly once.
2.  **Room Exclusivity:** A room cannot host more than one course at the same time.
3.  **Capacity Checks:** A course cannot be assigned to a room if the number of enrolled students exceeds the room's capacity (e.g., a class of 50 cannot go into a room of 15).
4.  **Student Conflicts:** If a student is enrolled in two courses, those courses cannot be scheduled at the same time.
5.  **Academic Precedence:** Specific logic ensures that **Theory** classes are always scheduled *before* their corresponding **Lab** sessions (e.g., `C3_Cpp_Theory` < `C3_Cpp_Lab`).
6.  **Teacher Availability:** Specific timeslots are blocked off for certain courses based on instructor schedules.

## Technologies

* **Language:** Python 3.x
* **Library:** [Google OR-Tools](https://developers.google.com/optimization) (CP-SAT Solver)

## Installation & Usage

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Kaladin2003/university-course-scheduler.git](https://github.com/Kaladin2003/university-course-scheduler.git)
    cd university-course-scheduler
    ```

2.  **Install dependencies:**
    ```bash
    pip install ortools
    ```

3.  **Run the scheduler:**
    ```bash
    python scheduler.py
    ```

## Example Output

When the script runs successfully, it outputs the optimal schedule in a table format:
```text
Solution Found!

TIME  | ROOM            | COURSE          | ENROLLED
--------------------------------------------------
0     | R2_Medium       | C3_Cpp_Theory   | 21   
0     | R3_Large        | C4_CSP_Theory   | 32   
1     | R1_Small        | C2_Math         | 2    
1     | R2_Medium       | C3_Cpp_Lab      | 2    
1     | R3_Large        | C5_CSP_Lab      | 2    
2     | R1_Small        | C1_Prog         | 2
```
## License

This project is licensed under the [MIT License](LICENSE).







