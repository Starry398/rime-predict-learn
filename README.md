# rime-predict-learn

为 Rime / 小企鹅输入法的 `liu_user_predict` 学习层生成**预置词级 bigram 数据**。

## 产物

`out/liu_user_predict.txt`，格式与 [liu_user_predict.lua](https://github.com/ryanwuson/rime-liur) 完全一致：

```
上文\t接续\t次数\t时间戳
我们\t的\t1200\t1700000000000
```

放进 Rime 用户目录（与 `predict.db` 同级）后重新部署，上屏预测会多出这批词级候选，且排序在学习层里优先于静态 `predict.db`。

## 语料

`pleisto/wikipedia-cn-20230720-filtered`（中文维基过滤版，约 100 万篇）。

## 参数

workflow_dispatch 可调：

| 参数 | 默认 | 说明 |
|---|---|---|
| `max_docs` | 80000 | 处理文档数 |
| `top_prev` | 15000 | 保留多少个上文 key |
| `per_key` | 8 | 每个上文最多几条接续 |
| `min_pair` | 3 | 词对最小出现次数 |

默认产出约 12 万条，文件几 MB。

## 限制

- 只保留 1–4 字纯汉字，标点/数字/英文会被丢弃
- `liu_user_predict.lua` 每个上文最多 15 条，超过会被裁剪
- 学习层全量加载进内存，条数别无限放大

## 手动跑

```bash
pip install jieba datasets
python scripts/build_learn_data.py --max-docs 80000
```
