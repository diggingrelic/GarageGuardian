class TestCase:
    def __init__(self):
        self.failed = False
        self.failure_message = ""

    def setUp(self):
        """Optional setup before each test"""
        pass

    def tearDown(self):
        """Optional cleanup after each test"""
        pass

    def assertTrue(self, condition, msg=None):
        if not condition:
            self.failed = True
            self.failure_message = msg or "Assertion failed: expected True"
            raise AssertionError(self.failure_message)

    def assertFalse(self, condition, msg=None):
        if condition:
            self.failed = True
            self.failure_message = msg or "Assertion failed: expected False"
            raise AssertionError(self.failure_message)

    def assertEqual(self, a, b, msg=None):
        if a != b:
            self.failed = True
            self.failure_message = msg or f"Assertion failed: {a} != {b}"
            raise AssertionError(self.failure_message)

    def assertNotEqual(self, a, b, msg=None):
        if a == b:
            self.failed = True
            self.failure_message = msg or f"Assertion failed: {a} == {b}"
            raise AssertionError(self.failure_message)

    def assertIn(self, item, container, msg=None):
        if item not in container:
            self.failed = True
            self.failure_message = msg or f"Assertion failed: {item} not in {container}"
            raise AssertionError(self.failure_message)

    def assertGreater(self, first, second, msg=None):
        """Verify that first is greater than second"""
        if not first > second:
            raise AssertionError(msg or f"{first} is not greater than {second}") 

    def assertGreaterEqual(self, first, second, msg=None):
        """Verify that first is greater than or equal to second"""
        if not first >= second:
            self.failed = True
            self.failure_message = msg or f"{first} is not greater than or equal to {second}"
            raise AssertionError(self.failure_message) 