import ssl
import gzip
import uuid
import json
import time
import StringIO
import threading
from websocket import create_connection
from dao.mysql_connection import Mysql


sql = """INSERT INTO {} (id, open, close, low, high, amount, vol, count) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE open=%s, close=%s, low=%s, high=%s, amount=%s, vol=%s, count=%s"""

def save(item, symbol):
    conn = Mysql()
    print sql.format(symbol)
    conn.insertOne(sql.format(symbol),
           [item['id'], item['open'], item['close'], item['low'], item['high'], item['amount'],item['vol'], item['count'],
            item['open'], item['close'], item['low'], item['high'], item['amount'], item['vol'], item['count']])

def createConnection(tradeId, symbol):
    print '{}, {} create connection'.format(tradeId, symbol)
    try:
        ws = create_connection("wss://api.huobipro.com/ws", sslopt={"cert_reqs": ssl.CERT_NONE})
        tradeStr = '{{"id": "{}", "sub": "market.{}.kline.1min"}}'
        ws.send(tradeStr.format(tradeId, symbol))
        return ws
    except Exception, e:
        time.sleep(10)
        return createConnection(tradeId, symbol)

def main(symbol):
    tradeId = uuid.uuid1()
    ws = createConnection(tradeId, symbol)
    while True:
        try:
            compressData = ws.recv()
            compressedStream = StringIO.StringIO(compressData)
            gzipFile = gzip.GzipFile(fileobj=compressedStream)
            result = gzipFile.read()
            if result[:7] == '{"ping"':
                ts = result[8:21]
                pong = '{"pong":' + ts + '}'
                ws.send(pong)
            else:
                print(result)
                item = json.loads(result)
                if 'tick' in item:
                    item = item['tick']
                    save(item, symbol)

        except Exception as e:
            print('exception: {}'.format(e))
            ws = createConnection(tradeId, symbol)

def history(symbol):
    tradeId = uuid.uuid1()
    ws = createConnection()
    tradeStr = '{{"id": "{}", "req": "market.{}.kline.1min", "from": {}, "to": {}}}'
    start = 1511845180
    ws.send(tradeStr.format(tradeId, symbol, 1511845180, 1511845180+60*240))
    index = 1
    while True:
        try:
            compressData = ws.recv()
            compressedStream = StringIO.StringIO(compressData)
            gzipFile = gzip.GzipFile(fileobj=compressedStream)
            result = gzipFile.read()
            if result[:7] == '{"ping"':
                ts = result[8:21]
                pong = '{"pong":' + ts + '}'
                ws.send(pong)
                # ws.send(tradeStr.format(tradeId, symbol, start+60*240*index+1, start+60*240*(index+1)))
            else:
                item = json.loads(result)
                conn.insertOne(sql.format(symbol), [item['id'], item['open'], item['close'], item['low'], item['high'], item['amount'], item['vol'], item['count'],
                                     item['open'], item['close'], item['low'], item['high'], item['amount'], item['vol'], item['count']])
                # ws.send(tradeStr.format(tradeId, symbol, start+60*240*index+1, start+60*240*(index+1)))
            index += 1
            time.sleep(.5)
        except Exception as e:
            print('exception: {}'.format(e))
            ws = createConnection()

if __name__ == '__main__':
    thread_list = []
    symbols = ['btcusdt','bchusdt','ethusdt','etcusdt','ltcusdt','eosusdt','xrpusdt','omgusdt','dashusdt','zecusdt','adausdt','ctxcusdt','actusdt','btmusdt','btsusdt','ontusdt','iostusdt','htusdt','trxusdt','dtausdt','neousdt','qtumusdt','elausdt','venusdt','thetausdt','sntusdt','zilusdt','xemusdt','smtusdt','nasusdt','ruffusdt','hsrusdt','letusdt','mdsusdt','storjusdt','elfusdt','itcusdt','cvcusdt','gntusdt']

    for symbol in symbols:
        thread_list.append(threading.Thread(target=main, args=(symbol,)))
    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()