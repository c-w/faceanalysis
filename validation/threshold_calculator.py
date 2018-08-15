from typing import Callable, List, Union, cast
import numpy as np
from sklearn.metrics import (accuracy_score,
                             f1_score,
                             precision_score,
                             recall_score)
from calculator import Calculator
from distance_calculator import DistanceCalculator
from metrics import DistanceMetric, ThresholdMetric, ThresholdMetricException
from pair import Pair


class ThresholdCalculator(Calculator):

    def __init__(self,
                 distance_metric: Union[str, DistanceMetric],
                 threshold_metric: Union[str, ThresholdMetric],
                 threshold_start: float,
                 threshold_end: float,
                 threshold_step: float) -> None:
        if type(threshold_metric) == str:
            self._threshold_metric = getattr(ThresholdMetric,
                                             cast(str, threshold_metric))
        else:
            self._threshold_metric = threshold_metric
        if type(distance_metric) == str:
            self._distance_metric = getattr(DistanceMetric,
                                            cast(str, distance_metric))
        else:
            self._distance_metric = distance_metric
        self._threshold_start = threshold_start
        self._threshold_end = threshold_end
        self._threshold_step = threshold_step

    def calculate(self, pairs: List[Pair]) -> float:
        threshold_scorer = self._get_threshold_scorer()
        dist = DistanceCalculator(self._distance_metric).calculate(pairs)
        labels = [pair.is_match for pair in pairs]
        best_score = float('-inf')
        best_threshold_index = 0
        thresholds = np.arange(self._threshold_start,
                               self._threshold_end,
                               self._threshold_step)
        for i, threshold in enumerate(thresholds):
            predictions = np.less(dist, threshold)
            score = threshold_scorer(labels, predictions)
            if score > best_score:
                best_score = score
                best_threshold_index = i
        return thresholds[best_threshold_index]

    def _get_threshold_scorer(
            self) -> Callable[[np.ndarray, np.ndarray], float]:
        if self._threshold_metric == ThresholdMetric.ACCURACY:
            return accuracy_score
        elif self._threshold_metric == ThresholdMetric.PRECISION:
            return precision_score
        elif self._threshold_metric == ThresholdMetric.RECALL:
            return recall_score
        elif self._threshold_metric == ThresholdMetric.F1:
            return f1_score
        else:
            metrics = [f'{ThresholdMetric.__qualname__}.{attr}'
                       for attr in dir(ThresholdMetric)
                       if not callable(getattr(ThresholdMetric, attr))
                       and not attr.startswith("__")]
            err = f"Undefined {ThresholdMetric.__qualname__}. \
Choose from {metrics}"
            raise ThresholdMetricException(err)
