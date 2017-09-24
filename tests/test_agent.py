import unittest
from modules.agents import Agent, Hierarchy


class TestHierarchy(unittest.TestCase):
    
    def setUp(self):
        self.hierarchy = Hierarchy(level=1)

    def test___str__(self):
        self.assertEqual(str(self.hierarchy), 1)

    def test___repr__(self):
        self.assertEqual(self.hierarchy.__repr__(), 'HIERARCHY_1')
