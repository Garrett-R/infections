# -*- coding: utf-8 -*-
"""

@author: Garrett Reynolds
"""


class User:

    __all_uids = set()

    def __init__(self, uid):
        # check for duplicate Users
        if uid in User._User__all_uids:
            raise RuntimeError("You tried to create more than one user with "
                               "uid:", uid, ". uids must be unique!")
        else:
            User._User__all_uids.update((uid,))
        self._uid = uid
        self._students = set()
        self._coaches = set()

    def add_students(self, students):
        '''Add student to this user and register this user as a coach of
        those students'''
        students = _make_iterable(students)
        self._students |= set(students)
        for student in students:
            if self not in student.get_coaches():
                student.add_coaches(self)

    def add_coaches(self, coaches):
        '''Add coaches to this user and register this user as a student of
        those coaches'''
        coaches = _make_iterable(coaches)
        self._coaches |= set(coaches)
        for coach in coaches:
            if self not in coach.get_students():
                coach.add_students(self)

    def get_students(self):
        return self._students

    def get_coaches(self):
        return self._coaches

    def get_uid(self):
        return self._uid

    @staticmethod
    def clear_users():
        '''clear the user list, in order to create new group of users'''
        User.__all_uids = set()


def _make_iterable(obj):
    '''If the argument is not iterable, we turn it into a single element
    tuple'''
    if hasattr(obj, '__contains__'):
        return obj
    else:
        obj = (obj,)
        return obj
