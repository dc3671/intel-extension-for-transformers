//  Copyright (c) 2021 Intel Corporation
//
//  Licensed under the Apache License, Version 2.0 (the "License");
//  you may not use this file except in compliance with the License.
//  You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
//  Unless required by applicable law or agreed to in writing, software
//  distributed under the License is distributed on an "AS IS" BASIS,
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  See the License for the specific language governing permissions and
//  limitations under the License.

#ifndef ENGINE_SPARSELIB_INCLUDE_UTILS_HPP_
#define ENGINE_SPARSELIB_INCLUDE_UTILS_HPP_
#include <stdlib.h>

#include <algorithm>
#include <chrono>  // NOLINT
#include <limits>
#include <random>
#include <sstream>
#include <string>
#include <vector>
#include "param_types.hpp"

#ifdef SPARSE_LIB_USE_VTUNE
#include <ittnotify.h>
#endif

namespace jd {

typedef unsigned short bfloat16_t;  // NOLINT
typedef int64_t dim_t;

template <typename T>
T cast_to(float x);

template <>
bfloat16_t cast_to(float x);

float make_fp32(bfloat16_t x);

bfloat16_t make_bf16(float x);

template <typename T>
void init_vector(T* v, int num_size, float bound1 = -10, float bound2 = 10, int seed = 5489u);

template <typename T>
bool compare_data(const void* buf1, int64_t size1, const void* buf2, int64_t size2, T eps = static_cast<T>(1e-6));

float time(const std::string& state);

template <typename value_type, typename predicate_type>
inline bool is_any_of(std::initializer_list<value_type> il, predicate_type pred) {
  return std::any_of(il.begin(), il.end(), pred);
}

#define ceil_div(x, y) (((x) + (y)-1) / (y))

#define is_nonzero(x) (fabs((x)) > (1e-3))

template <typename T>
T str_to_num(const std::string& s);

template <typename T>
std::vector<T> split_str(const std::string& s, const char& delim = ',');

std::string join_str(const std::vector<std::string>& ss, const std::string& delim = ",");

bool init_amx();

/**
 * @brief Check if every element in a sub matrix is zero
 *
 * @tparam T Element type of the matrix data
 * @param data pointer to the start element of th sub matrix to check
 * @param ld leading dim of the data
 * @param nd1 size in the major dimension
 * @param nd2 size in another dimension
 */
template <typename T>
bool all_zeros(const T* data, dim_t ld, dim_t nd1, dim_t nd2);

int get_data_size(data_type dt);

float get_exp(float x);
float get_linear(float x);
float get_gelu(float x);
float get_relu(float x, float alpha);
int get_quantize(float x, float alpha, float scale);
float get_dequantize(float x, float alpha, float scale);
float apply_postop_list(float value, const std::vector<jd::postop_attr>& attrs);

}  // namespace jd
#endif  // ENGINE_SPARSELIB_INCLUDE_UTILS_HPP_
