import configparser
import datetime
import ccxt
from colorama import init, Fore, Back
from time import sleep

init(autoreset=True)


'''------------------ User Setting ------------------'''

cf = configparser.ConfigParser()
cf.read('config.ini')
api_test_apiKey = str(cf.get('user', 'api_key'))
api_test_secret = str(cf.get('user', 'api_secret'))
subaccount = str(cf.get('user', 'sub_account'))

symbol = 'BTC-PERP'

'''--------------------------------------------------'''



ftx_exchange = ccxt.ftx({
    'headers': {
        'FTX-SUBACCOUNT': subaccount,
    },
    'apiKey': api_test_apiKey,
    'secret': api_test_secret,
    'enableRateLimit': True
})

print('交易所名稱:', ftx_exchange.name)
print('訪問頻率限制:', ftx_exchange.rateLimit, 'ms')
print('交易所時間(GMT+8):', ftx_exchange.iso8601(ftx_exchange.milliseconds() + (8 * 60 * 60 * 1000)))

while(True):
    # 網格設定
    try:
        top_price = int(cf.get('user', 'top_price'))
    except:
        top_price = int(input('請輸入頂價: '))
    try:
        ground_price = int(cf.get('user', 'ground_price'))
    except:
        ground_price = int(input('請輸入底價: '))
    try:
        set_step = int(cf.get('user', 'step'))
    except:
        set_step = int(input('請輸入網格數量: '))
        
    vol_limit = float(ftx_exchange.fetch_ticker(symbol)['info']['sizeIncrement'])
    try:
        min_vol = float(cf.get('user', 'min_vol'))
        if(min_vol < vol_limit): min_vol = vol_limit
    except:
        min_vol = float(input('請輸入每格下單金額,最小值為: ' + str(vol_limit) + str(symbol)))
        if(min_vol < vol_limit): min_vol = vol_limit

    # 計算網格價格
    arithmetic_d = (top_price - ground_price) / (set_step - 1)
    price_list = []
    price_list.append(ground_price)

    while(price_list[-1] < top_price):
        price_list.append(price_list[-1] + arithmetic_d)
        
    if(price_list[-1] > (top_price + 1)):
        price_list.remove(price_list[-1])

    price_list = list(map(int, price_list))  # 將 list 內所有數字轉換成 int
    price_set = set(price_list)

    if((set_step == len(price_list)) and (len(price_set) == len(price_list))):  # 確認網格數量正確
        print('網格設定完成')
        print('價格設定:等差', '頂價為:', top_price, '底價為:', ground_price, '網格設定為:', len(price_list), '格', '每隔間距為:', int(arithmetic_d))
        
        try:
            check = cf.get('user', 'check')
            if(check == 'True'): check = True
            elif(check == 'False'): check = False
            else: check = True
            if(check): sum_vol = float(input('目前持倉總量(若無請填0): '))
            else: sum_vol = 0
        except:
            sum_vol = float(input('目前持倉總量(若無請填0): '))

        while(True):
            start_confirm = str(input('輸入 Y/y 開始執行網格, 輸入其他值重新設定網格: '))
            if(start_confirm == 'Y'):
                start_confirm = True
                break
            elif(start_confirm == 'y'):
                start_confirm = True
                break
            else:
                print('輸入錯誤,取消執行')
                start_confirm = False
                top_price = int(input('請輸入頂價: '))
                ground_price = int(input('請輸入底價: '))
                set_step = int(input('請輸入網格數量: '))
                min_vol = float(input('請輸入每格下單金額(BTC),最小值為0.001BTC: '))
                if(min_vol < 0.001): min_vol = 0.001
                sum_vol = float(input('目前持倉總量(若無請填0): '))
        break
    else:
        print('系統錯誤(網格)')
        price_list = []

while(True):
    ticker_data = ftx_exchange.fetch_ticker(symbol)
    now_price = int(ticker_data['close'])

    if(price_list.count(now_price) == 0):
        price_list.append(now_price)
        price_list.sort()
        index = price_list.index(now_price)
        price_list.remove(price_list[index])
        up_price = price_list[index + 1]
        up_index = price_list.index(up_price)
        down_price = price_list[index - 1]
        down_index = price_list.index(down_price)
        break
    if(price_list.count(now_price) == 1):
        index = price_list.index(now_price)
        up_price = price_list[index + 1]
        up_index = price_list.index(up_price)
        down_price = price_list[index - 1]
        down_index = price_list.index(down_price)
        break


my_order_book = []
sum_vol = round(sum_vol, 7)
vol = 0

while(start_confirm):
    try:
        t = ftx_exchange.iso8601(ftx_exchange.milliseconds() + (8 * 60 * 60 * 1000))
        ticker_data = ftx_exchange.fetch_ticker(symbol)
        now_price = int(ticker_data['close'])

        if(sum_vol >= min_vol):
            up_price = price_list[up_index]
            down_price = price_list[down_index]
            if(now_price >= up_price):
                ftx_exchange.create_order(symbol=symbol, side='sell', type='market', amount=min_vol)
                sum_vol -= min_vol
                vol += min_vol
                up_index += 1
                down_index += 1
                sum_vol = round(sum_vol, 7)
                vol = round(vol, 7)
                t = ftx_exchange.iso8601(ftx_exchange.milliseconds() + (8 * 60 * 60 * 1000))
                print('[', (Fore.GREEN + 'INFO'), '] ', '[', (Fore.MAGENTA + str(t)), ']', '[', (Fore.GREEN + '上漲超過'), (Fore.GREEN + str(up_price)), ']', (Fore.YELLOW + str(now_price)), '市價單賣出', '下一觸發價格', (Fore.GREEN + str(price_list[up_index])), (Fore.RED + str(price_list[down_index])), ' 目前持倉:', (Back.CYAN + str('%.3f' % sum_vol)), '總交易量:', (Back.CYAN + str('%.3f' % vol)))
            if(now_price <= down_price):
                ftx_exchange.create_order(symbol=symbol, side='buy', type='market', amount=min_vol)
                sum_vol += min_vol
                vol += min_vol
                up_index -= 1
                down_index -= 1
                sum_vol = round(sum_vol, 7)
                vol = round(vol, 7)
                t = ftx_exchange.iso8601(ftx_exchange.milliseconds() + (8 * 60 * 60 * 1000))
                print('[', (Fore.GREEN + 'INFO'), '] ', '[', (Fore.MAGENTA + str(t)), ']', '[', (Fore.RED + '下跌超過'), (Fore.RED + str(down_price)), ']', (Fore.YELLOW + str(now_price)), '市價單買入', '下一觸發價格', (Fore.GREEN + str(price_list[up_index])), (Fore.RED + str(price_list[down_index])), ' 目前持倉:', (Back.CYAN + str('%.3f' % sum_vol)), '總交易量:', (Back.CYAN + str('%.3f' % vol)))
        
        if(sum_vol == 0):
            up_price = price_list[up_index]
            down_price = price_list[down_index]
            ftx_exchange.create_order(symbol=symbol, side='buy', type='limit', price=down_price, amount=min_vol)
            open_order = ftx_exchange.fetch_open_orders(symbol)
            for order in open_order:
                if((order['info']['side'] == 'buy') or (order['info']['type'] == 'limit')):
                    my_order_book.append([order['info']['id'], order['info']['side'], order['info']['price']])
                    t = ftx_exchange.iso8601(ftx_exchange.milliseconds() + (8 * 60 * 60 * 1000))
                    print('[', (Fore.GREEN + 'INFO'), '] ', '[', (Fore.MAGENTA + str(t)), ']', order['info']['market'], order['info']['type'], '已掛單, ID:', (Fore.YELLOW + order['info']['id']), order['info']['side'], '價格:', order['info']['price'], '大小:', order['info']['size'] )
                    order_id = order['info']['id']
                else:
                    print('[', (Fore.YELLOW + 'WARNING'), '] ', '[', (Fore.MAGENTA + str(t)), ']', '掛單程序執行錯誤,檢測到非為buy或是limit,將會自動修正重新掛單', order['info']['market'], order['info']['type'], '已掛單, ID:', (Fore.YELLOW + order['info']['id']), order['info']['side'], '價格:', order['info']['price'], '大小:', order['info']['size'])
            while(True):
                ticker_data = ftx_exchange.fetch_ticker(symbol)
                now_price = int(ticker_data['close'])
                up_price = price_list[up_index]
                down_price = price_list[down_index]

                if(now_price >= up_price):
                    up_index += 1
                    down_index += 1
                    t = ftx_exchange.iso8601(ftx_exchange.milliseconds() + (8 * 60 * 60 * 1000))
                    print('[', (Fore.GREEN + 'INFO'), '] ', '[', (Fore.MAGENTA + str(t)), ']', (Fore.CYAN + '因價格上升至'), (Fore.YELLOW + str(up_price)), (Fore.CYAN + '已刪改訂單'))
                    ftx_exchange.cancel_all_orders(symbol)
                    my_order_book = []

                    ftx_exchange.create_order(symbol=symbol, side='buy', type='limit', price=price_list[down_index], amount=min_vol)
                    
                    open_order = ftx_exchange.fetch_open_orders(symbol)
                    for order in open_order:
                        if((order['info']['side'] == 'buy') or (order['info']['type'] == 'limit')):
                            my_order_book.append([order['info']['id'], order['info']['side'], order['info']['price']])
                            t = ftx_exchange.iso8601(ftx_exchange.milliseconds() + (8 * 60 * 60 * 1000))
                            print('[', (Fore.GREEN + 'INFO'), '] ', '[', (Fore.MAGENTA + str(t)), ']', order['info']['market'], order['info']['type'], '已掛單, ID:', (Fore.YELLOW + order['info']['id']), order['info']['side'], '價格:', order['info']['price'], '大小:', order['info']['size'] )
                            order_id = order['info']['id']
                        else:
                            print('[', (Fore.YELLOW + 'WARNING'), '] ', '[', (Fore.MAGENTA + str(t)), ']', '掛單程序執行錯誤,檢測到非為buy或是limit,將會自動修正重新掛單', order['info']['market'], order['info']['type'], '已掛單, ID:', (Fore.YELLOW + order['info']['id']), order['info']['side'], '價格:', order['info']['price'], '大小:', order['info']['size'])

                fill = ftx_exchange.fetch_order(order_id, symbol)['filled']
                if(fill > 0):
                    if(fill == min_vol):
                        sum_vol += min_vol
                        vol += min_vol
                        up_index -= 1
                        down_index -= 1
                        sum_vol = round(sum_vol, 7)
                        vol = round(vol, 7)
                        t = ftx_exchange.iso8601(ftx_exchange.milliseconds() + (8 * 60 * 60 * 1000))
                        print('[', (Fore.GREEN + 'INFO'), '] ', '[', (Fore.MAGENTA + str(t)), ']', (Fore.YELLOW + str(order_id)), '已完全成交', '下一觸發價格', (Fore.GREEN + str(price_list[up_index])), (Fore.RED + str(price_list[down_index])), ' 目前持倉:', (Back.CYAN + str('%.3f' % sum_vol)), '總交易量:', (Back.CYAN + str('%.3f' % vol)))
                        break
                    if(fill < min_vol):
                        ftx_exchange.cancel_order(order_id, symbol)
                        fill = ftx_exchange.fetch_order(order_id, symbol)['filled']
                        ftx_exchange.create_order(symbol=symbol, side='buy', type='market', amount=(min_vol - fill))
                        sum_vol += min_vol
                        vol += min_vol
                        up_index -= 1
                        down_index -= 1
                        sum_vol = round(sum_vol, 7)
                        vol = round(vol, 7)
                        t = ftx_exchange.iso8601(ftx_exchange.milliseconds() + (8 * 60 * 60 * 1000))
                        print('[', (Fore.GREEN + 'INFO'), '] ', '[', (Fore.MAGENTA + str(t)), ']', (Fore.YELLOW + str(order_id)), '部分成交', (Fore.CYAN + str(fill)), '不足部分', (Fore.CYAN + str(min_vol - fill)), '使用市價單補齊', '下一觸發價格', (Fore.GREEN + str(price_list[up_index])), (Fore.RED + str(price_list[down_index])), ' 目前持倉:', (Back.CYAN + str('%.3f' % sum_vol)), '總交易量:', (Back.CYAN + str('%.3f' % vol)))
                        break
        
        if((now_price > top_price) or (now_price < ground_price)):
            ftx_exchange.create_order(symbol=symbol, side='sell', type='market', amount=sum_vol)
            vol += sum_vol
            sum_vol -= sum_vol
            sum_vol = round(sum_vol, 7)
            vol = round(vol, 7)
            t = ftx_exchange.iso8601(ftx_exchange.milliseconds() + (8 * 60 * 60 * 1000))
            print('[', (Fore.YELLOW + 'WARNING'), '] ', '[', (Fore.MAGENTA + str(t)), ']', '目前價格', (Fore.YELLOW + str(now_price)), '已超出網格範圍,啟動自動平倉', ' 目前持倉:', (Back.CYAN + str('%.3f' % sum_vol)), '總交易量:', (Back.CYAN + str('%.3f' % vol)))
            break
    
    except ccxt.BaseError as Error:
        t = datetime.datetime.now().isoformat()
        print('[', (Fore.RED + 'ERROR'), '] ', '[', (Fore.MAGENTA + (t[0:len(t) - 3] + 'Z')), ']', str(Error), '將於 1 秒後重試')
        sleep(1)
        try:
            t = ftx_exchange.iso8601(ftx_exchange.milliseconds() + (8 * 60 * 60 * 1000))
            print('[', (Fore.GREEN + 'INFO'), '] ', '[', (Fore.MAGENTA + str(t)), ']', '與交易所', ftx_exchange.name, '連線成功')
        except ccxt.BaseError as Error:
            t = datetime.datetime.now().isoformat()
            print('[', (Fore.RED + 'ERROR'), '] ', '[', (Fore.MAGENTA + (t[0:len(t) - 3] + 'Z')), ']', str(Error), '將於 1 秒後重試')
            sleep(1)
        continue
