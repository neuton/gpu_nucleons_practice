#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "host.c"

#define n 8192
#define nn 10

int main()
{
	puts("Testing...\n");
	v3r r[n], v[n];
	real m[n];
	int qe[n], qn[n];
	uint i;
	for (i=0; i<n; i++)
	{
		r[i].x = 10*rand()-5;
		r[i].y = 10*rand()-5;
		r[i].z = 10*rand()-5;
		v[i].x = rand()-0.5;
		v[i].y = rand()-0.5;
		v[i].z = rand()-0.5;
		m[i] = rand();
		qe[i] = 1;
		qn[i] = 1;
	}
	gpu_init(n,64,r,v,m,qe,qn);
	time_t t0;
	real dt_gpu, dt_cpu;

	for (i=0; i<5*nn; i++)	// for "heating up" GPU
		gpu_update();
	opencl_sync();
	t0 = clock();
	for (i=0; i<nn; i++)
		gpu_update();
	opencl_sync();
	dt_gpu = difftime(clock(), t0)/CLOCKS_PER_SEC;
	printf("GPU update: %.3f sec\n", dt_gpu);

	t0 = clock();
	for (i=0; i<nn; i++)
		cpu_update(n,r,v,m,qe,qn);
	dt_cpu = difftime(clock(), t0)/CLOCKS_PER_SEC;
	printf("CPU update: %.3f sec\n", dt_cpu);
	
	printf("\nboost: x%.1f\n", dt_cpu/dt_gpu);
	
	return 0;
}
