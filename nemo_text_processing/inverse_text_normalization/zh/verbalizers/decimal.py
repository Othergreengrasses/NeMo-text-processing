# Copyright (c) 2023, NVIDIA CORPORATION & AFFILIATES.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pynini
from pynini.lib import pynutil

from nemo_text_processing.inverse_text_normalization.zh.graph_utils import (
    NEMO_DIGIT,
    NEMO_NOT_QUOTE,
    GraphFst,
    delete_space,
)


class DecimalFst(GraphFst):
    def __init__(self):
        super().__init__(name="decimal", kind="verbalize")

        # group numbers by three
        exactly_three_digits = NEMO_DIGIT ** 3
        at_most_three_digits = pynini.closure(NEMO_DIGIT, 1, 3)

        # insert a "," for every three numbers before decimal point
        space_every_three_integer = at_most_three_digits + (pynutil.insert(",") + exactly_three_digits).closure()
<<<<<<< HEAD
        # insert a "," for every three numbers after decimal point
        space_every_three_decimal = (
            pynini.accep(".") + (exactly_three_digits + pynutil.insert(",")).closure() + at_most_three_digits
        )

        # combine both
        group_by_threes = space_every_three_integer | space_every_three_decimal
        self.group_by_threes = group_by_threes
=======
>>>>>>> 42c0071bbeb3141ba013d3965693bb100c06a8e6

        # removing tokenizations, 'negative: '
        optional_sign = pynini.closure(
            pynutil.delete("negative: ")
            + delete_space
            + pynutil.delete('"')
            + pynini.accep("-")
            + pynutil.delete('"')
            + delete_space
        )

        # removing tokenzations, 'integer_part:'
        integer = (
            pynutil.delete("integer_part:")
            + delete_space
            + pynutil.delete('"')
<<<<<<< HEAD
            + pynini.closure(NEMO_NOT_QUOTE, 1)
            + pynutil.delete('"')
        )
        integer = integer @ group_by_threes
=======
            + pynini.closure(NEMO_DIGIT, 1)
            + pynutil.delete('"')
        )
        integer = integer @ space_every_three_integer
>>>>>>> 42c0071bbeb3141ba013d3965693bb100c06a8e6
        optional_integer = pynini.closure(integer + delete_space, 0, 1)

        # removing tokenizations, 'fractionl_part'
        fractional = (
            pynutil.insert(".")
            + pynutil.delete("fractional_part:")
            + delete_space
            + pynutil.delete('"')
            + pynini.closure(NEMO_NOT_QUOTE, 1)
            + pynutil.delete('"')
        )
        optional_fractional = pynini.closure(fractional + delete_space, 0, 1)

        # removing tokenization, 'quantity:'
        quantity = (
            pynutil.delete("quantity:")
            + delete_space
            + pynutil.delete('"')
            + pynini.closure(NEMO_NOT_QUOTE, 1)
            + pynutil.delete('"')
        )
<<<<<<< HEAD
        optional_quantity = pynini.closure(quantity + delete_space)

        # combining graphs removing tokenizations *3
        graph = (optional_integer + optional_fractional + optional_quantity).optimize()
=======
        optional_quantity = pynini.closure(delete_space + quantity)

        # combining graphs removing tokenizations *3
        graph = (optional_integer + optional_fractional + optional_quantity).optimize()

>>>>>>> 42c0071bbeb3141ba013d3965693bb100c06a8e6
        graph = optional_sign + graph  # add optional sign for negative number
        self.numebrs = graph
        delete_tokens = self.delete_tokens(graph)
        self.fst = delete_tokens.optimize()
