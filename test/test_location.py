import unittest
from gridly.location import Location
class TestLocation(unittest.TestCase):
	def setUp(self):
		self.location23 = Location(2, 3)
		self.location65 = Location(6, 5)

	def test_zero(self):
		self.assertEqual(Location.zero(), Location(0, 0))

	def test_add(self):
		self.assertEqual(self.location23 + self.location65, Location(8, 8))

	def test_subtract(self):
		self.assertEqual(self.location65 - self.location23, Location(4, 2))

	def test_above(self):
		pass
