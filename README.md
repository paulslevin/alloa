# alloa
Project allocation software

At the University of Glasgow, mathematics students must do an undergraduate project (dissertation) in 4th year.
This software automates the labourious process of assigning projects to students.

We represent each student/project/academic as agents within hierarchies (level 1 for students, level 2 for projects,
level 3 for academics). Each agent has an (ordered) list of preferences of agents at the next higher level.
Specifically, this means that each student has a list of projects they want to do, and each project has a list of
academics that are suited to supervising it.

The algorithm assigns students to projects by minimising unhappiness; that is, we minimise the occurrence of situations
where students are assigned projects they give a low preference rating to. This algorithm is a variant of SPA as in
http://www.sciencedirect.com/science/article/pii/S1570866706000207

# How to run
Type python alloa.py in the command line which will take the projects, students, academics files in the test folder
and generate the allocation. You may need to install the networkx library. The allocation_* files in /test are the 
outputs of the program.