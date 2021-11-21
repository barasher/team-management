import unittest
import datetime
import main


class TestGetDays(unittest.TestCase):

    def test_nominal(self):
        days = main.get_days(datetime.date(2021, 1, 1), datetime.date(2021, 1, 10))
        self.assertEqual(len(days), 6)
        self.assertIn(datetime.date(2021, 1, 1), days)
        self.assertIn(datetime.date(2021, 1, 4), days)
        self.assertIn(datetime.date(2021, 1, 5), days)
        self.assertIn(datetime.date(2021, 1, 6), days)
        self.assertIn(datetime.date(2021, 1, 7), days)
        self.assertIn(datetime.date(2021, 1, 8), days)

    def test_start_after_end(self):
        with self.assertRaises(Exception):
            main.Manager.get_days(datetime.date(2021, 1, 10), datetime.date(2021, 1, 1))


class TestManagerAddProject(unittest.TestCase):
    def test_nominal(self):
        m = main.Manager(datetime.date(2021, 1, 1),
                         datetime.date(2021, 1, 10),
                         main.TeamProjPercent.empty(),
                         main.Holidays.empty())
        with self.assertRaises(Exception):
            m.get_project("projId")
        p = main.Project("projId", "projName")
        m.add_project(p)
        p2 = m.get_project("projId")
        self.assertEqual(p, p2)


class TestTeamProjPercent(unittest.TestCase):
    def test_nominal(self):
        tpp = main.TeamProjPercent.load("testdata/projPart.json")
        with self.assertRaises(Exception):
            tpp.get_agent_project_percentage("Robert")
        self.assertEqual(tpp.get_agent_project_percentage("John"), 0.7)
        self.assertEqual(tpp.get_agent_project_percentage("Doe"), 0.3)

    def test_file_not_found(self):
        with self.assertRaises(Exception):
            tpp = main.TeamProjPercent.load("nonExistingFile.json")


class TestManagerAddAssignment(unittest.TestCase):
    def test_nominal(self):
        # projectA
        #   Bob     1/1/2021 - 10/1/2021
        #   John    1/1/2021 - 5/1/2021
        # projectB
        #   Bob     2/1/2021 - 6/1/2021
        m = main.Manager(datetime.date(2021, 1, 1),
                         datetime.date(2021, 1, 10),
                         main.TeamProjPercent.empty(),
                         main.Holidays.empty())
        m.add_project(main.Project("projectA", "project A name"))
        m.add_assignment("projectA", main.Assignment("Bob", datetime.date(2021, 1, 1), datetime.date(2021, 1, 10)))
        m.add_assignment("projectA", main.Assignment("John", datetime.date(2021, 1, 1), datetime.date(2021, 1, 5)))
        m.add_project(main.Project("projectB", "project B name"))
        m.add_assignment("projectB", main.Assignment("Bob", datetime.date(2021, 1, 2), datetime.date(2021, 1, 6)))

        # get_assignment_count
        self.assertEqual(m.get_assignment_count("Bob", datetime.date(2021, 1, 1)), 1)
        self.assertEqual(m.get_assignment_count("Bob", datetime.date(2021, 1, 4)), 2)
        self.assertEqual(m.get_assignment_count("Bob", datetime.date(2021, 1, 30)), 0)

        # get_agents
        self.assertSetEqual(m.get_agents("projectA", datetime.date(2021, 1, 1)), set(["Bob", "John"]))
        self.assertSetEqual(m.get_agents("projectA", datetime.date(2021, 1, 8)), set(["Bob"]))
        self.assertSetEqual(m.get_agents("projectA", datetime.date(2021, 1, 30)), set())


class TestHolidays(unittest.TestCase):
    def test_nominal(self):
        h = main.Holidays.load("testdata/holidays.csv")
        self.assertEqual(h.get("John", "2021_01"), 5)
        self.assertEqual(h.get("John", "2021_02"), 3)
        self.assertEqual(h.get("Doe", "2021_01"), 2)
        self.assertEqual(h.get("Doe", "2021_02"), 8)
        self.assertEqual(h.get("Bob", "2021_01"), 0)
        self.assertEqual(h.get("John", "2021_12"), 0)

    def test_file_not_found(self):
        with self.assertRaises(Exception):
            tpp = main.Holidays.load("nonExistingFile.json")


class TestHolidays(unittest.TestCase):
    def test_nominal(self):
        self.assertEqual(main.opened_days_in_month("2021_1"), 21)
        self.assertEqual(main.opened_days_in_month("2021_2"), 20)


class TestManagerSummary(unittest.TestCase):
    def test(self):
        h = main.Holidays.load("testdata/holidays.csv")
        tpp = main.TeamProjPercent.load("testdata/projPart.json")
        m = main.Manager(
            datetime.date(2021, 1, 1),
            datetime.date(2021, 2, 28),
            tpp,
            h
        )

        # projectA
        #   Doe     1/1/2021 - 15/2/2021
        #   John    1/1/2021 - 5/1/2021
        # projectB
        #   Doe     1/2/2021 - 28/2/2021
        # projectC
        #   John    6/1/2021 - 28/02/2021

        m.add_project(main.Project("projectA", "project A name"))
        m.add_assignment("projectA", main.Assignment("Doe", datetime.date(2021, 1, 1), datetime.date(2021, 2, 15)))
        m.add_assignment("projectA", main.Assignment("John", datetime.date(2021, 1, 1), datetime.date(2021, 1, 5)))
        m.add_project(main.Project("projectB", "project B name"))
        m.add_assignment("projectB", main.Assignment("Doe", datetime.date(2021, 2, 1), datetime.date(2021, 2, 28)))
        m.add_project(main.Project("projectC", "project C name"))
        m.add_assignment("projectC", main.Assignment("John", datetime.date(2021, 1, 6), datetime.date(2021, 2, 28)))

        res = m.summary()
        self.assertEqual(res["project A name"]["2021_1"], 7.3)
        self.assertEqual(res["project A name"]["2021_2"], 0.99)
        self.assertEqual(res["project B name"]["2021_1"], 0)
        self.assertEqual(res["project B name"]["2021_2"], 2.61)
        self.assertEqual(res["project C name"]["2021_1"], 9.6)
        self.assertEqual(res["project C name"]["2021_2"], 11.9)


if __name__ == '__main__':
    unittest.main()
