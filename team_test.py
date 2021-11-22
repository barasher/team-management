import unittest
import datetime
import team


class TestGetDays(unittest.TestCase):

    def test_nominal(self):
        days = team.get_days(datetime.date(2021, 1, 1), datetime.date(2021, 1, 10))
        self.assertEqual(len(days), 6)
        self.assertIn(datetime.date(2021, 1, 1), days)
        self.assertIn(datetime.date(2021, 1, 4), days)
        self.assertIn(datetime.date(2021, 1, 5), days)
        self.assertIn(datetime.date(2021, 1, 6), days)
        self.assertIn(datetime.date(2021, 1, 7), days)
        self.assertIn(datetime.date(2021, 1, 8), days)

    def test_start_after_end(self):
        with self.assertRaises(Exception):
            team.Manager.get_days(datetime.date(2021, 1, 10), datetime.date(2021, 1, 1))


class TestManagerAddProject(unittest.TestCase):
    def test_nominal(self):
        m = team.Manager(datetime.date(2021, 1, 1),
                         datetime.date(2021, 1, 10),
                         team.Team.empty())
        with self.assertRaises(Exception):
            m.get_project("projId")
        p = team.Project("projId", "projName")
        m.add_project(p)
        p2 = m.get_project("projId")
        self.assertEqual(p, p2)


class TestManagerAddAssignment(unittest.TestCase):
    def test_nominal(self):
        # projectA
        #   Bob     1/1/2021 - 10/1/2021
        #   John    1/1/2021 - 5/1/2021
        # projectB
        #   Bob     2/1/2021 - 6/1/2021
        m = team.Manager(datetime.date(2021, 1, 1),
                         datetime.date(2021, 1, 10),
                         team.Team.empty())
        m.add_project(team.Project("projectA", "project A name"))
        m.add_assignment("projectA", team.Assignment("Bob", datetime.date(2021, 1, 1), datetime.date(2021, 1, 10)))
        m.add_assignment("projectA", team.Assignment("John", datetime.date(2021, 1, 1), datetime.date(2021, 1, 5)))
        m.add_project(team.Project("projectB", "project B name"))
        m.add_assignment("projectB", team.Assignment("Bob", datetime.date(2021, 1, 2), datetime.date(2021, 1, 6)))

        # get_assignment_count
        self.assertEqual(m.get_assignment_count("Bob", datetime.date(2021, 1, 1)), 1)
        self.assertEqual(m.get_assignment_count("Bob", datetime.date(2021, 1, 4)), 2)
        self.assertEqual(m.get_assignment_count("Bob", datetime.date(2021, 1, 30)), 0)

        # get_agents
        self.assertSetEqual(m.get_agents("projectA", datetime.date(2021, 1, 1)), set(["Bob", "John"]))
        self.assertSetEqual(m.get_agents("projectA", datetime.date(2021, 1, 8)), set(["Bob"]))
        self.assertSetEqual(m.get_agents("projectA", datetime.date(2021, 1, 30)), set())


class TestTeam(unittest.TestCase):
    def test_get_holidays(self):
        h = team.Team.load("testdata/team.csv")
        self.assertEqual(h.get_holidays("John", "2021_1"), 5)
        self.assertEqual(h.get_holidays("John", "2021_2"), 3)
        self.assertEqual(h.get_holidays("Doe", "2021_1"), 2)
        self.assertEqual(h.get_holidays("Doe", "2021_2"), 8)
        with self.assertRaises(Exception):
            h.get_holidays("Bob", "2021_1")
        with self.assertRaises(Exception):
            h.get_holidays("John", "2021_12")

    def test_get_project_percent(self):
        h = team.Team.load("testdata/team.csv")
        self.assertEqual(h.get_project_percent("John"), 0.7)
        self.assertEqual(h.get_project_percent("Doe"), 0.3)
        with self.assertRaises(Exception):
            h.get_project_percent("Alfred")

    def test_file_not_found(self):
        with self.assertRaises(Exception):
            team.Team.load("nonExistingFile.json")

    def test_exists(self):
        h = team.Team.load("testdata/team.csv")
        self.assertTrue(h.exists("John"))
        self.assertTrue(h.exists("Doe"))
        self.assertFalse(h.exists("Alfred"))

class TestOpenedDaysInMonth(unittest.TestCase):
    def test_nominal(self):
        self.assertEqual(team.opened_days_in_month("2021_1"), 21)
        self.assertEqual(team.opened_days_in_month("2021_2"), 20)


class TestManagerSummary(unittest.TestCase):
    def test(self):
        h = team.Team.load("testdata/team.csv")
        m = team.Manager(
            datetime.date(2021, 1, 1),
            datetime.date(2021, 2, 28),
            h
        )

        # projectA
        #   Doe     1/1/2021 - 15/2/2021
        #   John    1/1/2021 - 5/1/2021
        # projectB
        #   Doe     1/2/2021 - 28/2/2021
        # projectC
        #   John    6/1/2021 - 28/02/2021

        m.add_project(team.Project("projectA", "project A name"))
        m.add_assignment("projectA", team.Assignment("Doe", datetime.date(2021, 1, 1), datetime.date(2021, 2, 15)))
        m.add_assignment("projectA", team.Assignment("John", datetime.date(2021, 1, 1), datetime.date(2021, 1, 5)))
        m.add_project(team.Project("projectB", "project B name"))
        m.add_assignment("projectB", team.Assignment("Doe", datetime.date(2021, 2, 1), datetime.date(2021, 2, 28)))
        m.add_project(team.Project("projectC", "project C name"))
        m.add_assignment("projectC", team.Assignment("John", datetime.date(2021, 1, 6), datetime.date(2021, 2, 28)))

        res = m.summary()
        self.assertEqual(res["project A name"]["2021_1"], 7.3)
        self.assertEqual(res["project A name"]["2021_2"], 0.99)
        self.assertEqual(res["project B name"]["2021_1"], 0)
        self.assertEqual(res["project B name"]["2021_2"], 2.61)
        self.assertEqual(res["project C name"]["2021_1"], 9.6)
        self.assertEqual(res["project C name"]["2021_2"], 11.9)


if __name__ == '__main__':
    unittest.main()
