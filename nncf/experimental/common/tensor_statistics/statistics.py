# Copyright (c) 2024 Intel Corporation
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import pickle
from collections import Counter
from dataclasses import dataclass
from typing import ClassVar, Dict, Tuple

import numpy as np

from nncf.tensor import Tensor
from nncf.tensor import functions as fns


class TensorStatistic:
    """Base class that stores statistic data"""

    TENSOR_STATISTIC_OUTPUT_KEY = "tensor_statistic_output"


@dataclass
class MinMaxTensorStatistic(TensorStatistic):
    MIN_STAT: ClassVar[str] = "min_values"
    MAX_STAT: ClassVar[str] = "max_values"

    min_values: Tensor
    max_values: Tensor

    def __eq__(self, other: TensorStatistic):
        if isinstance(other, MinMaxTensorStatistic):
            return fns.allclose(self.min_values, other.min_values) and fns.allclose(self.max_values, other.max_values)
        return False

    def get_statistic_info(self, target_node_info):
        return {"type": "MinMaxTensorStatistic", "target_node_info": target_node_info}

    def get_dumped_data(self, target_node_info):
        return {
            "type": "MinMaxTensorStatistic",
            "target_node_info": target_node_info,
            "min_values": np.array(self.min_values.data),
            "max_values": np.array(self.max_values.data),
        }

    def load_dumped_data(self, data):
        self.load_data(data["min_values"], data["max_values"])

    def load_data(self, min_values, max_values):
        self.min_values = Tensor(min_values)
        self.max_values = Tensor(max_values)

    def dump(self, stat_filename, target_node_info):
        data = {
            "type": "MinMaxTensorStatistic",
            "target_node_info": target_node_info,
            "min_values": np.array(self.min_values.data),
            "max_values": np.array(self.max_values.data),
        }
        with open(stat_filename, "wb") as f:
            pickle.dump(data, f)
        # np.savez(stat_filename, min_values=np.array(self.min_values.data), max_values=np.array(self.max_values.data))


@dataclass
class MeanTensorStatistic(TensorStatistic):
    MEAN_STAT: ClassVar[str] = "mean_values"
    SHAPE_STAT: ClassVar[str] = "shape"

    mean_values: Tensor
    shape: Tuple[int, ...]

    def __eq__(self, other: TensorStatistic):
        if isinstance(other, MeanTensorStatistic):
            return self.shape == other.shape and fns.allclose(self.mean_values, other.mean_values)
        return False

    def get_dumped_data(self, target_node_info):
        return {
            "type": "MinMaxTensorStatistic",
            "target_node_info": target_node_info,
            "mean_values": np.array(self.mean_values.data),
            "shape": np.array(self.shape),
        }

    def get_statistic_info(self, target_node_info):
        return {"type": "MinMaxTensorStatistic", "target_node_info": target_node_info}

    def load_dumped_data(self, data):
        self.load_data(data["mean_values"], data["shape"])

    def load_data(self, mean_values, shape):
        self.mean_values = Tensor(mean_values)
        self.shape = tuple(shape)

    def dump(self, stat_filename, target_node_info):
        data = {
            "type": "MinMaxTensorStatistic",
            "target_node_info": target_node_info,
            "mean_values": np.array(self.mean_values.data),
            "shape": np.array(self.shape),
        }
        with open(stat_filename, "wb") as f:
            pickle.dump(data, f)


@dataclass
class MedianMADTensorStatistic(TensorStatistic):
    MEDIAN_VALUES_STAT: ClassVar[str] = "median_values"
    MAD_VALUES_STAT: ClassVar[str] = "mad_values"

    median_values: Tensor
    mad_values: Tensor

    def __eq__(self, other: TensorStatistic):
        if isinstance(other, MedianMADTensorStatistic):
            return fns.allclose(self.median_values, other.median_values) and fns.allclose(
                self.mad_values, other.mad_values
            )
        return False


@dataclass
class PercentileTensorStatistic(TensorStatistic):
    PERCENTILE_VS_VALUE_DICT: ClassVar[str] = "percentile_vs_values_dict"

    percentile_vs_values_dict: Dict[str, Tensor]

    def __eq__(self, other: TensorStatistic):
        if isinstance(other, PercentileTensorStatistic):
            if Counter(self.percentile_vs_values_dict.keys()) != Counter(other.percentile_vs_values_dict.keys()):
                return False
            for pct in self.percentile_vs_values_dict:
                if not fns.allclose(self.percentile_vs_values_dict[pct], other.percentile_vs_values_dict[pct]):
                    return False
            return True
        return False


@dataclass
class RawTensorStatistic(TensorStatistic):
    VALUES_STATS: ClassVar[str] = "values"

    values: Tensor

    def __eq__(self, other: RawTensorStatistic) -> bool:
        if isinstance(other, PercentileTensorStatistic):
            return fns.allclose(self.values, other.values)
        return False
