"""
valid tag:
@start:mm/dd/yyyy
@due:mm/dd/yyyy
@cost:3
@important, @easy
"""
import sys, os
import argparse
from datetime import datetime, timedelta

default_myNextToDo_txt = os.path.expanduser('./myNextToDo.txt')
__base_urgency__ = 1
__overdue_urgency__ = 10000
__one_day_due_urgency__ = 1000
__two_day_due_urgency__ = 100
__three_day_due_urgency__ = 50
__important_urgency__ = 10
__easy_urgency__ = 1

def parse_cmd_options(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, default=default_myNextToDo_txt)
    parser.add_argument('-n', '--num_next_actions', type=int, default=2)
    module_opt = parser.parse_args(argv)
    return module_opt

def parse_datetime_str(datetime_str):
    the_datetime = None
    for fmt in ['%m/%d/%Y', '%m/%d/%Y']:
        try:
            the_datetime = datetime.strptime(datetime_str, fmt)
        except ValueError as e:
            continue
    if the_datetime is None:
        raise ValueError('invalid date/time format.')

    return the_datetime


class ToDoEntry():
    def __init__(self, todo_entry: str):
        self.todo_entry = todo_entry
        # parse entry
        todo_entry_split_list = self.todo_entry.split('@')
        self.title = todo_entry_split_list[0].strip()

        self.start = None
        self.due = None
        self.important = False
        self.easy = False
        self.cost = 0
        self.wait = False

        for todo_entry_split in todo_entry_split_list:
            todo_entry_split = todo_entry_split.strip()
            tmp_idx = todo_entry_split.find(':')
            if tmp_idx < 0:
                tag_key = todo_entry_split
                tag_value = None
            else:
                tag_key = todo_entry_split[:tmp_idx]
                tag_value = todo_entry_split[tmp_idx + 1:]

            if tag_key == 'start' or tag_key == 's':
                self.start = parse_datetime_str(tag_value)
            if tag_key == 'due' or tag_key == 'd':
                self.due = parse_datetime_str(tag_value)
            if tag_key == 'cost' or tag_key == 'c':
                self.cost = int(tag_value)
            if tag_key == 'important' or tag_key == 'i':
                self.important = True
            if tag_key == 'easy' or tag_key == 'e':
                self.easy = True
            if tag_key == 'wait' or tag_key == 'w':
                self.wait = True

            self.risk_of_overdue = False
            self.already_overdue = False

            self.risk_of_overdue = self.get_urgency()

    def get_urgency(self):
        today = datetime.today()
        # missing start date, any important or having-due task starts from today
        if self.start is None and (self.due is not None or self.important):
            start_date = today
        else:
            start_date = None

        score_muliplier = 0
        score = 0
        if start_date is not None and start_date <= today:
            score_muliplier = 1
            score += __base_urgency__

        if self.important:
            score_muliplier *= 2.0
            score += __important_urgency__

        if self.easy:
            score += __easy_urgency__

        # compute due date
        if self.due is not None:
            due_date = self.due
            if today + timedelta(days=self.cost) <= due_date - timedelta(days=3):
                score += __three_day_due_urgency__
            elif today + timedelta(days=self.cost) <= due_date - timedelta(days=2):
                score += __two_day_due_urgency__
            elif today + timedelta(days=self.cost) <= due_date - timedelta(days=1):
                score += __one_day_due_urgency__
            else:
                score += __overdue_urgency__
                self.risk_of_overdue = True

        if self.due is not None and self.due < today:
            self.already_overdue = True

        return score_muliplier * score

    def __str__(self):
        the_str = ''
        the_str += 'Title:\t' + self.title + '\n'

        if self.already_overdue:
            the_str += 'Overdue: !!!!! Already Overdue !!!!!\n'
        elif self.risk_of_overdue:
            the_str += 'Overdue: *** High Risk *** \n'

        if self.start is not None:
            the_str += 'Start:\t' + str(self.start) + '\n'
        if self.due is not None:
            the_str += 'Due:\t' + str(self.due) + '\n'
        if self.cost is not None:
            the_str += 'Cost:\t' + str(self.cost) + '\n'
        the_str += 'Tag:\t '
        if self.important is not None:
            the_str += '[Important]'
        if self.easy is not None:
            the_str += '[Easy]'
        if self.wait is not None:
            the_str += '[Wait]'

        return the_str


def parse_todo_txt(myNextToDo_txt):
    if not os.path.isfile(myNextToDo_txt):
        print('Cannot find {}'.format(myNextToDo_txt))
        return None

    with open(myNextToDo_txt, 'r') as fid:
        file_lines = fid.readlines()

    todo_entry_list = []
    for the_line in file_lines:
        the_line = the_line.strip()
        if len(the_line) == 0 or the_line.startswith('#'):
            continue

        todo_entry_list.append(ToDoEntry(the_line))

    return todo_entry_list



if __name__ == '__main__':
    opt = parse_cmd_options(sys.argv[1:])
    myNextToDo_txt = opt.input
    todo_entry_list = parse_todo_txt(myNextToDo_txt)
    todo_entry_list.sort(key=lambda x: x.get_urgency(), reverse=True)
    print('=' * 72)
    for loop_count in range(opt.num_next_actions):
        print(todo_entry_list[loop_count])
        print('-' * 72)
    print('=' * 72)


