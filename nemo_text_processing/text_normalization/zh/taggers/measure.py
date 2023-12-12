# Copyright (c) 2022, NVIDIA CORPORATION & AFFILIATES.  All rights reserved.
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
from nemo_text_processing.text_normalization.zh.graph_utils import NEMO_NOT_QUOTE, GraphFst, delete_space, insert_space
from nemo_text_processing.text_normalization.zh.utils import get_abs_path
from pynini.lib import pynutil


class MeasureFst(GraphFst):
    '''
        1kg  -> tokens { measure { cardinal { integer: "一" } units: "千克" } }
    '''

    def __init__(
        self, cardinal: GraphFst, decimal: GraphFst, fraction: GraphFst, deterministic: bool = True, lm: bool = False
    ):
        super().__init__(name="measure", kind="classify", deterministic=deterministic)

        units_en = pynini.string_file(get_abs_path("data/measure/units_en.tsv"))
        units_zh = pynini.string_file(get_abs_path("data/measure/units_zh.tsv"))
        score_sign = pynini.string_file(get_abs_path("data/math/score.tsv")) | pynini.string_file(
            get_abs_path("data/math/symbol.tsv")
        )

        graph_cardinal = cardinal.with_sign
        graph_decimal = decimal.decimal
        graph_fraction = fraction.fractions

        graph_just_cardinal = cardinal.just_cardinals
        graph_just_decimal = decimal.regular_decimal
        graph_just_fraction = fraction.just_fractions

        # these units ared added due to falures when running Sparrow Hawk tests that "ms" would be processed as "m" and "s" left outside of the tagegr
        units = (
            pynini.cross("ms", "毫秒")
            | pynini.cross("m²", "平方米")
            | pynini.cross("m2", "平方米")
            | pynini.cross("m²", "平方米")
            | pynini.cross("m³", "立方米")
            | pynini.cross("mbps", "兆比特每秒")
            | pynini.cross("mg", "毫克")
            | pynini.cross("mhz", "兆赫兹")
            | pynini.cross("mi2", "平方英里")
            | pynini.cross("mi²", "平方英里")
            | pynini.cross("mi", "英里")
            | pynini.cross("min", "分钟")
            | pynini.cross("ml", "毫升")
            | pynini.cross("mm2", "平方毫米")
            | pynini.cross("mm²", "平方毫米")
            | pynini.cross("mol", "摩尔")
            | pynini.cross("mpa", "兆帕")
            | pynini.cross("mph", "英里每小时")
            | pynini.cross("mm", "毫米")
            | pynini.cross("mv", "毫伏")
            | pynini.cross("mw", "毫瓦")
        )

        unit_component = pynutil.insert("units: \"") + (units_en | units_zh | units) + pynutil.insert("\"")

        unit_component_math = pynutil.insert("units: \"") + score_sign + pynutil.insert("\"")

        graph_cardinal_measure = pynini.closure(
            (pynutil.insert("cardinal { ") + graph_cardinal + pynutil.insert(" } ") + insert_space + unit_component), 1
        )

        graph_decimal_measure = pynini.closure(
            (pynutil.insert("decimal { ") + graph_decimal + pynutil.insert(" } ") + unit_component), 1
        )

        graph_fraction_measure = pynini.closure(
            (pynutil.insert("fraction { ") + graph_fraction + pynutil.insert(" } ") + insert_space + unit_component), 1
        )

        graph_math_cardinal = (
            graph_just_cardinal
            + pynini.closure(score_sign + graph_just_cardinal, 1)
            + pynini.cross("=", "等于")
            + graph_just_cardinal
        )

        graph_math_cardinal = pynutil.insert("cardinal { integer: \"") + graph_math_cardinal + pynutil.insert("\" } ")

        graph_maths = graph_math_cardinal
        graph_measures = graph_decimal_measure | graph_cardinal_measure | graph_fraction_measure

        final_graph = graph_measures | graph_maths

        final_graph = self.add_tokens(final_graph)
        self.fst = final_graph.optimize()

        # import pdb; pdb.set_trace()
