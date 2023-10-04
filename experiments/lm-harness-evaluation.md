# LM Harness Evaluation

The evaluation harness from EleutherAI is integrated a submodule. We use a fork on [HF's Github](https://github.com/huggingface/lm-evaluation-harness).
To initialize the submodule, run:
```bash
git submodule init
git submodule update
```

Make sure you have the requirements in `lm-evaluation-harness`:
```bash
cd lm-evaluation-harness
pip install -r requirements.txt
```

To launch an evaluation, run:
```bash
python lm-evaluation-harness/main.py \
    --model gpt2 \
    --model_args pretrained=gpt2-xl \
    --tasks cola,mrpc,rte,qnli,qqp,sst,boolq,cb,copa,multirc,record,wic,wsc,coqa,drop,lambada,lambada_cloze,piqa,pubmedqa,sciq \
    --provide_description \ # Whether to provide the task description
    --num_fewshot 3 \ # Number of priming pairs
    --batch_size 2 \
    --output_path eval-gpt2-xl
```

Please note:
- As of now, only single GPU is supported in `lm-evaluation-harness`.
