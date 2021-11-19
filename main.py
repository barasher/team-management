import datetime
import json


class Project:

    def __init__(self, id, name):
        self.id = id
        self.name = name


class Assignment:

    def __init__(self, who, start, end):
        self.who = who
        self.start = start
        self.end = end


class Manager:

    def __init__(self, start: datetime.date, end: datetime.date, team_proj_percent: str):
        self.start = start
        self.end = end
        self.projects = dict()
        self.agents_by_project_and_date = dict()  # projId -> day -> list<agents>
        self.assignment_count_by_day_and_agent = dict()  # projId_YYYYMMDD -> count

        with open(team_proj_percent) as j:
            data = json.load(j)
        self.proj_percentage_by_agent = dict(data)

    def get_agent_project_percentage(self, agent: str):
        try:
            return self.proj_percentage_by_agent[agent]
        except KeyError:
            raise Exception("Can't find project percentage for agent {}".format(agent))

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
        for curDay in Manager.get_days(assignment.start, assignment.end):
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

    @staticmethod
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

    def summary(self):
        summary = dict()
        for proj_id, proj in self.projects.items():
            proj_report = dict()
            for day in Manager.get_days(self.start, self.end):
                day_key = "{}_{}".format(day.year, day.month)
                val = proj_report.get(day_key)
                if val is None:
                    val = 0
                val += len(self.get_agents(proj_id, day))
                proj_report[day_key] = val
            summary[proj.name] = proj_report.items()
        return summary

#fixme : test summary
#fixme : integrer le % d'activité
#fixme : integrer les taches multiples
#fixme : integrer les conges
