# Django 計程車LINE Bot - 實作司機端及乘客端
### 系統簡介

本系統是專為高雄私家計程車團隊客製化的LINE聊天機器人，乘客端線上叫車、司機端接單及導航。

### 功能說明
- 乘客端 LINE Bot
  1. 於乘客端開啟LIFF叫車頁面
  2. 上車地點可透過輸入或GPS座標定位取得當前位置
  3. 顯示預估行程頁面
- 司機端 LINE Bot
  1. 司機帳號登入機制
  2. 登入後，點擊【上線接單】，LIFF頁面上線，並每隔50秒更新座標位置等待接單
  3. LINE對話處理，接單、結單
  4. LIFF導航功能(至指定定點)

### Demo
![image](https://github.com/clin92154/goddess.taxi/assets/57654809/46745eca-fb99-47cd-889a-ce10f55ebd4e)

### 使用技術
mult-threading、pandas 、Google App Engine部署、Django連線並建立Google Cloud SQL、Messaging＆LIFF實現LINE對話、Geolocation API接收座標
