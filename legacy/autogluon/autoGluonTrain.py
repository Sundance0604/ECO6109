import pandas as pd
from autogluon.tabular import TabularPredictor

def data_split(filePath:str, label_col:str ):
    df_raw = pd.read_excel(filePath)
    df_raw.set_index('date', inplace=True)

    # 先删除目标列为空的行
    df_raw = df_raw.dropna(subset=[label_col])

    # 涨跌标签：下一期比当前期涨为 1，跌为 -1，不变为 0
    df_raw['label'] = (df_raw[label_col].shift(-1) - df_raw[label_col]).apply(
        lambda x: -1 if x > 0 else (1 if x < 0 else 0)
    )

    # 若为 0，则继承前一个标签
    df_raw['label'] = df_raw['label'].replace(0, method='ffill')

    # 删除最后一行（因为没有未来数据做标签）
    df_clean = df_raw.iloc[:-1]

    # 假设 df_clean 已经准备好，索引为时间或顺序
    label_col = "label"
    split_point = int(len(df_clean) * 0.8)

    # 按顺序切分
    df_train = df_clean.iloc[:split_point]
    df_test  = df_clean.iloc[split_point:]

    # 拆分特征和标签
    X_train, y_train = df_train.drop(columns=[label_col]), df_train[label_col]
    X_test,  y_test  = df_test.drop(columns=[label_col]),  df_test[label_col]

    train_data = pd.concat([X_train, y_train], axis=1)
    test_data = pd.concat([X_test, y_test], axis=1)
    return train_data, test_data
def model(train_data:pd.DataFrame, test_data:pd.DataFrame, label_col:str, save_path:str):
    # 可修改presets参数
    predictor = TabularPredictor(label=label_col).fit(train_data,presets='best')
    