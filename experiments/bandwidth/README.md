# Bandwidth tests

## Deepspeed benchmark

https://gist.github.com/stas00/ec5e197b15e2e7aea0153f54d2f97c15

Probably need to adjust `TRIALS` to a higher number to get the more realistic results (after the interconnects is saturated).

Note: tried a larger number but got the same results.

## Single node V100

ssh into a desired node and then:
```
export NCCL_DEBUG=info
python -m torch.distributed.launch --nproc_per_node=4 all_reduce_bench.py 2>&1 | tee n1_32gb_all_reduce_bench.txt
```

Results:
- [16gb](./n1_16gb_all_reduce_bench.txt) - `algo throughput: 1329.4242 Gbps`
- [32gb](./n1_32gb_all_reduce_bench.txt) - `algo throughput: 1323.6244 Gbps`

Here we have NVLink gen 2

https://en.wikipedia.org/wiki/NVLink
```
Nvidia GV100 | V100 SXM2 | NVLink 2.0 | 25 GT/s | 300 GByte/s
```
So the total is 300GB/s => 2400 Gb/s

and the benchmark clocks 1360 Gb/s - slightly more than half of the max total.

if this test is run a bit longer, it drops to 600 Gbps.



## 16 nodes V100 32GB

```
export NCCL_DEBUG=info
export MASTER_ADDR=$(scontrol show hostnames $SLURM_JOB_NODELIST | head -n 1)
srun --jobid $SLURM_JOBID bash -c 'python -m torch.distributed.launch --nnodes 16 --nproc_per_node=4 --node_rank $SLURM_PROCID --master_addr $MASTER_ADDR --master_port 12345 all_reduce_bench.py'  2>&1 | tee n16_32gb_all_reduce_bench.txt
```
Results:

- [32gp](./n16_32gb_all_reduce_bench.txt) - `algo throughput: 23.2939 to 55.0766 Gbps`

If the test is run much longer it fluctuates between 44 and 57 Gbps.

Currently we have an issue with nccl that doesn't fully utilize Intel OPA full bandwidth. Which is supposed to be 400Gbps max.


## 4 nodes V100 32GB

Here is a recent re-run - jan 2022:

script: [all_reduce_bench-32gb-n4.slurm](./all_reduce_bench-32gb-n4.slurm)


```
sbatch all_reduce_bench-32gb-n4.slurm
```

Results:

[all_reduce_bench-32gb-n4.txt](./all_reduce_bench-32gb-n4.txt) - `algo throughput: 30 to 90 Gbps`




## 4 nodes A100 80GB


script: [all_reduce_bench-a100-n4.slurm](./all_reduce_bench-a100-n4.slurm)


```
sbatch all_reduce_bench-a100-n4.slurm
```

Results:

[all_reduce_bench-a100-n4.txt](./all_reduce_bench-a100-n4.txt) - `algo throughput: 15 to 42 Gbps`

As a reference Azure has [ND A100 v4-series](https://docs.microsoft.com/en-us/azure/virtual-machines/nda100-v4-series) w/ 1.6 Tb/s of interconnect bandwidth per VM. And Jeff Rasley clocked ~1.5Tb/s with this `all_reduce_bench` script.


## NCCL tests

https://github.com/nvidia/nccl-tests

The details are explained here:

https://github.com/NVIDIA/nccl-tests/blob/master/doc/PERFORMANCE.md

```
git clone https://github.com/nvidia/nccl-tests
cd nccl-tests
make
```


## Single node

ssh into a desired node and then:
```
./build/all_reduce_perf -b 8 -e 128M -f 2 -g 4
```


## 16 nodes

from master node:
```
srun --jobid $SLURM_JOBID ./build/all_reduce_perf -b 8 -e 128M -f 2 -g 4
```
(not sure if I did it right - didn't have time to read the docs)
