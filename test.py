#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Garrett Reynolds
"""

from __future__ import print_function, division
from user import User
from infections import total_infection, limited_infection
from save_load import save_users, load_users
from numpy import random


def _create_users(num_users=1000, max_comp_size=50, prob_students=0.1,
                  max_students=20, seed=1):
    '''Creates an example user set

    INPUT:
        > num_users: interger number of users
        > max_comp_size: the maximum size of any connected component
        > prob_students: the probability of any give user having any students
        > max_student: the maximum students a coach may have

    RETURN:
        > users: dictionary of User objects where the keys are the uids'''
    random.seed(seed)
    users = dict()
    num_current_users = 0
    while(num_current_users < num_users):
        comp_size = random.randint(1, max_comp_size + 1)
        # make sure not overshoot the number of users needed
        if comp_size > (num_users - num_current_users):
            continue

        # create users for this connected component
        for user_i in range(num_current_users,
                            num_current_users + comp_size):
            users.update({user_i:User(user_i)})
        # link to students
        for user_i in range(num_current_users,
                            num_current_users + comp_size):
            user_has_students = (random.rand() < prob_students)
            if not user_has_students:
                continue

            num_students = random.randint(0, max_students+1)
            student_uids = random.randint(num_current_users,
                                   num_current_users + comp_size,
                                   size = num_students)
            for student_uid in student_uids:
                # you can't teach yourself
                if student_uid == user_i:
                    continue
                users[user_i].add_students(users[student_uid])

        num_current_users += comp_size
    return users


def _create_example_small():
    '''Creates a graph with three separate connected components for testing

    Do NOT change the hard-coded numbers in here without updated all the tests
    relying on them.'''
    User.clear_users()
    users = {}
    for uid in range(10):
        users.update({uid:User(uid)})

    #first connected connected component (with cycles)
    users[0].add_students(users[3])
    users[1].add_students(users[2])
    users[2].add_students((users[0], users[3]))
    users[3].add_students(users[1])
    #second connected component
    users[4].add_students((users[5], users[8], users[6]))
    users[5].add_students((users[6], users[8]))
    users[6].add_students(users[4])
    users[7].add_students(users[8])
    # users[8] has no students
    # third connected component
    # users[9] has no students

    return users


def _create_example_large():
    '''Creates a large graph or loads it from file it the file exists'''

    example_large_filename = 'test_data/example_large.csv'

    User.clear_users()

    try:
        print("Loading large example from file...")
        users = load_users(example_large_filename)
        # convert to dictionary
        users = {user.get_uid():user for user in users}
    except FileNotFoundError:
        print('Creating large example.  May take a few minutes, but you only '
              'have to do it once.')
        users = _create_users(num_users=int(1e4), prob_students=0.8,
                              max_comp_size=1000, max_students=500, seed=1)
        print('Saving users to file... (could take a few minutes)')
        save_users(users.values(), example_large_filename)

    return users


def _test_total_infection_example_small():
    users = _create_example_small()
    infected_user = users[2]
    assert(total_infection(infected_user)
            == set((0, 1, 2, 3)))

    infected_user = users[7]
    assert(total_infection(infected_user)
            == set((4, 5, 6, 7, 8)))

    infected_user = users[9]
    assert(total_infection(infected_user)
            == set((9,)))

    return True


def _test_limited_infection_example_small():
    users = _create_example_small()
    assert(limited_infection(users, 4) == set((0, 1, 2, 3)))
    assert(limited_infection(users, 5) == set((4, 5, 6, 7, 8)))
    assert(limited_infection(users, 9) == set((0, 1, 2, 3, 4, 5, 6, 7, 8)))
    assert(limited_infection(users, 0.1) == set((9,)))
    assert(limited_infection(users, 2) == set((9,0)) or
           limited_infection(users, 2) == set((9,1)))
    return True


def _test_total_infection_example_large(users_example_large):
    infected_user = users_example_large[0]
    try:
        infected_users = total_infection(infected_user)
        assert(len(infected_users) == 38)
    except RuntimeError as err:
        if (str(err) == 'maximum recursion depth exceeded'):
            print("The maximum recursion depth was exceeded.\n That means you "
                  "probably had an unrealistic graph with thousands of layers "
                  "of teachers!  (i.e. you have a teacher of a teacher of "
                  "a teacher ... and so on for a few thousand layers)")
        return False
    return True


def _test_limited_infection_example_large(users_example_large):
    infected_users = limited_infection(users_example_large,
                                       num_to_infect = 0.7,
                                       tol=0, verbose=False)
    proportion_infected = len(infected_users) / len(users_example_large)
    assert( 0.69 < proportion_infected and proportion_infected < 0.71)

    for num_to_infect in [1000, 2000, 3000, 4000, 4550]:
        infected_users = limited_infection(users_example_large,
                                           num_to_infect = num_to_infect,
                                           tol=0,
                                           verbose=True)
        assert(len(infected_users) == num_to_infect)

    return True


def run_tests():
    print('Starting tests with 10 users\n')
    if _test_total_infection_example_small():
        print("Total infection small example: PASSED")
    if _test_limited_infection_example_small():
        print("Limited infection small example: PASSED")

    users_example_large = _create_example_large()
    print('\nStarting tests with 10,000 users\n')
    if _test_total_infection_example_large(users_example_large):
        print("Total infection large example: PASSED")
    else:
        print("Total infection large example: FAILED")
    if _test_limited_infection_example_large(users_example_large):
        print("Limited infection large example: PASSED")


if __name__ == '__main__':
    run_tests()
