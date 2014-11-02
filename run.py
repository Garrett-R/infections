#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Garrett Reynolds
"""

import argparse
from save_load import _try_converting_to_int, load_users, save_users
from infections import total_infection, limited_infection


def main():
    parser = argparse.ArgumentParser(description=
                                     "Split users for A/B testing, minimizing "
                                     "connections between groups")

    parser.add_argument('-i', '--input', help="Input .csv file where the first number is the user ID, and the following numbers (if any) are IDs of students",
                        type=str, required=True)
    parser.add_argument('-o', '--output', help="Ouput .csv file where infected user IDs will be saved to", required=False, type=str)
    parser.add_argument('-t', '--total', help="Set this to do total infection.  You must then also give a user ID", action="store_true", required=False)
    parser.add_argument('-u', '--user', help="First infected user when we're doing total infection", required=False, type=int)
    parser.add_argument('-l', '--limited', help="Limited infection", action="store_true", required=False)
    parser.add_argument('-n', '--numToInfect', required=False, type=float,
                        help="""(int or float) If integer, that is the number
                        of people who will be infected.  If float, then it must
                        be between 0 and 1 and represents the proportion of
                        infected people.)""")
    parser.add_argument('-e', '--tolerance', required=False, type=float,
                        help="""(int or float) The tolerance in number of infected people
                        setting it to be greater than zero makes it more likely to
                        find a subset without conflicts.  If it is a float, it'll
                        be interpreted as a proportion of the total population.
                        (ignored if perfect_only is True)""")
    parser.add_argument('-v', '--verbose', action="store_true", required=False)

    args = parser.parse_args()

    if args.total and not args.user:
        print("You asked for total infection, so you must specify a starting "
              "user ID.  Exiting...")
        return

    if args.total and args.limited:
        print("You can't do total and limited infection at the same time! "
              "Exiting....")
        return

    if args.limited and not args.numToInfect:
        print("You're doing limited so you must specify the number to infect "
              "by adding, for example, '-n 70'.  Exiting....")
        return

    if not (args.total or args.limited):
        if args.user is not None:
            print("We assume you want to do total infection.")
            args.total = True
        else:
            print("You must have either total (-t) or limited (-l) flag set, "
                  "type 'run.py --help' for more information.\nExiting...")
            return

    if args.user is not None:
        args.user = _try_converting_to_int(args.user)

    print("Loading users...")
    users = load_users(args.input)
    print("Finished loading.")
    # convert to dictionary
    users = {user.get_uid():user for user in users}

    if args.total:
        infected_uids = total_infection(users[args.user])
        if verbose:
            print("A total of", len(infected_uids), "users were infected.")
    elif args.limited:
        if args.tolerance is None:
            args.tolerance = 0
        infected_uids = limited_infection(users, args.numToInfect,
                                           args.tolerance, args.verbose)

    if args.output is None:
        print("No ouput file specified, so results won't be saved")
    else:
        print("Saving infected users to:", args.output)
        infected_users = set((users[uid] for uid in infected_uids))
        save_users(infected_users, args.output)

    return






if __name__ == '__main__':
    main()
