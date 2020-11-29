from mlpipeline import Versions, MetricContainer
from mlpipeline.base import ExperimentABC, DataLoaderABC


class Experiment(ExperimentABC):
    def setup_model(self):
        pass

    def pre_execution_hook(self, **kwargs):
        pass

    def train_loop(self, input_fn, **kwargs):
        pass

    def evaluate_loop(self, input_fn, **kwargs):
        return MetricContainer()

    def export_model(self, **kwargs):
        pass

    def _export_model(self, export_dir):
        pass

    def post_execution_hook(self, **kwargs):
        pass


v = Versions()
v.add_version("Run-1")
EXPERIMENT = Experiment(v)
