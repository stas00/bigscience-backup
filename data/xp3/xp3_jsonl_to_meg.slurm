#!/bin/bash
#SBATCH --job-name=xp3jsonl # job name
#SBATCH --ntasks=1                   # number of MP tasks
#SBATCH --nodes=1
#SBATCH --cpus-per-task=40           # number of cores per tasks
#SBATCH --hint=nomultithread         # we get physical cores not logical
#SBATCH --time=20:00:00             # maximum execution time (HH:MM:SS)
#SBATCH --output=%x-%j.out          # output file name
#SBATCH --account=six@cpu
#SBATCH --partition=cpu_p1
#SBATCH --qos=qos_cpu-t3

set -x -e

source $six_ALL_CCFRWORK/start-tr13f-6B3-ml-t0
export HF_DATASETS_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

MEGATRON_DEEPSPEED_REPO=$six_ALL_CCFRWORK/code/tr13f-6B3-ml-t0/Megatron-DeepSpeed

TOKENIZER_PATH="bigscience/tokenizer"

LANGS=(
ak
ar
as
bm
bn
ca
code
en
es
eu
fon
fr
gu
hi
id
ig
ki
kn
lg
ln
ml
mr
ne
nso
ny
or
pa
pt
rn
rw
sn
st
sw
ta
te
tn
ts
tum
tw
ur
vi
wo
xh
yo
zh
zu
)


DATA_PATH=/gpfswork/rech/six/commun/bigscience-training/jsonls/xp3capped/train

for val in {0..45}; do
    LANG=${LANGS[$val]}
    cd $DATA_PATH/$LANG
    cat *.jsonl > merged_dups_$LANG.jsonl
    # Drop duplicates (~1G / 37G for en)
    sort -u merged_dups_$LANG.jsonl | shuf > merged_$LANG.jsonl
    OUTPUT=/gpfswork/rech/six/commun/bigscience-training/xp3cappednew/train/xp3_train_$LANG
    cd $MEGATRON_DEEPSPEED_REPO
    python tools/preprocess_data.py \
        --input $DATA_PATH/$LANG/merged_$LANG.jsonl \
        --output-prefix $OUTPUT \
        --dataset-impl mmap \
        --json-key inputs \
        --tokenizer-type PretrainedFromHF \
        --tokenizer-name-or-path $TOKENIZER_PATH \
        --workers 35
    python tools/preprocess_data.py \
        --input $DATA_PATH/$LANG/merged_$LANG.jsonl \
        --output-prefix $OUTPUT \
        --dataset-impl mmap \
        --json-key targets \
        --tokenizer-type PretrainedFromHF \
        --tokenizer-name-or-path $TOKENIZER_PATH \
        --append-eod \
        --prepend-space \
        --workers 35
done

# No val data for other langs
LANGS=(
ar
bn
code
en
es
fr
hi
id
pt
sw
te
vi
zh
)

DATA_PATH=/gpfswork/rech/six/commun/bigscience-training/jsonls/xp3capped/validation
cd $DATA_PATH


for val in {0..12}; do
    LANG=${LANGS[$val]}
    cd $DATA_PATH/$LANG
    cat *.jsonl > merged_dups_$LANG.jsonl
    # Drop duplicates (~1G / 37G for en)
    sort -u merged_dups_$LANG.jsonl > merged_$LANG.jsonl
    OUTPUT=/gpfswork/rech/six/commun/bigscience-training/xp3cappednew/validation/xp3_validation_$LANG
    cd $MEGATRON_DEEPSPEED_REPO
    python tools/preprocess_data.py \
        --input $DATA_PATH/$LANG/merged_$LANG.jsonl \
        --output-prefix $OUTPUT \
        --dataset-impl mmap \
        --json-key inputs \
        --tokenizer-type PretrainedFromHF \
        --tokenizer-name-or-path $TOKENIZER_PATH \
        --workers 35
    python tools/preprocess_data.py \
        --input $DATA_PATH/$LANG/merged_$LANG.jsonl \
        --output-prefix $OUTPUT \
        --dataset-impl mmap \
        --json-key targets \
        --tokenizer-type PretrainedFromHF \
        --tokenizer-name-or-path $TOKENIZER_PATH \
        --append-eod \
        --prepend-space \
        --workers 35
done
