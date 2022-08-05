# FTX_GridTrading

在FTX交易所上執行網格交易策略<br />
一開始先做市價交易(已公開)，後續為了避免手續費過高導致收益下降，使用限價交易(未公開)<br />
並配合質押 25FTT 獲得的 0% Maker Fee 來獲得更高的收益<br />

限價交易圖片 ( 時間 / 市場 / 價格 / 買賣 / 數量 / 交易流水號 / 成交形式 / 持倉數量 / 累計限價成交 / 累計市價成交 )
![image](https://github.com/tntrock/FTX_GridTrading/blob/main/TradingHistory.jpg)


# config.ini

|   名稱  | 數值 |
| ------ | ---- |
api_key | 填入FTX得到的API_KEY
api_secret | 填入FTX得到的API_SECRET
sub_account | 若使用子帳戶請填入子帳戶名稱
top_price | 網格交易的最高價格
ground_price | 網格交易的最低價格
step | 網格交易的格數
min_vol | 每格要交易的數量
check | 進入程式前是否要確認設定
