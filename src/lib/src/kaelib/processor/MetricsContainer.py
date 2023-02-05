from torch import Tensor
from typing import Callable, Optional, Union, Dict, List
from torchmetrics.classification import MulticlassAccuracy, MulticlassF1Score

MetricsName = str
CallableMetrics = Callable[[Tensor, Optional[Tensor]], Tensor]
CallableCallbacks = Callable[[MetricsName, Tensor], None]
MetricsHistoryDict = Dict[MetricsName, List[Union[float, str]]]
MetricsBatchDict = Dict[MetricsName, List[float]]


class MetricsContainer:
    metrics_fn: "Dict[MetricsName, CallableMetrics]" = {}
    __callbacks: "List[CallableCallbacks]" = []

    metrics_value_history: MetricsHistoryDict = {}
    metrics_value_batch: MetricsBatchDict = {}

    def __init__(
        self,
        metrics_fn: "Dict[MetricsName, CallableMetrics]",
        callbacks: "Optional[List[CallableCallbacks]]" = None,
    ) -> None:
        self.metrics_fn = metrics_fn
        for i in self.metrics_fn:
            self.metrics_value_history[i] = []
        if callbacks is not None:
            self.__callbacks = callbacks
        self.__build_metrics_value_batch()
        return

    def new_batch(self):
        """
        New metric batch
        """
        self.__build_metrics_value_batch()

    def process_batch(self):
        """
        Processing a batch by averaging all the value and pushing to history
        """
        mean_metric = self.__compute_mean_metrics_value(self.metrics_value_batch)
        for i in mean_metric:
            self.metrics_value_history[i].append(mean_metric[i])

    def __call__(
        self, name: MetricsName, pred: Tensor, target: Optional[Tensor] = None
    ):
        """
        Calculate a metric and pushing to batch
        """
        self.compute_metric(name, pred, target)
        return

    def compute_metric(
        self, name: MetricsName, pred: Tensor, target: Optional[Tensor] = None
    ):
        """
        Calculate a metric and pushing to batch
        """
        if name not in self.metrics_fn.keys():
            raise ValueError(f"metrics with name {name}' is not initialized")

        metrics_fn = self.metrics_fn[name]

        # Get metrics val
        detach_pred = pred.detach()
        if target is not None:
            detach_target = target.detach()
            metrics_val = metrics_fn(detach_pred, detach_target)
        else:
            metrics_val = metrics_fn(detach_pred, None)

        # Add to batch
        self.metrics_value_batch[name].append(float(metrics_val))
        # Run callback
        self.__run_callbacks(name, metrics_val)
        return

    def mean_metrics_batch(self, precision: int = 4) ->"Dict[str, Union[float, str]]":
        """
        Get current average in a batch
        """
        mean_metrics = self.__compute_mean_metrics_value(
            self.metrics_value_batch,
        )
        mean_metrics = self.__resolve_precision(precision, mean_metrics)
        return mean_metrics

    def latest_metrics_batch(
        self, precision: int = 4
    ) -> "Dict[MetricsName, Union[float,str]]":
        """
        Get the latest metrics on a batch
        """
        latest_metrics = {}
        for i in self.metrics_value_batch:
            metrics_history = self.metrics_value_batch[i]
            if len(metrics_history) > 0:
                metrics_val = metrics_history[-1]
                latest_metrics[i] = metrics_val
                if type(metrics_val) == float:
                    latest_metrics[i] = round(metrics_val, precision)  # type: ignore (bug on vscode)

        latest_metrics = self.__resolve_precision(precision, latest_metrics)
        return latest_metrics

    def latest_metrics_history(
        self, precision: int = 4
    ) -> "Dict[MetricsName,  Union[float, str]]":
        """
        Get the latest metrics on a history
        """
        latest_metrics = {}
        for i in self.metrics_value_history:
            metrics_history = self.metrics_value_history[i]
            if len(metrics_history) > 0:
                metrics_val = metrics_history[-1]
                latest_metrics[i] = metrics_val
                if type(metrics_val) == float:
                    latest_metrics[i] = round(metrics_val, precision)  # type: ignore (bug on vscode)

        latest_metrics = self.__resolve_precision(precision, latest_metrics)
        return latest_metrics

    def __run_callbacks(self, name: MetricsName, metrics_value: Tensor):
        for callback_func in self.__callbacks:
            callback_func(name, metrics_value)
        return

    def __build_metrics_value_batch(self):
        for i in self.metrics_fn:
            self.metrics_value_batch[i] = []

    def __compute_mean_metrics_value(
        self, metrics_value: Union[MetricsHistoryDict, MetricsBatchDict]
    ) -> "Dict[MetricsName, Union[float, str]]":
        final_dict = {}
        for metrics_name in metrics_value:
            current_metrics = metrics_value[metrics_name]
            # Get all float value
            float_arr = []
            for val in current_metrics:
                if type(val) == float:
                    float_arr.append(val)
            # Empty float value
            if len(float_arr) == 0:
                final_dict[metrics_name] = "Empty"
                continue
            # Not empty float
            final_dict[metrics_name] = sum(float_arr) / len(float_arr)
        return final_dict

    def __resolve_precision(
        self, precision: int, metrics_value: "Dict[MetricsName, Union[float, str]]"
    ) -> "Dict[MetricsName, Union[float, str]]":
        final_metrics = {}
        for name in metrics_value:
            val = metrics_value[name]
            final_metrics[name] = val
            if type(val) == float:
                final_metrics[name] = round(val, precision)  # type: ignore (bug on vscode)
        return final_metrics


# Example
if __name__ == "__main__":
    import torch
    from custom_metrics import loss_metrics

    # Prepare Metrics to call
    metrics_dict = {
        "acc": MulticlassAccuracy(num_classes=3),
        "f1": MulticlassF1Score(num_classes=3),
        "loss": loss_metrics,
        "empty_metrics": loss_metrics,  # For example if we didnt compute on this metrics
    }

    # Prepare callback
    def callbacks_example(name: MetricsName, metrics_val: Tensor):
        print(
            "Hello from a callback",
            name,
            "with a value of",
            metrics_val,
            "\nThis will run every insert_metric or __call__ invoked",
        )

    metrics = MetricsContainer(metrics_fn=metrics_dict, callbacks=[callbacks_example])

    # New batch
    metrics.new_batch()

    # Dummy tensor
    target_1 = torch.tensor([2, 1, 0, 0])
    preds_1 = torch.tensor([2, 1, 0, 1])
    target_2 = torch.tensor([0, 1, 2])
    preds_2 = torch.tensor([0, 1, 2])
    loss = torch.tensor(1.32323, dtype=torch.float64)
    loss_2 = torch.tensor(100, dtype=torch.float64)

    # Add metric by calling insert_metric
    metrics.compute_metric("acc", preds_1, target_1)
    # Add metric by calling the class
    metrics("f1", preds_1, target_1)
    metrics("loss", loss)

    # Process batch
    metrics.process_batch()
    print("batch 1 latest metrics on a batch", metrics.latest_metrics_batch())
    print("batch 1 mean metrics on a batch", metrics.mean_metrics_batch())
    print("batch 1 latest history", metrics.latest_metrics_history())

    # New batch
    metrics.new_batch()

    # Add metric by calling insert_metric
    metrics.compute_metric("acc", preds_2, target_2)
    # Add metric by calling the class
    metrics("f1", preds_2, target_2)
    metrics("loss", loss_2)

    metrics.process_batch()
    print("batch 2 latest metrics on a batch", metrics.latest_metrics_batch())
    print("batch 2 mean metrics on a batch", metrics.mean_metrics_batch())
    print("batch 2 latest history", metrics.latest_metrics_history())
