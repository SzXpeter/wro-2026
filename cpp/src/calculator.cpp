#include "calculator.h"

double calc_add(double a, double b) { return a + b; }
double calc_sub(double a, double b) { return a - b; }
double calc_mul(double a, double b) { return a * b; }
double calc_div(double a, double b) { return b != 0.0 ? a / b : 0.0; }
