import datetime
import json
import csv
import calendar


class Project:

    def __init__(self, id, name):
        self.id = id
        self.name = name


class Assignment:

    def __init__(self, who, start, end):
        self.who = who
        self.start = start
        self.end = end


class TeamProjPercent:

    def __init__(self, agent_to_percent: dict):
        self.proj_percentage_by_agent = agent_to_percent

    def get_agent_project_percentage(self, agent: str):
        try:
            return self.proj_percentage_by_agent[agent]
        except KeyError:
            raise Exception("Can't find project percentage for agent {}".format(agent))

    @staticmethod
    def load(f: str):
        with open(f) as j:
            data = json.load(j)
        return TeamProjPercent(data)

    @staticmethod
    def empty():
        return TeamProjPercent(dict())


class Holidays:
    def __init__(self, d: dict):
        self.data = d

    @staticmethod
    def load(f: str):
        d = dict()
        with open(f) as j:
            r = csv.DictReader(j, delimiter=";")
            for line in r:
                for k, v in line.items():
                    if k != "Agent":
                        d["{}_{}".format(line["Agent"], k)] = int(v)
        return Holidays(d)

    @staticmethod
    def empty():
        return Holidays(dict())

    def get(self, who: str, month: str):
        try:
            return self.data["{}_{}".format(who, month)]
        except KeyError:
            return 0


class Manager:

    def __init__(self, start: datetime.date, end: datetime.date, tpp: TeamProjPercent, h: Holidays):
        self.start = start
        self.end = end
        self.projects = dict()
        self.agents_by_project_and_date = dict()  # projId -> day -> list<agents>
        self.assignment_count_by_day_and_agent = dict()  # projId_YYYYMMDD -> count
        self.team_proj_percent = tpp
        self.holidays = h

    def add_project(self, p):
        self.projects[p.id] = p

    def get_project(self, id):
        try:
            return self.projects[id]
        except KeyError:
            raise Exception("Project {} unknown".format(id))

    def add_assignment(self, project_id, assignment: Assignment):
        self.get_project(project_id)  # check if project exists
        agent_by_date = self.agents_by_project_and_date.get(project_id)
        if agent_by_date is None:
            agent_by_date = dict()
        for curDay in get_days(assignment.start, assignment.end):
            # save assignment for the day
            agent_list = agent_by_date.get(curDay)
            if agent_list is None:
                agent_list = list()
            agent_list.append(assignment.who)
            agent_by_date[curDay] = agent_list
            # increment task count for the day
            k = "{}_{}{}{}".format(assignment.who, curDay.year, curDay.month, curDay.day)
            count = self.assignment_count_by_day_and_agent.get(k)
            if count is None:
                count = 0
            count += 1
            self.assignment_count_by_day_and_agent[k] = count
        self.agents_by_project_and_date[project_id] = agent_by_date

    def get_assignment_count(self, who: str, day: datetime.date):
        k = "{}_{}{}{}".format(who, day.year, day.month, day.day)
        try:
            return self.assignment_count_by_day_and_agent[k]
        except KeyError:
            return 0

    def get_agents(self, proj_id: str, day: datetime.date):
        try:
            return set(self.agents_by_project_and_date[proj_id][day])
        except KeyError:
            return set()

    def summary(self):
        summary = dict()
        for proj_id, proj in self.projects.items():
            proj_report = dict()
            for day in get_days(self.start, self.end):
                day_key = "{}_{}".format(day.year, day.month)
                val = proj_report.get(day_key)
                if val is None:
                    val = 0

                for agent in self.get_agents(proj_id, day):
                    worked_days = opened_days_in_month(day_key) - self.holidays.get(agent, day_key)
                    worked_days_on_project = worked_days * self.team_proj_percent.get_agent_project_percentage(agent)
                    worked_days_on_project_per_opened_day = worked_days_on_project / opened_days_in_month(day_key)
                    to_add = worked_days_on_project_per_opened_day / self.get_assignment_count(agent, day)
                    val += to_add

                proj_report[day_key] = val

            d = {}
            for m, c in proj_report.items():
                d[m]=round(c, 2)
            summary[proj.name] = d
        return summary


def get_days(start, end):
    if start > end:
        raise Exception("Start date ({}) > end date ({})".format(start, end))
    cur = start
    delta = datetime.timedelta(days=1)
    days = list()
    while cur <= end:
        if cur.weekday() <= 4:
            days.append(cur)
        cur = cur + delta
    return days


def opened_days_in_month(ym: str):
    y, m = ym.split("_")
    y, m = int(y), int(m)
    tot_days = calendar.monthrange(y, m)[1]
    tot = 0
    for i in range(1, tot_days + 1):
        if datetime.date(y, m, i).weekday() <= 4:
            tot += 1
    return tot

# fixme : test summary
