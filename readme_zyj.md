# 数据集导入

使用OASIS数据集，下载后训练数据集和验证数据集直接使用其中的`aligned_norm.nii.gz`和`aligned_seg35.nii.gz`即可。测试数据需要使用`convert_nii_to_pkl.py`代码文件将`nii.gz`转换为`pkl`文件。

# 依赖库安装

```shell
conda install pytorch torchvision torchaudio cudatoolkit=11.3 -c pytorch
conda install batchgenerators
conda install natsort
conda install pystrum
conda install nibabel
conda install ml_collections
conda install timm
```

# TransMorph

- 训练模型

  ```shell
  python train_TransMorph.py
  ```

- 测试模型

  ```shell
  python infer_TransMorph.py
  ```

- 代码文件说明

  |      文件/文件夹      |                     作用                     |
  | :-------------------: | :------------------------------------------: |
  |         data          |          生成模型可以用的数据集输入          |
  |        models         |           Transformer模型整体框架            |
  | convert_nii_to_pkl.py |             将nii.gz文件转为pkl              |
  |  infer_TransMorph.py  |                   测试模型                   |
  |       losses.py       |                 损失函数相关                 |
  |   seg35_labels.txt    |    分割图标签说明，用于最后计算每类的dsc     |
  |  train_TransMorph.py  |                   训练模型                   |
  |       utils.py        | 计算一些指标和实现一些基本变换的基本函数和类 |

# nnFormer

- 训练模型

  ```shell
  python train_TransMorph.py
  ```

- 测试模型

  ```shell
  python infer_TransMorph.py
  ```

- 代码文件说明

  |    文件/文件夹    |                           作用                           |
  | :---------------: | :------------------------------------------------------: |
  |       data        |                生成模型可以用的数据集输入                |
  |      models       |                 Transformer模型整体框架                  |
  |  img0438.nii.gz   | 测试集中编号为0438的被试的数据，在测试阶段用于获取affine |
  | infer_nnFormer.py |                         测试模型                         |
  |     losses.py     |                       损失函数相关                       |
  | seg35_labels.txt  |          分割图标签说明，用于最后计算每类的dsc           |
  | train_nnFormer.py |                         训练模型                         |
  |     utils.py      |       计算一些指标和实现一些基本变换的基本函数和类       |
  |  val_nnFormer.py  |                用验证集数据进一步评价模型                |