import pandas as pd
import numpy as np
data_path = r'D:\比赛数据\360rong'.decode('utf-8').encode('gbk')
title = 'r360'

bill_detail_train = pd.read_csv(r'{}\train\bill_detail_train.txt'.format(data_path),header = None)
bill_detail_test = pd.read_csv(r'{}\test\bill_detail_test.txt'.format(data_path), header = None)
# 用户id，账单时间戳、银行id、上期账单金额、上期还款金额、信用卡额度、本期账余额、本期账单最低还款额、
#消费笔数,本期账单金额、调整金额，循环利息、可用余额、预借金额额度、还款状态
col_names = ['userid', 'tm_encode_3', 'bank_id', 'prior_account', 'prior_repay', 'credit_limit', 'account_balance','minimun_repay',
             'consume_count', 'account', 'adjust_account', 'circulated_interest', 'avaliable_balance', 'cash_limit', 'repay_state']
bill_detail_train.columns = col_names; bill_detail_test.columns = col_names
bill_detail = pd.concat([bill_detail_train, bill_detail_test])
bill_detail.tm_encode_3 = bill_detail.tm_encode_3.map(lambda i:datetime.datetime.fromtimestamp(i))
bill_detail = bill_detail.set_index('userid')


def set_count(arr):
    return arr.value_counts().count()

def max_cha(arr):
    return arr.max() - arr.min()

def bill_pro(bill_detail):
    bill_detail['tm_date'] = bill_detail.tm_encode_3.map(lambda i: i.date())
    bill_detail_t['tm_yearMonth'] = bill_detail_t.tm_date.map(lambda i: i.strftime('%Y-%m'))
    # clean cols
    clean_cols = ['adjust_account', 'circulated_interest', 'avaliable_balance', 'repay_state']
    bill_detail = bill_detail.drop(clean_cols, axis=1)
    # clean index
    nullcol_names = ['prior_account', 'prior_repay', 'credit_limit', 'account_balance', 'minimun_repay',
                     'consume_count', 'account', 'cash_limit']
    bill_detail_1 = bill_detail[nullcol_names];
    null_dis = (bill_detail_1 == 0).sum(axis=1)
    clean_index = null_dis[null_dis == 8].index;
    bill_detail = bill_detail.drop(clean_index[clean_index <= 55596], axis=0)
    print r'0值处理后，bill_detail的大小为', bill_detail.shape
    # 0值如何填充，暂未处理
    # count 1个
    bill_pro_1a = bill_detail.reset_index()
    temp = bill_pro_1a[['bank_id', 'userid']].groupby('userid')['bank_id'].value_counts()
    bill_pro_1 = pd.DataFrame(temp.count(level='userid'));
    bill_pro_1.columns = ['bill_bankid_count']
    print r'表1大小', bill_pro_1.shape
    # bank_id, credit_limit  # credit_limit的0值做删除处理 3个
    bill_detail_2 = bill_detail.reset_index()
    bill_detail_2['credit_limit'][bill_detail_2.credit_limit == 0] = bill_detail_2.credit_limit.mean()
    bill_pro_2 = bill_detail_2[['userid', 'bank_id', 'credit_limit']].groupby(['userid', 'bank_id'])[
        'credit_limit'].mean().unstack()
    bill_pro_2['bill_limitSum'] = bill_pro_2.sum(axis=1).round(decimals=1)
    bill_pro_2['bill_limitMean'] = bill_pro_2.mean(axis=1).round(decimals=1)
    bill_pro_2['bill_limitStd'] = bill_pro_2.std(axis=1).round(decimals=2)
    bill_pro_2 = bill_pro_2[['bill_limitSum', 'bill_limitMean', 'bill_limitStd']]
    print r'表2大小', bill_pro_2.shape
    # account  4个
    bill_detail_4a = bill_detail.reset_index()
    bill_pro_4a = \
    bill_detail_4a[['userid', 'bank_id', 'tm_yearMonth', 'account']].groupby(['userid', 'bank_id', 'tm_yearMonth'])[
        'account'].max()  # 去噪
    bill_pro_4a = bill_pro_4a.sum(
        level=['userid', 'tm_yearMonth']).unstack()  # bill_pro_4a:(index:userid, col:yearMonth, val:account)
    bill_pro_4 = pd.DataFrame([])
    bill_pro_4['bill_account_std'] = bill_pro_4a.std(axis=1).round(decimals=2)
    bill_pro_4b = bill_pro_4a.pct_change(axis=1);
    bill_pro_4b[bill_pro_4b == np.inf] = 0;
    bill_pro_4b[bill_pro_4b == -np.inf]  # 有inf值设为0.#bill_pro_4b:(index:userid, col:yearMonth, val:pat)
    bill_pro_4['bill_account_pctSum'] = bill_pro_4b.sum(axis=1).round(decimals=3)
    bill_pro_4['bill_account_pctSumAbs'] = bill_pro_4b.sum(axis=1).abs().round(decimals=3)
    bill_pro_4 = bill_pro_4.fillna(0)
    bill_pro_4['bill_account_monthAvg'] = bill_pro_4a.mean(axis=1).round(decimals=1)
    print r'表4大小', bill_pro_4.shape
    # minimun_repay 3个
    bill_detail_5a = bill_detail.reset_index()
    bill_pro_5a = bill_detail_5a[['userid', 'bank_id', 'tm_yearMonth', 'minimun_repay']].groupby(
        ['userid', 'bank_id', 'tm_yearMonth'])['minimun_repay'].mean()  # 去噪
    bill_pro_5a = bill_pro_5a.sum(level=['userid', 'tm_yearMonth']).unstack()
    bill_pro_5 = pd.DataFrame([])
    bill_pro_5b = bill_pro_5a.pct_change(axis=1);
    bill_pro_5b[bill_pro_5b == np.inf] = 0;
    bill_pro_5b[bill_pro_5b == -np.inf] = 0  # 有inf值,设为0
    bill_pro_5['bill_minimunRepay_pctSum'] = bill_pro_5b.sum(axis=1).round(decimals=3)
    # bill_pro_5['bill_account_pctSumAbs'] = bill_pro_5b.sum(axis=1).abs().round(decimals=3)
    bill_pro_5['bill_minimunRepay_std'] = bill_pro_5a.std(axis=1).round(decimals=2)
    bill_pro_5 = bill_pro_5.fillna(0)
    bill_pro_5['bill_minimunRepay_mean'] = bill_pro_5a.mean(axis=1).round(decimals=1)
    bill_pro_5 = bill_pro_5.fillna(bill_pro_5.mean())
    # 'prior_account', 'prior_repay' 9个
    bill_detail_6 = bill_detail.reset_index()
    bill_pro_6 = pd.DataFrame()
    bill_pro_6a = bill_detail_6[['userid', 'bank_id', 'tm_yearMonth', 'prior_account']].groupby(
        ['userid', 'bank_id', 'tm_yearMonth'])['prior_account'].mean()  # 去噪
    bill_pro_6a = bill_pro_6a.sum(level=['userid', 'tm_yearMonth']).unstack()
    # 标记
    temp = bill_pro_6a.pct_change(axis=1);
    temp[temp == np.inf] = 0;
    temp[temp == -np.inf] = 0
    bill_pro_6['bill_priorAccount_pctSum'] = temp.sum(axis=1).round(decimals=2)
    bill_pro_6['bill_priorAccount_mean'] = bill_pro_6a.mean(axis=1).round(decimals=1)
    bill_pro_6['bill_priorAccount_max'] = bill_pro_6a.max(axis=1).round(decimals=1);
    bill_pro_6 = bill_pro_6.fillna(bill_pro_6.mean())
    bill_pro_6['bill_priorAccount_std'] = bill_pro_6a.std(axis=1).round(decimals=2);
    bill_pro_6 = bill_pro_6.fillna(0)
    bill_pro_7 = pd.DataFrame()
    bill_pro_7a = \
    bill_detail_6[['userid', 'bank_id', 'tm_yearMonth', 'prior_repay']].groupby(['userid', 'bank_id', 'tm_yearMonth'])[
        'prior_repay'].mean()
    bill_pro_7a = bill_pro_7a.sum(level=['userid', 'tm_yearMonth']).unstack()
    #
    temp = bill_pro_7a.pct_change(axis=1);
    temp[temp == np.inf] = 0;
    temp[temp == -np.inf] = 0
    bill_pro_7['bill_priorRepay_pctSum'] = temp.sum(axis=1).round(decimals=2)
    bill_pro_7['bill_priorRepay_mean'] = bill_pro_7a.mean(axis=1).round(decimals=1)
    bill_pro_7['bill_priorRepay_max'] = bill_pro_7a.max(axis=1).round(decimals=1);
    bill_pro_7 = bill_pro_7.fillna(bill_pro_7.mean())
    bill_pro_7['bill_priorRepay_std'] = bill_pro_7a.std(axis=1).round(decimals=2);
    bill_pro_7 = bill_pro_7.fillna(0)
    bill_pro_8 = pd.DataFrame()
    bill_detail_8 = bill_detail.reset_index()
    bill_detail_8['bill_priorRepayCAccount'] = bill_detail_8.prior_repay / bill_detail_8.prior_account
    bill_pro_8a = bill_detail_8[['userid', 'bank_id', 'tm_yearMonth', 'bill_priorRepayCAccount']].groupby(
        ['userid', 'bank_id', 'tm_yearMonth'])['bill_priorRepayCAccount'].mean()
    bill_pro_8a = bill_pro_8a.sum(level=['userid', 'tm_yearMonth']).unstack()
    bill_pro_8['bill_priorRepayCAccount_std'] = bill_pro_8a.std(axis=1).round(decimals=2);
    bill_pro_8 = bill_pro_8.fillna(0)
    # others  2个
    bill_detail_9 = bill_detail.reset_index()
    bill_pro_9 = bill_detail_9[['userid', 'bank_id']].groupby('userid').agg('count').add_prefix('bill_count')
    bill_pro_9['bill_count_monthAvg'] = \
    bill_detail_9[['userid', 'bank_id', 'tm_yearMonth']].groupby(['userid', 'tm_yearMonth'])['bank_id'].count().mean(
        level='userid').round(decimals=0)

    # account_balance 3个
    bill_detail_10 = bill_detail.reset_index()
    temp = bill_detail_10[['userid', 'bank_id', 'account_balance', 'tm_yearMonth']].groupby(
        ['userid', 'tm_yearMonth', 'bank_id'])['account_balance'].mean()
    temp = temp.sum(level=['userid', 'tm_yearMonth']).unstack();
    temp_1 = temp.pct_change(axis=1);
    temp_1[temp_1 == np.inf] = 0;
    temp_1[temp_1 == -np.inf] = 0;
    bill_pro_10 = pd.DataFrame(temp_1.sum(axis=1).round(decimals=2));
    bill_pro_10 = bill_pro_10.fillna(bill_pro_10.mean())
    bill_pro_10.columns = ['bill_accountBalance_pctSum']
    bill_pro_10['bill_accountBalance_std'] = temp.std(axis=1).round(decimals=2)
    bill_pro_10['bill_accountBalance_mean'] = temp.mean(axis=1).round(decimals=1)

    bill_pro = pd.concat(
        [bill_pro_1, bill_pro_2, bill_pro_4, bill_pro_5, bill_pro_6, bill_pro_7, bill_pro_8, bill_pro_9, bill_pro_10],
        axis=1)
    return bill_pro