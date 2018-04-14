import json
import numpy
import logging
import time
import datetime
import http.client
import statistics
from collections import deque
#TODO settings
#TODO ma

logger = logging.getLogger(__service__)

# 记录每种虚拟货币的每笔交易
transaction_dict = {}
# 记录每种虚拟货币在1分钟内的分析数据，队列长度设置为10，即10分钟内的数据
analyzed_queue_dict = {}
# 记录10分钟内的"价格"变化，这里的"价格"目前直接用close的差计算，以后考虑通过交易量，标准差等计算
price_change_dict = {}