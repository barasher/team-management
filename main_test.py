import unittest
import datetime
import main


class TestManagerGetDays(unittest.TestCase):

    def test_nominal(self):
        days = main.Manager.get_days(datetime.date(2021, 1, 1), datetime.date(2021, 1, 10))
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
        m = main.Manager(datetime.date(2021, 1, 1), datetime.date(2021, 1, 10), "testdata/projPart.json")
        with self.assertRaises(Exception):
            m.get_project("projId")
        p = main.Project("projId", "projName")
        m.add_project(p)
        p2 = m.get_project("projId")
        self.assertEqual(p, p2)


class TestManagerGetAgentProjectPercentage(unittest.TestCase):
    def test_nominal(self):
        m = main.Manager(datetime.date(2021, 1, 1), datetime.date(2021, 1, 10), "testdata/projPart.json")
        with self.assertRaises(Exception):
            m.get_agent_project_percentage("Robert")
        self.assertEqual(m.get_agent_project_percentage("John"), 0.7)
        self.assertEqual(m.get_agent_project_percentage("Doe"), 0.3)

    def test_file_not_found(self):
        with self.assertRaises(Exception):
            m = main.Manager(datetime.date(2021, 1, 1), datetime.date(2021, 1, 10), "nonExistingFile.json")


class TestManagerAddAssignment(unittest.TestCase):
    def test_nominal(self):
        # projectA
        #   Bob     1/1/2021 - 10/1/2021
        #   John    1/1/2021 - 5/1/2021
        # projectB
        #   Bob     2/1/2021 - 6/1/2021
        m = main.Manager(datetime.date(2021, 1, 1), datetime.date(2021, 1, 10), "testdata/projPart.json")
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

        print(m.summary())


if __name__ == '__main__':
    unittest.main()
