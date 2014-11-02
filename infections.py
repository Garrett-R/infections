# -*- coding: utf-8 -*-
"""

@author: Garrett Reynolds
"""

from __future__ import print_function
import numpy as np
from user import User
from copy import deepcopy


def total_infection(user):
    '''TODO:
    '''
    assert(isinstance(user, User))
    # the set of infected users so far
    infected_users = set((user,))
    # recursively infect all coaches and students
    _infect_coaches_students(user, infected_users)
    return infected_users   #TODO: return set of uid's instead?


def _infect_coaches_students(user, infected_users):
    '''Infect all coaches and students of the user and recursively infect
    their coaches and stuents, etc. until entire connected component is
    infected.

    INPUT:
    '''
    # infect the students and coaches of this user who aren't already infected
    for user_to_infect in (user.get_students() | user.get_coaches()
                            - infected_users):
        # due to the fact the graph can be cyclic, a user may have gotten
        # infected since starting the for loop, so we double check
        if user_to_infect in infected_users:
            continue
        infected_users.add(user_to_infect)
        _infect_coaches_students(user_to_infect, infected_users)

    return infected_users


def limited_infection(all_users, num_to_infect, tol=0, verbose=False):
    '''Find a subset of all_users while minimizing coach-student 'conflicts'

    By 'conflicts', we mean when only one party of a student-coach relationship
    is infected.

    INPUT:
        > all_users: A dictionary with UID as keys and the corresponding User
                    objects as values.
        > num_to_infected: (int or float) If integer, that is the number of people
                        who will be infected.  If float, then it must be
                        between 0 and 1 and represents the proportion of
                        infected people.
        > tolerance: (int or float) The tolerance in number of infected people
                    setting it to be greater than zero makes it more likely to
                    find a subset without conflicts.  If it is a float, it'll
                    be interpreted as a proportion of the total population.
                    (ignored if perfect_only is True)  #TODO: did I implement this?

    RETURN:
        > a set of UIDs of the infected people'''


    users_currently_infected = set()
    # while searching for an exact match, we "cure" whole connected components
    # and we want to make sure not to reconsider users who have ever been
    # infected
    users_ever_infected = set()

    if isinstance(num_to_infect, float):
        if 0.0 <= num_to_infect and num_to_infect <= 1.0:
            num_to_infect = int(num_to_infect * len(all_users))
        else:
            print("Error: the number of infected users was a float and not "
                  "between 0.0 and 1.0.  Make sure it's an integer.")
            raise RuntimeError
    if isinstance(tol, float):
        if 0.0 <= tol and tol <= 1.0:
            tol = int(tol * len(all_users))
        else:
            print("Error: the tolerance was a float and not "
                  "between 0.0 and 1.0.  Make sure it's an integer.")
            raise RuntimeError
    if num_to_infect > len(all_users):
        raise RuntimeError("You're trying to infect", num_to_infect, "users, "
                           "when you only have", len(all_users), "users.")
    if num_to_infect < 0:
        raise RuntimeError("You must infect a positive number of users.")

    # number of users in each connected component
    comp_counts = []  # TODO: update for starting with users.  and same for comp_uids, users_ever_infected
    # the uids for each connected component
    comp_uids = []

    #get all connected components and the number users in each one
    for uid, user in all_users.items():
        if uid in users_ever_infected:
            continue

        newly_infected = total_infection(user)
        num_newly_infected = len(newly_infected)

        newly_infected_uids = set((user.get_uid() for user in newly_infected))
        users_ever_infected.update(newly_infected_uids)
        comp_uids.append(newly_infected_uids)
        comp_counts.append(num_newly_infected)

#        num_infected = sum(comp_counts)
#        if (num_to_infect - tol) <= num_infected and (num_to_infect - tol) <= num_infected:
#            if verbose:
#                print("A split without any coflicts was found!")
#            #flatten
#            return set.union(*comp_uids)

    # sort the connected components from largest to smallest
    sorted_ind = np.argsort(comp_counts)
    reverse_ind = sorted_ind[::-1]
    comp_counts = [comp_counts[ind] for ind in reverse_ind]
    comp_uids = [comp_uids[ind] for ind in reverse_ind]

    # add components one at a time as long as the total doesn't overshoot
    num_infected = 0
    comps_to_keep = []
    smallest_uninfected_comp = -1
    for comp_i, comp_count in enumerate(comp_counts):
        if num_infected + comp_count > num_to_infect:
            smallest_uninfected_comp = comp_i # (we use this later on)
            continue
        num_infected += comp_count
        comps_to_keep.append(comp_i)

    infected_uids = set.union(*(comp_uids[comp_i] for comp_i in comps_to_keep))

    # if we're lucky, we got an exact split, otherwise, we'll have to break
    # up a connected component
    if (num_to_infect - tol) <= num_infected and num_infected <= (num_to_infect + tol):
        if verbose:
            print("A split without any coflicts was found!")
    else:
        # we already know the smallest uninfected component is larger than we
        # need so we only need to split that one
        smallest_comp_users = [all_users[user_i]
                               for user_i in comp_uids[smallest_uninfected_comp]]
        # number of users left to infect
        remaining_to_infect = num_to_infect - num_infected
        extra_infected_users = _split_component(smallest_comp_users,
                                                remaining_to_infect)
        if verbose:
            # report number of conflicting relationships
            num_conflicts = 0
            for user in smallest_comp_users:
                num_conflicts += _find_num_conflicts(user,
                                                     extra_infected_users)
            print("The number of conflicting relationships is: ",
                  num_conflicts)

        infected_uids.update(extra_infected_users)

    return infected_uids


def _split_component(users, remaining_to_infect, max_iter=10000):
    '''Split the graph while minimizing the number of connections between
    groups.

    We will use the Kernighan-Lin alrogithm for this graph partition.  For more
    details, see: wikipedia.org/wiki/Kernighan–Lin_algorithm.  We modify the
    algorithm to accomodate a specified number of nodes to partition out.
    This takes ~O(n^2 log(n)).
    TODO: make this function reusable instead of specific to the infection
          task.

    INPUT:
        > users: set or list with User objects
        > remaining_to_infect: integer representing how many need to be
                                infected
        > max_iter: maximum number of iterations of KL algorithm before
                    stopping and settling on the current solution.

    RETURN:
        > infected_uids: set of uids of infected users'''

    users = set(users)

    def _get_D_value(user, infected_set):
        '''see the Wikipage Kernighan-Lin algorithm for the meaning of D'''
        num_conn_infected = num_conn_uninfected = 0
        for conn in (user.get_students() | user.get_coaches()):
            if conn.get_uid() in infected_set:
                num_conn_infected += 1
            else:
                num_conn_uninfected += 1
        if user.get_uid() in infected_set:
            return num_conn_uninfected - num_conn_infected
        else:
            return num_conn_infected - num_conn_uninfected

    def _toggle_infected(uids, infected_set):
        '''toggle on/off the infected status of uids in infected_set'''
        for uid in uids:
            if uid in infected_set:
                infected_set.remove(uid)
            else:
                infected_set.update((uid,))

    num_uninfected = len(users) - remaining_to_infect
    infected_uids = set()
    users_dict = {user.get_uid():user for user in users}
    all_uids = set(users_dict.keys())

#    if remaining_to_infect <= num_uninfected:
##        fewer_infected = True
#        small_partition_size = remaining_to_infect
#    else:
##        fewer_infected = False
#        small_partition_size = num_uninfected
#    small_partition_size

    # start off by randomly assigning users to small group
    for user_i, user in enumerate(users):
        infected_uids.update((user.get_uid(),))
        if user_i + 1 >= remaining_to_infect:
            break

    for _ in range(max_iter):

        g_values = []
        g_pairs = []
        # the infected UIDs for this round
        temp_inf_uids = deepcopy(infected_uids)
        #uids that have already been moved during this round
        completed_uids = set()
        for nn in range(min(remaining_to_infect, num_uninfected)):  #(small_partition_size):  TODO
            for uid in (all_uids - completed_uids):
                user = users_dict[uid]
                user._d = _get_D_value(user, temp_inf_uids)
            # find maximum g value
            max_g_value=-1000000000
            max_g_pair = (-1, -1)
            for inf in temp_inf_uids - completed_uids:
                for non_inf in (all_uids - temp_inf_uids - completed_uids):
                    g_value = users_dict[inf]._d + users_dict[non_inf]._d \
                              -2*(_are_connected(users_dict[inf],
                                                 users_dict[non_inf]))
                    if g_value > max_g_value:
                        max_g_value = g_value
                        max_g_pair = (inf, non_inf)
            # end of find max g value
            completed_uids.update(max_g_pair)
            g_pairs.append(max_g_pair)
            g_values.append(max_g_value)
            _toggle_infected(max_g_pair, temp_inf_uids)
        # end for

        # now we find number which maximizes g_values subarray
        subarray_length = _find_max_left_justified_subarray(g_values)
        g_max = sum(g_values[:subarray_length])
        if g_max <= 0:
            break
        for g_pair_i in range(subarray_length):
            uids_to_switch = g_pairs[g_pair_i]
            _toggle_infected(uids_to_switch, infected_uids)

    #end for (KL alogorithm main loop)
    else:
        print("WARNING: maximum number of iteration reached during KL "
              "algorithm...")

    for user in users:
        del user._d

    return infected_uids


def _are_connected(user1, user2):
    '''return true if the users have a connection'''
    return user1 in (user2.get_students() | user2.get_coaches())


def _find_max_left_justified_subarray(array):
    '''return number of elements to keep in order to maximize the subarray
    which is constrained to start at the first element.'''
    subarray_length = 0
    max_sum = 0
    for ii in range(len(array)):
        current_sum = sum(array[:ii+1])
        if current_sum > max_sum:
            max_sum = current_sum
            subarray_length = ii + 1
    return subarray_length


def _find_num_conflicts(user, infected_set):
    '''Number of conlifcting relationships.  For example, if user is infected and has
    connections to 4 uninfected users, return 4.'''
    num_conn_infected = num_conn_uninfected = 0
    for conn in (user.get_students() | user.get_coaches()):
        if conn.get_uid() in infected_set:
            num_conn_infected += 1
        else:
            num_conn_uninfected += 1
    if user.get_uid() in infected_set:
        return num_conn_uninfected
    else:
        return num_conn_infected
