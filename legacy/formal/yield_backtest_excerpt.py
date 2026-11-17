"""Historical yield backtest excerpt; not verified to reproduce the report.
Source: data_train_backtest.py, DataTrain methods only.
No Wind connection or perpetual-bond batch execution is included.
"""
import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

class LegacyYieldBacktest:
    def make_dirs(self, file_path):
        '''
        传入文件路径，判断文件路径是否存在，不存在则创建
        file_path: 文件路径
        '''
        dir_path = os.path.dirname(file_path)
        # print(dir_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)


    def tradesignal(self, data):
        tradesignaldata = data.copy()
        position = 0
        for i in tradesignaldata.index:
            if (tradesignaldata.loc[i, 'signal'] == 1) & (position == 0):
                tradesignaldata.loc[i, 'tradesignal'] = 1
                position += 1
            elif (tradesignaldata.loc[i, 'signal'] == -1) & (position == 1):
                tradesignaldata.loc[i, 'tradesignal'] = -1
                position += -1
            else:
                tradesignaldata.loc[i, 'tradesignal'] = 0
            tradesignaldata.loc[i, 'position'] = position
        tradesignaldata['tradesignal'] = tradesignaldata['tradesignal'].shift(fill_value=0)
        tradesignaldata['position'] = tradesignaldata['position'].shift(fill_value=0)
        data['tradesignal'] = tradesignaldata['tradesignal']
        data['position'] = tradesignaldata['position']
        return data


    def trade1(self, data):
        trade1data = data.copy()
        # 计算利息率
        trade1data['interest rate'] = trade1data['yield'] * trade1data['position'] * trade1data['tradesignal']
        trade1data['interest rate'] = trade1data['interest rate'].replace(0, np.nan).ffill().fillna(0) * trade1data[
            'position']
        # 设日期为index:trade1data.set_index('日期', inplace=True, drop=True)
        # 拼接日历日
        trade1data_ziranri = pd.DataFrame(
            index=pd.date_range(start=trade1data.index[0], end=trade1data.index[-1], freq="D"))
        trade1data = trade1data_ziranri.merge(trade1data, left_index=True, right_index=True, how="left")
        trade1data['yield'] = trade1data['yield'].ffill()
        trade1data['signal'] = trade1data['signal'].fillna(0)
        trade1data['tradesignal'] = trade1data['tradesignal'].fillna(0)
        trade1data['position'] = trade1data['position'].ffill()
        trade1data['interest rate'] = trade1data['interest rate'].ffill()
        return trade1data


    def trade2(self, data, term):
        trade2data = data.copy()
        # 计算资本利得
        trade2data['trading income bps'] = -(trade2data['yield'] - trade2data['yield'].shift()).fillna(0)
        # 初始仓位
        openworth = 100
        lastworth = 100
        # 计算仓位
        for i in trade2data.index:
            if trade2data.loc[i, 'position'] == 0 and trade2data.loc[i, 'tradesignal'] == 0:
                # 尚未首次开仓
                trade2data.loc[i, 'trading income'] = 0
                trade2data.loc[i, 'interest rate income'] = 0
                trade2data.loc[i, 'networth'] = openworth
            # elif tradedata.loc[i,'position'] == 1 & ((tradedata.loc[i,'tradesignal'] == 1) | (tradedata.loc[i,'tradesignal'] == 0)):
            elif trade2data.loc[i, 'position'] == 1 and trade2data.loc[i, 'tradesignal'] == 1:
                # 首次开仓
                trade2data.loc[i, 'trading income'] = 0
                trade2data.loc[i, 'interest rate income'] = openworth * trade2data.loc[i, 'interest rate'] / 36500
                dailypnl = trade2data.loc[i, 'interest rate income']
                lastworth += dailypnl
                trade2data.loc[i, 'networth'] = lastworth
            elif trade2data.loc[i, 'position'] == 1 and trade2data.loc[i, 'tradesignal'] == 0:
                # 首次开仓后持仓
                trade2data.loc[i, 'trading income'] = openworth * term * trade2data.loc[i, 'trading income bps'] / 100
                trade2data.loc[i, 'interest rate income'] = openworth * trade2data.loc[i, 'interest rate'] / 36500
                dailypnl = trade2data.loc[i, 'trading income'] + trade2data.loc[i, 'interest rate income']
                lastworth += dailypnl
                trade2data.loc[i, 'networth'] = lastworth
            # elif tradedata.loc[i,'position'] == 1 and tradedata.loc[i,'tradesignal'] == 0:
            #     #持仓
            #     networth = networth + networth*tradedata.loc[i,'interest rate']/36500 + networth*int(y[-2])*tradedata.loc[i,'trading income']/1000000
            elif trade2data.loc[i, 'position'] == 0 and trade2data.loc[i, 'tradesignal'] == -1:
                # 首次开仓持仓后平仓并更新openworth
                trade2data.loc[i, 'trading income'] = openworth * term * trade2data.loc[i, 'trading income bps'] / 100
                trade2data.loc[i, 'interest rate income'] = 0
                dailypnl = trade2data.loc[i, 'trading income']
                lastworth += dailypnl
                trade2data.loc[i, 'networth'] = lastworth
                # 一个开仓持仓平仓周期结束后更新openworth
                openworth = lastworth
                # 报错
            else:
                trade2data.loc[i, 'networth'] = 'something wrong'
        return trade2data


    def performance(self, data, rf):
        performancedata = data.copy()
        # 计算年化ROA
        ROA = 365 * (performancedata['networth'][-1] - performancedata['networth'][0]) / (
                performancedata['networth'] * performancedata['position']).sum()
        # year_earnings = (performancedata['networth'][-1]-performancedata['networth'][0])/((performancedata.index[-1]-performancedata.index[0])/np.timedelta64(1,'D'))*365
        # zhanzi = (performancedata['networth']*performancedata['position']).sum()/((performancedata.index[-1]-performancedata.index[0])/np.timedelta64(1,'D'))
        # ROA = earings/zhanzi
        # ROA=(performancedata['networth'][-1]-performancedata['networth'][0])/performancedata['networth'][0]/((performancedata.index[-1]-performancedata.index[0])/np.timedelta64(1,'D'))*365
        # 计算开仓次数
        if performancedata['tradesignal'].sum() != 0:
            num = performancedata['tradesignal'][performancedata['tradesignal'] > 0].sum() - 1
        else:
            num = performancedata['tradesignal'][performancedata['tradesignal'] > 0].sum()
        # 计算年化收益率
        daily_pctchange = performancedata['networth'].pct_change()
        Annual_yield = daily_pctchange.mean() * 365
        # 计算年化波动率
        Annual_std = daily_pctchange.std() * math.sqrt(365)
        # 计算夏普比率
        if Annual_std == 0:
            Sharp_ratio = 'NA'
        else:
            Sharp_ratio = (Annual_yield - rf) / Annual_std
        # 最大回撤
        Max_drawdown = max(
            (np.maximum.accumulate(performancedata['networth']) - performancedata['networth']) / np.maximum.accumulate(
                performancedata['networth']))
        # 卡尔玛比率
        if Max_drawdown == 0:
            Calmar_ratio = 'NA'
        else:
            Calmar_ratio = (Annual_yield - rf) / Max_drawdown
        return {'训练集准确率': self.acc_train, '测试集准确率': self.acc_test, '年化收益率': Annual_yield,
                '年化波动率': Annual_std, '夏普比率': Sharp_ratio, '最大回撤': Max_drawdown,
                '卡尔玛比率': Calmar_ratio, 'ROA': ROA, '开仓次数': num}


    def backtest(self, plt_savepath, term, model, test_file):
        '''
        回测函数
        plt_savepath: 图表保存路径
        '''
        # 指定文件
        # file_name = r'.\result\adaboost\ada_cl_test_国开1yYTM.xlsx'
        file_name = os.path.join('result', model, test_file)

        # 读取数据
        # 数据应为三列，表头分别为date代表日期，yield代表收益率，signal代表策略发出的原信号
        # 若某日有原信号1/0/-1，则第二日执行交易买入/不动/卖出

        df = pd.read_excel(file_name)
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df = df.loc[df['date'] > '20231230']
        df.set_index(['date'], drop=True, inplace=True)

        # 计算结果
        df = self.tradesignal(df)
        df = self.trade2(self.trade1(df), term)
        df['trading income accu'] = df['trading income'].cumsum()
        df['interest rate income accu'] = df['interest rate income'].cumsum()
        df['pnl accu'] = df['trading income accu'] + df['interest rate income accu']
        df['trading income percentage'] = df['trading income accu'] / df['pnl accu']
        df['trading income percentage'] = df['trading income percentage'].fillna(0)
        performace = self.performance(df, 0.02)
        print(performace)

        df['date'] = df.index
        df0 = df.copy()
        fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
        plt.grid()
        title1 = '策略总体表现'
        plt.title(title1)
        line1 = ax.plot(df['date'], df['networth'], label='净值曲线(左轴、起始资金100)', color='crimson', linewidth=1,
                        alpha=0.9)
        ax_twin = ax.twinx()
        line2 = ax_twin.plot(df['date'], df['yield'], label="收益率曲线(右轴)", color='slategrey', linewidth=0.5,
                             linestyle="dashed")
        # 增加开多和开空时间点位
        long_idx = df[df['tradesignal'] == 1]['date']
        short_idx = df[df['tradesignal'] == -1]['date']
        line3 = ax_twin.plot(long_idx, df.loc[df['date'].isin(long_idx), 'yield'], '>', alpha=0.5, markersize=6,
                             color='lightcoral', label='开仓')
        line4 = ax_twin.plot(short_idx, df.loc[df['date'].isin(short_idx), 'yield'], '<', alpha=0.5, markersize=6,
                             color='springgreen', label='平仓')
        # 加图例
        lines = line1 + line2 + line3 + line4
        labels = [line.get_label() for line in lines]
        ax.legend(lines, labels, loc='upper left')
        ax.xaxis.set_major_locator(ticker.MultipleLocator(100))  # 设置绘图坐标轴间隔
        fig.autofmt_xdate()  # 自动旋转xlabel
        # 未存在的文件需要创建
        self.make_dirs(plt_savepath)
        plt.savefig(plt_savepath + f'{model}_{title1}.png', dpi=300)
        # plt.show()

        fig, ax = plt.subplots(figsize=(10, 5), dpi=100)  # figsize=(20,10),
        plt.grid()
        title2 = '策略资本利得情况'
        plt.title(title2)
        line1 = ax.plot(df['date'], df['pnl accu'], label='总收入曲线(起始资金100)', color='crimson', linewidth=1,
                        alpha=0.9)
        line2 = ax.plot(df['date'], df['trading income accu'], label="累计资本利得曲线", color='tab:green',
                        linewidth=0.5, linestyle="dashed")
        line3 = ax.plot(df['date'], df['interest rate income accu'], label="累计利息收入曲线", color='slategrey',
                        linewidth=0.5, linestyle="dashed")
        # 加图例
        lines = line1 + line2 + line3
        labels = [line.get_label() for line in lines]
        ax.legend(lines, labels, loc='upper left')
        ax.xaxis.set_major_locator(ticker.MultipleLocator(100))  # 设置绘图坐标轴间隔
        fig.autofmt_xdate()  # 自动旋转xlabel
        self.make_dirs(plt_savepath)
        plt.savefig(plt_savepath + f'{model}_{title2}.png', dpi=300)
        # plt.show()

        df_performace = pd.DataFrame(performace, index=[0])
        print(df_performace)
        df_performace.to_excel(plt_savepath + f'{model}_performance.xlsx', index=False)

