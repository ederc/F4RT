/**
 * \file   mat-elim-pthrd.h
 * \author Christian Eder ( christian.eder@inria.fr )
 * \date   April 2013
 * \brief  Header file for Gaussian Elimination using pThread.
 *         This file is part of F4RT, licensed under the GNU General
 *         Public License version 3. See COPYING for more information.
 */

#ifndef F4RT_MAT_ELIM_PTHRD_H
#define F4RT_MAT_ELIM_PTHRD_H

#include <matrix.h>
#include "../mat-elim-tools.h"

#ifdef __F4RT_HAVE_PTHREAD_H

struct paramsElim {
  mat *a;
  int size;
  mat inv;
  uint64 prime;
  uint32 index;
  uint32 start;
  uint32 m;
  uint32 n;
  int tid;
};

struct paramsCoElim {
  mat *M;
  mat* neg_inv_piv;
  uint64 size;
  uint64 prime;
  uint32 rows;
  uint32 cols;
  uint32 blocksize;
  uint32 i1;
  uint32 i2;
  uint32 j1;
  uint32 j2;
  uint32 k1;
  uint32 k2;
  int nthrds;
};


void elimPTHRD(Matrix& A, uint32 blocksize);

void elimNaivePTHRDModP1d(Matrix& A, int nthrds, uint32 blocksize, uint64 prime);

void elimNaivePTHRDModP1dPivot(Matrix& A, int nthrds, uint32 blocksize, uint64 prime);
//
// cache-oblivious stuff

void elimCoPTHRDBaseModP( mat *M, const uint32 k1, const uint32 i1,
                        const uint32 j1, const uint32 rows, const uint32 cols,
                        uint64 size, uint64 prime, mat *neg_inv_piv,
                        int nthrds, uint32 blocksize);

void APTHRD( mat *M, const uint32 k1, const uint32 k2,
        const uint32 i1, const uint32 i2,
		    const uint32 j1, const uint32 j2,
		    const uint32 rows, const uint32 cols,
        uint64 size, uint64 prime, mat *neg_inv_piv,
        int nthrds, uint32 blocksize);

void B1PTHRD(mat *M, const uint32 k1, const uint32 k2,
        const uint32 i1, const uint32 i2,
		    const uint32 j1, const uint32 j2,
		    const uint32 rows, const uint32 cols,
        uint64 size, uint64 prime, mat *neg_inv_piv,
        int nthrds, uint32 blocksize);

void C1PTHRD(mat *M, const uint32 k1, const uint32 k2,
        const uint32 i1, const uint32 i2,
		    const uint32 j1, const uint32 j2,
		    const uint32 rows, const uint32 cols,
        uint64 size, uint64 prime, mat *neg_inv_piv,
        int nthrds, uint32 blocksize);

void* D1PTHRD(void *p);

void elimCoPTHRDModP(Matrix& M, int nthrds, uint32 blocksize, uint64 prime);

#endif
#endif
