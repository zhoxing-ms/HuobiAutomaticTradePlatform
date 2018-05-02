import urllib
import urllib2
import json
import time
import sys
import json
import requests
from service.rest_api_service import get_balance, send_order, cancel_order, order_matchresults

#用户配置信息
url_buy = 'https://api-otc.huobi.pro/v1/otc/trade/list/public?coinId=1&tradeType=1&currentPage=1&payWay=&country='
url_sell = 'https://api-otc.huobi.pro/v1/otc/trade/list/public?coinId=1&tradeType=0&currentPage=1&payWay=&country='
url_order = 'https://api-otc.huobi.pro/v1/otc/order/submit'
url_get_order = 'https://api-otc.huobi.pro/v1/otc/order/confirm?order_ticket='
agent = 'User-Agent,Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0.2 Safari/604.4.7'
avg_data = []
#---------------------#
#防波动收购差价配置
d_price = 1200
#防做空收购数量境界
max_buy_num = 0.18
#爬虫定时/秒
t = 5
#输入用户cookie和token头的值
cookie = ''
token = ''
#---------------------#

#获取收售比特币的数据
def get_buy(url,headers):
   req = urllib2.Request(url)
   req.add_header("User-Agent",headers) 
   req.add_header("Host","api-otc.huobi.pro") 
   content = urllib2.urlopen(req)
   buy_data = content.read() 
   content.close()
   return buy_data


#将json格式化，得出最低价格
def json_data(jsondata):
   json_to_python = json.loads(jsondata)
   mindata_json = json_to_python['data'][0]
   new_min_json = json.dumps(mindata_json,ensure_ascii=False)
   new_min_data = json.loads(new_min_json)
   min_price = new_min_data['price']
   min_number = new_min_data['tradeCount']
   min_id = new_min_data['id']
   min_tradeNo = new_min_data['tradeNo']
   return min_price,min_number,min_id


#取出售商家参考平均值
def avg_sell(jsondata_sell):
   json_to_python = json.loads(jsondata_sell)
   for i in range(5):
      maxdata_json = json_to_python['data'][i]
      new_max_json = json.dumps(maxdata_json,ensure_ascii=False)
      new_max_data = json.loads(new_max_json)
      avg_data.append(new_max_data['price'])
   return (avg_data[0]+avg_data[1]+avg_data[2]+avg_data[3]+avg_data[4])//5


#get_ticket脚本
def get_ticket(buyNum,minBuy,tradeId):
   maxTradeLimit = buyNum * minBuy
   data = {'tradeId':tradeId,'amount':maxTradeLimit,'remark':''}
   req = urllib2.Request(url_order)
   req.add_header("User-Agent",agent)
   req.add_header("Host","api-otc.huobi.pro")
   req.add_header("token",token)
   req.add_header("Referer","https://otc.huobipro.com")
   req.add_header("Cookie",cookie)
   req.add_data(urllib.urlencode(data))
   content = urllib2.urlopen(req)
   order_data = content.read()
   content.close()
   json_to_python = json.loads(order_data)
   ticket_json = json_to_python['data']
   new_ticket_json = json.dumps(ticket_json,ensure_ascii=False)
   new_ticket = json.loads(new_ticket_json)
   try:
      ticket = new_ticket['ticket']
   except TypeError:
      ticket = 0
   return ticket


#下单脚本
def get_order(order_ticket):
   data = ''
   req = urllib2.Request(url_get_order+order_ticket)
   req.add_header("User-Agent",agent)
   req.add_header("Host","api-otc.huobi.pro")
   req.add_header("token",token)
   req.add_header("Referer","https://otc.huobipro.com")
   req.add_header("Cookie",cookie)
   req.add_data(urllib.urlencode(data))
   content = urllib2.urlopen(req)
   result_data = content.read()
   content.close()
   return result_data


#主逻辑与下单脚本
def btc_scan():
    buydata = get_buy(url_buy,agent)
    selldata = get_buy(url_sell,agent)
    minBuy,buyNum,tradeId = json_data(buydata)
    avgSell = avg_sell(selldata)
    if avgSell - minBuy > d_price:
       if buyNum < max_buy_num:
          ticket  = get_ticket(buyNum,minBuy,tradeId)
          if ticket != 0:
             order_result = get_order(ticket)
          else:
             order_result = 'error order'
          return '1','price differences:'+str(avgSell - minBuy),ticket,order_result
       else:
          return '2','count to much!',buyNum
    else:
       return 0,'waitting','min buy price:'+str(minBuy),'sell avg price:'+str(avgSell)


#定时执行
def timer(n):
   while True:
      print time.strftime('%X',time.localtime()),
      print btc_scan()
      time.sleep(n)
timer(t)

###
# 等待买入的币种(小写)
COIN1 = 'ela'
# 你想买进的COIN1的数量
COIN1_AMOUNT = 10
# 当COIN1的价格小于这个价位，程序允许买入，单位为COIN2
COIN1_PRICE = 0.00153
# 用来支付的币种，在USDT/BTC/ETH中间选择
COIN2 = 'btc'

def get_tote(coin):
    balance_dict = get_balance()
    token = {coin: 0}
    token_list = balance_dict['data']['list']
    for item in token_list:
        if item['currency'] == coin and item['type'] == 'trade':
            token[coin] = item['balance']
            break
    return token[coin]


def get_price(symbol):
    addr = 'https://api.huobi.pro/market/depth?symbol={symbol}&type=step0'
    resp_json = requests.get(addr.format(symbol=symbol)).text
    if '[]' not in resp_json:
        resp_dict = json.loads(resp_json)
        sell_price = resp_dict['tick']['asks'][0][0]
        return '%f' % sell_price
    else:
        return '0'


def buy_limit(coin1, coin2, coin1_max_price, coin1_amount):
    coin1_price = get_price(coin1 + coin2)
    if 0 < float(coin1_price) < coin1_max_price:
        resp_dict = send_order(amount=str(coin1_amount),
                               source='',
                               symbol=coin1 + coin2,
                               _type='buy-limit',
                               price=coin1_price)
        return resp_dict
    else:
        return {'status': 'err'}


def task():
    print('任务说明>> 我想用 {} 来买 {} '.format(COIN2, COIN1))
    print('钱包状况>> 我有 {} 个 {} '.format(get_tote(COIN2), COIN2))
    while True:
        resp_dict = buy_limit(COIN1, COIN2, COIN1_PRICE, COIN1_AMOUNT)
        if 'data' in resp_dict:
            order_id = resp_dict['data']
            print('当前进度>> 已下买单,订单ID为 {}'.format(order_id))
            if order_matchresults(order_id)['status'] != 'ok':
                print('订单追踪>> 未买到，取消订单...')
                cancel_order(order_id)
            else:
                print('订单追踪>> 已经买入，任务完成')
                break
        else:
            print('当前进度>> 暂未上币，或价格不符...')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        task()