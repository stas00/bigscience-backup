# Megatron-LM Notes and Nuances


## Configuration

- Data Parallel: `data-parallel-size = world_size / (pipeline_model_parallel_size * tensor_model_parallel_size)`
   By default, `pipeline_model_parallel_size=`` and `tensor_model_parallel_size=1`


## Troubleshooting

- if megatron hangs in:

```
>>> done with dataset index builder. Compilation time: 0.107 seconds
> compiling and loading fused kernels ...
```
do:
```
rm megatron/fused_kernels/build/lock
```
and restart.


## General Performance Notes

NVIDIA paper: https://arxiv.org/abs/2104.04473v2

- they used 80GB A100s with 312TFlops/gpu (and achieved about 50% of that in the largest model/batch size (163TFlops)

- we are using 32GB V100s with 125TFlops/gpu

- The DGX-2 clusters used by NVIDIA have 300GBps intra-node connections and 800Gbps inter-node connections

- JZ on the other hand has 50GBps intra-node connections and 400Gbps inter-node connections.

and the rest of the hardware is less powerful (so if we reach about 35-50TFlops that would be fantastic)

Their main scaling table:

- model parallel size = tensor model parallel * pipeline model parallel

where tensor parallel is 8 at the most

So for example for 76B it says MP=32, which means 8 * 4 - so `PP_size=4` and `TP_size=8`

Basically use tensor model parallelism within a node, then use pipeline model parallelism for larger models
- So if MP size <= 8, tensor MP = MP size, pipeline MP = 1
- Otherwise, tensor MP = 8, pipeline MP = (MP size // 8 )

DataParallel isn't not in the table, it's:

DP = (total number of GPUs // MP size)

Here is the main table from the paper with added breakdown of TP/PP/DP:

|       |       |        |     |    |    |    |     |      |       |        |        |        |        |
| ---:  | ----: | -----: | --: | -: | -: | -: | --: | ---: |  ---: | -----: |  ----: |  ----: | -----: |
| Model | Atten | Hidden | Lay | TP | PP | DP |  MP | GPUs | Micro | Global | TFlops | TFlops | PFlops |
| size  | heads |   size | ers |    |    |    |     |      |    BS |     BS |   /GPU |      % | Aggreg |
| 1.7B  |    24 |   2304 |  24 |  1 |  1 | 32 |   1 |   32 |    16 |    512 |    137 |    44% |    4.4 |
| 3.6B  |    32 |   3072 |  30 |  2 |  1 | 32 |   2 |   64 |    16 |    512 |    138 |    44% |    8.8 |
| 7.5B  |    32 |   4096 |  36 |  4 |  1 | 32 |   4 |  128 |    16 |    512 |    142 |    46% |   18.2 |
| 18B   |    48 |   6144 |  40 |  8 |  1 | 32 |   8 |  256 |     8 |   1024 |    135 |    43% |   34.6 |
| 39B   |    64 |   8192 |  48 |  8 |  2 | 32 |  16 |  512 |     4 |   1536 |    138 |    44% |   70.8 |
| 76B   |    80 |  10240 |  60 |  8 |  4 | 32 |  32 | 1024 |     2 |   1792 |    140 |    45% |  143.8 |
| 145B  |    96 |  12288 |  80 |  8 |  8 | 24 |  64 | 1536 |     2 |   2304 |    148 |    47% |  227.1 |
| 310B  |   128 |  16384 |  96 |  8 | 16 | 15 | 128 | 1920 |     1 |   2160 |    155 |    50% |  297.4 |
| 530B  |   128 |  20480 | 105 |  8 | 35 |  9 | 280 | 2520 |     1 |   2520 |    163 |    52% |  410.2 |
| 1T    |   160 |  25600 | 128 |  8 | 64 |  6 | 512 | 3072 |     1 |   3072 |    163 |    52% |  502.0 |
|       |       |        |     |    |    |    |     |      |       |        |        |        |        |


## TODO

Notes from Jared - to sort:

- batch size

`--global-batch-size` leads to automatic gradient accumulation, so for example on 4-gpu node with:

with only 4-way data parallel using a micro batch size of 16 and global batch size of 2048 it's going to do gradient accumulation on 32 batches for each iteration.

so probably best not to use this argument, unless it's thought through.

--micro-batch-size is always the smallest "batch size", it's what gets sent through the model.

--global-batch-size will default to micro batch size * data parallelism unless specified. With the default value there will be no gradient accumulation. If specified, gradient accumulation will happen to reach the global batch size. The "chunks" you talk about above for PP we see as just gradient accumulation. Without gradient accumulation PP is very inefficient with no overlap of executing the different stages. So the more micro-batches that get accumulated, or the large the global batch size, the more efficient PP will be.
We discussed a lot about how best to expose that in arguments and decided most of the time we care about the micro batch size and the global batch size and don't want to do the math to figure out the number of microbatches done to get to the global batch size. Especially since we will sometimes have a dynamic global batch size

So bottom line under PP number of micro-batches == gradient accumulation
# Megatron-LM notes
