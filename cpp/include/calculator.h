#pragma once

#ifdef __cplusplus
extern "C" {
#endif

double calc_add(double a, double b);
double calc_sub(double a, double b);
double calc_mul(double a, double b);
double calc_div(double a, double b);  // 0-val való osztásnál 0.0-t ad vissza

#ifdef __cplusplus
}
#endif
