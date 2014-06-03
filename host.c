/*
	C host for interacting nucleons
*/

#include "opencl.h"	// header for an OpenCL wrapper functions & types

#define v3r cl_float4	// corresponds to float4 OpenCL C vector type

static cl_kernel kernel_compute_forces, kernel_update_positions;	// kernels
static cl_var gpu_r, gpu_v, gpu_a, gpu_m, gpu_qe, gpu_qn;	// variables for kernels arguments

// initialization function; executed once before kernels are launched
// n -- number of particles (multiple of work-group size)
// wg_size -- work-group size
// r -- array of particles positions
// v -- array of particles speeds
// m -- array of particles masses
// qe -- array of particles electric charges (+1/-1/0)
// qn -- array of particles barionic charges (0/1)
extern void gpu_init(const uint n, const uint wg_size, const v3r r[], const v3r v[], const real m[], const int qe[], const int qn[])
{
	// initial stuff:
	opencl_init_gpu();
	// creating OpenCL C program from file with compiler parameter:
	cl_program program = opencl_create_program("kernel.cl", "-cl-single-precision-constant");
	// creating kernels:
	kernel_compute_forces = opencl_create_kernel(program, "compute_forces");
	kernel_update_positions = opencl_create_kernel(program, "update_positions");
	// creating variables for kernel arguments:
	gpu_r = opencl_create_var(sizeof(v3r), n, 0, r);
	gpu_v = opencl_create_var(sizeof(v3r), n, 0, v);
	gpu_a = opencl_create_var(sizeof(v3r), n, 0, NULL);
	gpu_m = opencl_create_var(sizeof(real), n, CL_MEM_READ_ONLY, m);
	gpu_qe = opencl_create_var(sizeof(int), n, CL_MEM_READ_ONLY, qe);
	gpu_qn = opencl_create_var(sizeof(int), n, CL_MEM_READ_ONLY, qn);
	// setting kernels arguments:
	opencl_set_kernel_args(kernel_compute_forces, gpu_r, gpu_v, gpu_a, gpu_m, gpu_qe, gpu_qn);
	opencl_set_kernel_args(kernel_update_positions, gpu_r, gpu_v, gpu_a);
	// specifying local (work-goup) and global sizes:
	opencl_set_local_ws(1, wg_size);
	opencl_set_global_ws(1, n);
}

// function for launching kernels (non-blocking)
extern void gpu_update()
{
	opencl_run_kernel(kernel_compute_forces);
	opencl_run_kernel(kernel_update_positions);
}

// function for reading back particles positions data (blocking read)
extern void gpu_getval(v3r r[])
{
	opencl_get_var(gpu_r, r);
}


// below there's a CPU variant of computation for execution time comparison purpose

#include <math.h>
#include "host.h"	// header file generated by python script (in order to have one place for dt, dt2 etc. definitions)

extern void cpu_update(const uint n, v3r r[], v3r v[], const real m[], const int qe[], const int qn[])
{
	v3r dr, r0, f;
	real d, d2, d1_2, d1_3, fs;
	uint i, j;
	int qe0, qn0;
	#pragma omp parallel for private(f, dr, r0, d, d2, d1_2, d1_3, fs, qe0, qn0, i, j)
	for (j=0; j<n; j++)
		if (m[j]>0)
		{
			f.x = f.y = f.z = 0;
			r0 = r[j];
			qe0 = qe[j];
			qn0 = qn[j];
			for (i=0; i<n; i++)
			{
				dr.x = r[i].x - r0.x;
				dr.y = r[i].y - r0.y;
				dr.z = r[i].z - r0.z;
				d2 = dr.x*dr.x + dr.y*dr.y + dr.z*dr.z;
				if (d2>0)
				{
					d = sqrt(d2);
					d1_2 = 1/d2;
					d1_3 = d1_2/d;
					fs = 0;
					if (d>1)
						fs -= qe0 * qe[i] * d1_3;	// electric force
					if (d>0.5 && d<1.5)
						fs += 200 * qn0 * qn[i] * (d1_3 - d1_2*d1_3);	// strong force
					f.x += dr.x * fs;
					f.y += dr.y * fs;
					f.z += dr.z * fs;
				}
			}
			f.x = f.x/m[j];
			f.y = f.y/m[j];
			f.z = f.z/m[j];
			r[j].x += dt * (v[j].x + dt2 * f.x);
			r[j].y += dt * (v[j].y + dt2 * f.y);
			r[j].z += dt * (v[j].z + dt2 * f.z);
			v[j].x += dt * f.x;
			v[j].y += dt * f.y;
			v[j].z += dt * f.z;
		}
}
