Infections
===========

Use this to create a "limited infection" among in a graph.  We partition the graph attempting to minimize the number of edges between the two groups.

Also, "total infection" will allow you to see a connected component in the graph.

Usage
--------

Download this repository.  Then make the files `run.py` and `test.py` exectuable, by running
	chmod +x run.py test.py

# Testing

You can now execute the unit test to make sure everything is in order:
	./test.py

# Input

To give an input, it must be a .csv file where, for each line, the first number is the user ID, and the following numbers (if any) are IDs of connected nodes (in KA's case, that's students.  No need to specify coaches since that's redundant)

# Total Infection

To spread a total infection starting from user 42,
	./run.py --total -v --input test_data/example_large.csv --output infected_users.csv --user 42

# Limited Infection

To create a limited infection with 2000 users, do
	./run.py --limited -v --input test_data/example_large.csv --output infected_users.csv --numToInfect 2000

You can also specify the proportion of users, so to infect half of them, do
	./run.py --limited -v --input test_data/example_large.csv --output infected_users.csv --numToInfect 0.5

If you want to infect 2000 +/- 50, you can do
	./run.py --limited -v --input test_data/example_large.csv --output infected_users.csv --numToInfect 2000 --tolerance 50
where we have a higher chance of getting a perfect split.

Notes
------

This was written for Python 3, but will also work with Python 2 although it'll be slower.

Assumptions
-----------


