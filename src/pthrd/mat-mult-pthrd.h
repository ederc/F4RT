/**
 * \file   mat-mul-pthrd.h
 * \author Christian Eder ( christian.eder@inria.fr )
 * \date   March 2013
 * \brief  Header file for dense matrix multiplication using pthread.
 *         This file is part of F4RT, licensed under the GNU General
 *         Public License version 3. See COPYING for more information.
 */

#ifndef F4RT_MAT_MULT_PTHRD_H
#define F4RT_MAT_MULT_PTHRD_H

#include <matrix.h>

struct params {
  const float *a;
  const float *b;
  float *c;
  int size;
  uint32 m;
  uint32 n;
  int tid;
};

void *multPThreadImpose(void *p);

void *multPThread(void *p);

// multiplies A*B^T and stores it in C
void multPT(Matrix& C, const Matrix& A, const Matrix& B, int nthrds,
            int blocksize, int impose);

#endif