import sys
from ortools.sat.python import cp_model


def main():
    model = cp_model.CpModel()

    # 1. DATA SETUP 
    # Courses
    courses = ['C1_Prog', 'C2_Math', 'C3_Cpp_Theory', 'C3_Cpp_Lab', 'C4_CSP_Theory', 'C5_CSP_Lab']
    
    # Rooms with their capacities
    rooms_capacities = {'R1_Small': 15, 'R2_Medium': 25, 'R3_Large': 50}
    rooms = list(rooms_capacities.keys())
    
    # Available Timeslots (0, 1, 2)
    timeslots = [0, 1, 2]  

    # Students and their enrolled courses
    students = {
        'Student_1': ['C1_Prog', 'C2_Math'],      
        'Student_2': ['C3_Cpp_Theory', 'C3_Cpp_Lab', 'C4_CSP_Theory'],
        'Student_3': ['C4_CSP_Theory', 'C5_CSP_Lab'], 
        'Student_4': ['C1_Prog', 'C3_Cpp_Theory', 'C3_Cpp_Lab'],   
        'Student_5': ['C2_Math', 'C5_CSP_Lab']
    }
    
    # Calculate enrollments per course
    enrollments = {c: 0 for c in courses}
    for student_courses in students.values():
        for c in student_courses:
            enrollments[c] += 1
            
    # Add dummy students to test capacity constraints
    enrollments['C3_Cpp_Theory'] += 20 
    enrollments['C4_CSP_Theory'] += 30  

    # Teacher unavailability (Course: [Unavailable Timeslots])
    teacher_unavailable = {
        'C1_Prog': [0] 
    }

    # 2. VARIABLES 
    # x[(c, r, t)]: 1 if course 'c' is assigned to room 'r' at time 't'
    x = {}
    for c in courses:
        for r in rooms:
            for t in timeslots:
                x[(c, r, t)] = model.NewBoolVar(f'x_{c}_{r}_{t}')

    #3. CONSTRAINTS
    # 1. Each course must be scheduled exactly once
    for c in courses:
        model.Add(sum(x[(c, r, t)] for r in rooms for t in timeslots) == 1)
    # 2. Room exclusivity: A room can host at most one course per timeslot
    for r in rooms:
        for t in timeslots:
            model.Add(sum(x[(c, r, t)] for c in courses) <= 1)

    # 3. Room Capacity: If enrollments > capacity, variable must be 0
    for c in courses:
        for r in rooms:
            if enrollments[c] > rooms_capacities[r]:
                for t in timeslots:
                    model.Add(x[(c, r, t)] == 0)

    # 4. Student Conflicts: A student cannot attend two courses at the same time
    for student, student_courses in students.items():
        for i in range(len(student_courses)):
            for j in range(i + 1, len(student_courses)):
                c1 = student_courses[i]
                c2 = student_courses[j]
                
                for t in timeslots:
                    c1_active = sum(x[(c1, r, t)] for r in rooms)
                    c2_active = sum(x[(c2, r, t)] for r in rooms)
                    model.Add(c1_active + c2_active <= 1)

    # 5. Time Dependencies: Theory must be before Lab
    # Create integer variables for the time slot of specific courses
    time_vars = {}
    specific_courses = ['C4_CSP_Theory', 'C5_CSP_Lab', 'C3_Cpp_Theory', 'C3_Cpp_Lab']
    
    for c in specific_courses:
        time_vars[c] = model.NewIntVar(0, max(timeslots), f'time_{c}')
        for r in rooms:
            for t in timeslots:
                # Link the boolean variable x to the integer variable time_vars
                model.Add(time_vars[c] == t).OnlyEnforceIf(x[(c, r, t)])

    # Enforce Precedence
    model.Add(time_vars['C4_CSP_Theory'] < time_vars['C5_CSP_Lab'])
    model.Add(time_vars['C3_Cpp_Theory'] < time_vars['C3_Cpp_Lab'])

    # 6. Teacher Availability
    for c, bad_times in teacher_unavailable.items():
        for t in bad_times:
            for r in rooms:
                model.Add(x[(c, r, t)] == 0)

    #4. SOLVE AND PRINT
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f"\nSolution Found")
        print(f"{'TIME':<5} | {'ROOM':<15} | {'COURSE':<15} | {'ENROLLED':<5}")
        print("-" * 50)
        
        assignments = []
        for t in timeslots:
            for r in rooms:
                for c in courses:
                    if solver.Value(x[(c, r, t)]):
                        assignments.append((t, r, c, enrollments[c]))
        
        # Sort by time for better readability
        assignments.sort(key=lambda x: x[0])

        for item in assignments:
            print(f"{item[0]:<5} | {item[1]:<15} | {item[2]:<15} | {item[3]:<5}")
    else:
        print("No solution.")

if __name__ == '__main__':
    main()
