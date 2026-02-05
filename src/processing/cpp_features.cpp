#include <numeric>
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <vector>

namespace py = pybind11;

/**
 * Compute the rolling average of a 1D double array.
 */
py::array_t<double> rolling_mean_cpp(py::array_t<double> input, int window) {
  auto buf = input.request();
  double *ptr = (double *)buf.ptr;
  int size = buf.size;

  std::vector<double> result(size, std::numeric_limits<double>::quiet_NaN());

  if (window <= 0 || window > size) {
    return py::cast(result);
  }

  double current_sum = 0;
  for (int i = 0; i < size; ++i) {
    current_sum += ptr[i];
    if (i >= window) {
      current_sum -= ptr[i - window];
    }
    if (i >= window - 1) {
      result[i] = current_sum / window;
    }
  }

  return py::cast(result);
}

PYBIND11_MODULE(cpp_features, m) {
  m.doc() = "High-performance features implemented in C++";
  m.def("rolling_mean", &rolling_mean_cpp, "Compute rolling mean",
        py::arg("input"), py::arg("window"));
}
