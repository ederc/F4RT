# Copyright 2012 Christian Eder
# 
# This file is part of F4RT, licensed under the GNU General Public
# License version 3. See COPYING for more information.

AUTOMAKE_OPTIONS = subdir-objects

INCLUDES=-I$(top_srcdir) -I$(top_srcdir)/include -I$(top_builddir)

#AM_CXXFLAGS = -g -Wall -DDEBUG -O0 -fomit-frame-pointer


SUBDIRS=

BASIC_HDRS =											\
	../include/la-bencher-config.h 	\
	intrinsics.h										\
	matrix.h												\
	mat-mult.h											\
	kaapi/mat-mult-kaapi.h					\
	omp/mat-mult-omp.h							\
	pthrd/mat-mult-pthrd.h					\
	seq/mat-mult-seq.h							\
	tbb/mat-mult-tbb.h							\
	mat-elim.h											\
	mat-elim-tools.h								\
	blas/mat-elim-blas.h						\
	kaapi/mat-elim-kaapi.h					\
	omp/mat-elim-omp.h							\
	pthrd/mat-elim-pthrd.h					\
	seq/mat-elim-seq.h							\
	tbb/mat-elim-tbb.h							\
	mat-gen.h

SOURCES=										\
	intrinsics.c							\
	la-bencher.cpp						\
	matrix.cpp								\
	mat-mult.cpp							\
	kaapi/mat-mult-kaapi.cpp	\
	omp/mat-mult-omp.cpp			\
	pthrd/mat-mult-pthrd.cpp	\
	seq/mat-mult-seq.cpp			\
	tbb/mat-mult-tbb.cpp			\
	mat-elim.cpp							\
	mat-elim-tools.c					\
	blas/mat-elim-blas.c			\
	kaapi/mat-elim-kaapi.c		\
	omp/mat-elim-omp.cpp			\
	pthrd/mat-elim-pthrd.cpp	\
	seq/mat-elim-seq.cpp			\
	tbb/mat-elim-tbb.cpp			\
	mat-gen.cpp

pkginclude_HEADERS =	\
	$(BASIC_HDRS)

libla_bencher_la_CPPFLAGS	= $(AM_CXXFLAGS) -D__F4RT_NDEBUG -DNDEBUG $(INCLUDES)
libla_bencher_la_CXXFLAGS	= $(AM_CXXFLAGS) -std=gnu++0x -Wall -D__F4RT_NDEBUG -DNDEBUG $(INCLUDES)
libla_bencher_la_CFLAGS	= $(AM_CFLAGS) -std=gnu99 -Wall -D__F4RT_NDEBUG -DNDEBUG $(INCLUDES)

libla_bencher_la_SOURCES	=	\
	$(SOURCES)

libla_bencher_la_LIBADD=
if ENABLE_DEBUG
lib_LTLIBRARIES	=	libla-bencher.la libla-bencher_debug.la
libla_bencher_debug_la_CPPFLAGS	=	$(AM_CXXFLAGS) -g3 -ggdb -Wall -D__F4RT_DEBUG -DDEBUG $(INCLUDES)
libla_bencher_debug_la_CXXFLAGS	=	$(AM_CXXFLAGS) -g3 -ggdb -Wall -std=gnu++0x -D__F4RT_DEBUG -DDEBUG $(INCLUDES)
libla_bencher__debug_la_CFLAGS	= $(AM_CFLAGS) -std=gnu99 -Wall -D__F4RT_NDEBUG -DNDEBUG $(INCLUDES)
libla_bencher_debug_la_SOURCES	=	\
	$(SOURCES)
libla_bencher_debug_la_LIBADD=
else
lib_LTLIBRARIES	=	libla-bencher.la
endif

bin_PROGRAMS = intrinsics la-bencher

intrinsics_CPPFLAGS= $(AM_CXXFLAGS)
intrinsics_SOURCES= intrinsics.c intrinsics.h
intrinsics_LDADD=libla-bencher.la

la_bencher_CXXFLAGS= $(AM_CXXFLAGS) -std=gnu++0x
la_bencher_CFLAGS= $(AM_CFLAGS) -std=gnu99
la_bencher_SOURCES=  				\
	la-bencher.cpp 						\
	matrix.cpp 								\
	mat-mult.cpp							\
	kaapi/mat-mult-kaapi.cpp	\
	omp/mat-mult-omp.cpp			\
	pthrd/mat-mult-pthrd.cpp	\
	seq/mat-mult-seq.cpp			\
	tbb/mat-mult-tbb.cpp			\
	mat-elim.cpp							\
	mat-elim-tools.c					\
	blas/mat-elim-blas.c			\
	kaapi/mat-elim-kaapi.c		\
	omp/mat-elim-omp.cpp			\
	pthrd/mat-elim-pthrd.cpp	\
	seq/mat-elim-seq.cpp			\
	tbb/mat-elim-tbb.cpp			\
	mat-gen.cpp

CLEANFILES=				\
	../obj/*				\
	kaapi/.dirstamp	\
	pthrd/.dirstamp	\
	omp/.dirstamp		\
	tbb/.dirstamp		\
	seq/.dirstamp		

DISTCLEANFILES=		\
	../obj/*				\
	kaapi/.dirstamp	\
	pthrd/.dirstamp	\
	omp/.dirstamp		\
	tbb/.dirstamp		\
	seq/.dirstamp		
