from mlpipeline.base import DataLoaderABC


class DataLoader(DataLoaderABC):
    def __init__(self):
        self.test_data = []
        self.train_data = []

    def get_test_input(self, **kwargs):
        return self.test_data

    def get_test_sample_count(self, **kwargs):
        return len(self.test_data)

    def get_train_input(self, **kwargs):
        return self.train_data

    def get_train_sample_count(self, **kwargs):
        return len(self.train_data)
