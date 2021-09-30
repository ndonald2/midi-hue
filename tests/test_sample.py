class TestSample:
    value = 0

    def test_one(self):
        self.value = 1
        assert self.value == 1
