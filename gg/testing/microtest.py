class TestCase:
    def __init__(self):
        self.failed = False
        self.failure_message = ""

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