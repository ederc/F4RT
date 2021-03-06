/**
 * \file   mat-mult-kaapi.cpp
 * \author Christian Eder ( christian.eder@inria.fr )
 * \date   March 2013
 * \brief  Source file for dense matrix multiplication using KAAPI.
 *         This file is part of F4RT, licensed under the GNU General
 *         Public License version 3. See COPYING for more information.
 */

#include "mat-mult-kaapi.h"

#define __F4RT_DEBUG  0

#if defined(__F4RT_HAVE_KAAPIC)
/*******************************
 * KAAPIC implementation
 ******************************/
static void multMat2dInnerImpose(
    size_t start, size_t end, int32_t tid, 
    uint32 i, uint32 n, uint32 m,
    mat* c_entries, const mat* a_entries, const mat* b_entries) {
  for (size_t j = start; j < end; ++j) {
    mat sum = 0;
    for (size_t k = 0; k < n; ++k) {
      sum += a_entries[k+i*n] * b_entries[k+j*n];
    }
    //std::cout << j+i*m << ". " << sum << std::endl;
    c_entries[j+i*m]  = sum;
  }
}

static void multMat2dOuterImpose(
    size_t start, size_t end, int32_t tid, 
    uint32 m, uint32 n, 
    mat* c_entries, const mat* a_entries, const mat* b_entries) {
  for (size_t i = start; i < end; ++i) {
    kaapic_foreach_attr_t attr;
    kaapic_foreach_attr_init(&attr);
    kaapic_foreach( 0, m, &attr, 6, multMat2dInnerImpose, i, n,
                    m, c_entries, a_entries, b_entries);
  }
}

static void multMat2dInner(
    size_t start, size_t end, int32_t tid, 
    uint32 i, uint32 n, 
    mat* c_entries, const mat* a_entries, const mat* b_entries) {
  for (size_t j = start; j < end; ++j) {
    mat sum = 0;
    for (size_t k = 0; k < n; ++n) {
      sum += a_entries[k+i*n] * b_entries[j+k*(end+1)];
    }
    c_entries[j+i*(end+1)]  = sum;
  }
}

static void multMat2dOuter(
    size_t start, size_t end, int32_t tid, 
    uint32 m, uint32 n, 
    mat* c_entries, const mat* a_entries, const mat* b_entries) {
  for (size_t i = start; i < end; ++i) {
    kaapic_foreach_attr_t attr;
    kaapic_foreach_attr_init(&attr);
    kaapic_foreach(0, m, &attr, 5, multMat2dInner, i, n, c_entries, a_entries, b_entries);
  }
}

static void multMat1dImpose(
    size_t start, size_t end, int32_t tid, 
    uint32 m, uint32 n, 
    mat* c_entries, const mat* a_entries, const mat* b_entries) {
  for (size_t i = start; i < end; ++i) {
    for (size_t j = 0; j < m; ++j) {
      float sum = 0;
      for (size_t k = 0; k < n; k++) {
        sum += a_entries[k+i*n] * b_entries[k+j*n];
      }
      //std::cout << j+i*m << "." << sum << "LL" << std::endl;
      c_entries[j+i*m]  = (float) (sum);
    }
  }
}

static void multMat1d(
    size_t start, size_t end, int32_t tid, 
    uint32 m, uint32 n, 
    mat* c_entries, const mat* a_entries, const mat* b_entries) {
  for (size_t i = start; i < end; ++i) {
    for (size_t j = 0; j < m; ++j) {
      mat sum = 0;
      for (size_t k = 0; k < n; k++) {
        sum += a_entries[k+i*n] * b_entries[j+k*m];
      }
      //std::cout << j+i*m << "." << sum << "LL" << std::endl;
      c_entries[j+i*m]  = (float) (sum);
    }
  }
}


/********************************
 * 1 Dimensional implementation
 *******************************/

void multKAAPIC1d(Matrix& C, const Matrix& A, const Matrix& B, int nthrds, uint32 blocksize, int impose) {
  uint32 l, m, n;
  int thrdCounter = nthrds;
  if (impose == 1) {
    l = A.nRows();
    m = B.nRows();
    n = B.nCols();
  } else {
    l = A.nRows();
    m = B.nCols();
    n = B.nRows();
  }

  const mat *a_entries = new mat[l*n];
  a_entries = A.entries.data();
  
  const mat *b_entries = new mat[n*m];
  b_entries = B.entries.data();

  mat *c_entries = new mat[l*m];
  //C.resize(l*m);
  std::cout << "Matrix Multiplication" << std::endl;
  timeval start, stop;
  clock_t cStart, cStop;
#if __F4RT_DEBUG
  std::cout << std::endl;
  std::cout << "A => " << A.nRows() << "-" << A.nCols() << "-" << A.nEntries() << std::endl;
  std::cout << "B => " << A.nRows() << "-" << A.nCols() << "-" << A.nEntries() << std::endl;
  std::cout << "C => " << C.nRows() << "-" << C.nCols() << "-" << C.nEntries() << std::endl;
#endif
  // only start main kaapi thread, others are initialized first when parallel
  // region starts
  kaapic_foreach_attr_t attr;
  kaapic_init(1);
  kaapic_foreach_attr_init(&attr);
  kaapic_foreach_attr_set_grains(&attr, blocksize, blocksize);
  gettimeofday(&start, NULL);
  cStart  = clock();
  if (nthrds > 0)
    omp_set_num_threads(nthrds);
if (impose == 1) {
  kaapic_foreach(0, l, &attr, 5, multMat1dImpose, m, n, c_entries, a_entries, b_entries);
} else {
  kaapic_foreach(0, l, &attr, 5, multMat1d, m, n, c_entries, a_entries, b_entries);
}
  gettimeofday(&stop, NULL);
  cStop = clock();

  // finalizes kaapic interface
  kaapic_finalize();
  std::cout << "---------------------------------------------------" << std::endl;
  std::cout << "Method:           KAAPIC 1D" << std::endl;
  std::cout << "Cache improved:   ";
  if (impose == 1)
    std::cout << "1" << std::endl;
  else
    std::cout << "0" << std::endl;
  // compute FLOPS:
  // assume addition and multiplication in the mult kernel are 2 operations
  // done A.nRows() * B.nRows() * B.nCols()
  double flops = 2 * A.nRows() * B.nRows() * B.nCols();
  float epsilon = 0.0000000001;
  double realtime = ((stop.tv_sec - start.tv_sec) * 1e6 + 
                    (stop.tv_usec - start.tv_usec)) / 1e6;
  double cputime  = (double)((cStop - cStart)) / CLOCKS_PER_SEC;
  char buffer[50];
  // get digits before decimal point of cputime (the longest number) and setw
  // with it: digits + 1 (point) + 4 (precision) 
  int digits = sprintf(buffer,"%.0f",cputime);
  double ratio = cputime/realtime;
  std::cout << "# Threads:        " << thrdCounter << std::endl;
  std::cout << "Block size:       " << blocksize << std::endl;
  std::cout << "- - - - - - - - - - - - - - - - - - - - - - - - - -" << std::endl;
  std::cout << "Real time:        " << std::setw(digits+1+4) 
    << std::setprecision(4) << std::fixed << realtime << " sec" 
    << std::endl;
  std::cout << "CPU time:         " << std::setw(digits+1+4) 
    << std::setprecision(4) << std::fixed << cputime
    << " sec" << std::endl;
  if (cputime > epsilon)
    std::cout << "CPU/real time:    " << std::setw(digits+1+4) 
      << std::setprecision(4) << std::fixed << ratio << std::endl;
  std::cout << "- - - - - - - - - - - - - - - - - - - - - - - - - -" << std::endl;
  std::cout << "GFLOPS/sec:       " << std::setw(digits+1+4) 
    << std::setprecision(4) << std::fixed << flops / (1000000000 * realtime) 
    << std:: endl;
  std::cout << "---------------------------------------------------" << std::endl;
}


/********************************
 * 2 Dimensional implementation
 *******************************/

void multKAAPIC2d(Matrix& C, const Matrix& A, const Matrix& B, int nthrds, uint32 blocksize, int impose) {
  uint32 l, m, n;
  int thrdCounter = nthrds;
  if (impose == 1) {
    l = A.nRows();
    m = B.nRows();
    n = B.nCols();
  } else {
    l = A.nRows();
    m = B.nCols();
    n = B.nRows();
  }

  const mat *a_entries = new mat[l*n];
  a_entries = A.entries.data();
  
  const mat *b_entries = new mat[n*m];
  b_entries = B.entries.data();

  mat *c_entries = new mat[l*m];
  //C.resize(l*m);
  std::cout << "Matrix Multiplication" << std::endl;
  timeval start, stop;
  clock_t cStart, cStop;
#if __F4RT_DEBUG
  std::cout << std::endl;
  std::cout << "A => " << A.nRows() << "-" << A.nCols() << "-" << A.nEntries() << std::endl;
  std::cout << "B => " << A.nRows() << "-" << A.nCols() << "-" << A.nEntries() << std::endl;
  std::cout << "C => " << C.nRows() << "-" << C.nCols() << "-" << C.nEntries() << std::endl;
#endif
  // only start main kaapi thread, others are initialized first when parallel
  // region starts
  kaapic_foreach_attr_t attr;
  kaapic_init(1);
  kaapic_foreach_attr_init(&attr);
  kaapic_foreach_attr_set_grains(&attr, blocksize, blocksize);
  gettimeofday(&start, NULL);
  cStart  = clock();
  if (nthrds > 0)
    omp_set_num_threads(nthrds);
if (impose == 1) {
  kaapic_foreach(0, l, &attr, 5, multMat2dOuterImpose, m, n, c_entries, a_entries, b_entries);
} else {
  kaapic_foreach(0, l, &attr, 5, multMat2dOuter, m, n, c_entries, a_entries, b_entries);
}
  gettimeofday(&stop, NULL);
  cStop = clock();

  // finalizes kaapic interface
  kaapic_finalize();
  std::cout << "---------------------------------------------------" << std::endl;
  std::cout << "Method:           KAAPIC 2D" << std::endl;
  std::cout << "Cache improved:   ";
  if (impose == 1)
    std::cout << "1" << std::endl;
  else
    std::cout << "0" << std::endl;
  // compute FLOPS:
  // assume addition and multiplication in the mult kernel are 2 operations
  // done A.nRows() * B.nRows() * B.nCols()
  double flops = 2 * A.nRows() * B.nRows() * B.nCols();
  float epsilon = 0.0000000001;
  double realtime = ((stop.tv_sec - start.tv_sec) * 1e6 + 
                    (stop.tv_usec - start.tv_usec)) / 1e6;
  double cputime  = (double)((cStop - cStart)) / CLOCKS_PER_SEC;
  char buffer[50];
  // get digits before decimal point of cputime (the longest number) and setw
  // with it: digits + 1 (point) + 4 (precision) 
  int digits = sprintf(buffer,"%.0f",cputime);
  double ratio = cputime/realtime;
  std::cout << "# Threads:        " << thrdCounter << std::endl;
  std::cout << "Block size:       " << blocksize << std::endl;
  std::cout << "- - - - - - - - - - - - - - - - - - - - - - - - - -" << std::endl;
  std::cout << "Real time:        " << std::setw(digits+1+4) 
    << std::setprecision(4) << std::fixed << realtime << " sec" 
    << std::endl;
  std::cout << "CPU time:         " << std::setw(digits+1+4) 
    << std::setprecision(4) << std::fixed << cputime
    << " sec" << std::endl;
  if (cputime > epsilon)
    std::cout << "CPU/real time:    " << std::setw(digits+1+4) 
      << std::setprecision(4) << std::fixed << ratio << std::endl;
  std::cout << "- - - - - - - - - - - - - - - - - - - - - - - - - -" << std::endl;
  std::cout << "GFLOPS/sec:       " << std::setw(digits+1+4) 
    << std::setprecision(4) << std::fixed << flops / (1000000000 * realtime) 
    << std:: endl;
  std::cout << "---------------------------------------------------" << std::endl;
}

#endif
