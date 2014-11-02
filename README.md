Infections
===========

Use this to create a "limited infection" among in a graph.  We partition the graph attempting to minimize the number of edges between the two groups.

Also, "total infection" will allow you to see a connected component in the graph.

Usage
--------

Download this repository.  Then make the files `run.py` and `test.py` exectuable, by running `chmod +x run.py test.py`

**Testing**

You can now execute the unit test to make sure everything is in order:

    ./test.py

**Input**

To give an input, it must be a .csv file where, for each line, the first number is the user ID, and the following numbers (if any) are IDs of connected nodes (in Khan Academy's case, that's students.  No need to specify coaches since that's redundant ‒ see assumptions)

**Total Infection**

To spread a total infection starting from user 42,

    ./run.py --total -v --input test_data/example_large.csv --output infected_users.csv --user 42


**Limited Infection**

To create a limited infection with 2000 users, do

	./run.py --limited -v --input test_data/example_large.csv --output infected_users.csv --numToInfect 2000

You can also specify the proportion of users, so to infect half of them, do

	./run.py --limited -v --input test_data/example_large.csv --output infected_users.csv --numToInfect 0.5

If you want to infect 2000 +/- 50, you can do

	./run.py --limited -v --input test_data/example_large.csv --output infected_users.csv --numToInfect 2000 --tolerance 50

where we have a higher chance of getting a perfect split.

Assumptions
-----------

 - For the limited infection, all connections between group A and group B are equally bad (i.e. this is an unweighted graph)
 - The number of users shouldn't be much more than a few million (or computers will have gotten more memory by the time that happens)
 - A node can't be connected to itself (cycles, loops, etc. are fine)
 - There's no path through the directed graph that is more than a few thousand nodes long (in the Khan Academy case, that means we can't have a teacher of a teacher of a teacher of a teacher of...  chain lasting more than a few thousand) since that'll break our recursive strategy for finding connected components
 - (for Khan Academy application) A is a student of B if and only if B is a coach of A
 - It is possible to query KA's database to extract a unique user ID for each user as well as the user IDs of the user's students.

Algorithm
---------

For the **total infection** case, I recursively infected the students and coaches of a user.

For the **limited infection** case, the algorithm is in two parts: 
 1. Identify all connected components.  Sort them from largest to smallest.  Go through the list infecting entire components, skipping them if they're too big and will exceed the number we want to infect.  If we're lucky, we'll get an exact match from this 
 2. Partition the smallest uninfected component using the the [Kernighan-Lin algorithm](https://en.wikipedia.org/wiki/Kernighan%E2%80%93Lin_algorithm), modified to parition into unequal sizes.

To Do
---------

 - Need to fix the hodge-lodge of data structures for storing users since it's inconsistent.  We sometimes use sets of users, sets of user IDs, dictionaries of users, etc.  (Sorry!)

Here's some possible enhancements for **limited infection**,

 - Allow user to input a list of already infected users.  This would be useful because we may want to roll out the A/B testing to more users, but keeping the already infected one infected.  We may also want to decrease the number of infected users.
 - Take into account an attribute of the user and slightly prefer infections of users with similar attributes.  For example, say users have the same zip code, they're much more likely to know each other in person, so we should slightly prefer to keep them in the same group.
 - Spend more time finding perfect split.  The algorithm tends to be fairly good at finding a perfect split if there is one, but certainly not perfect.  We find the numbers of user in each connected component, then solve the problem of finding a subarry sum equal to the target infection number.  (could be prohibitively slow though)
 - Load users from file faster.  This is the slowest part, but would be easy to improve by reading multiple lines from the file at a time.2
