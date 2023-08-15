# Django modoule
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.template import loader
from urllib.parse import *

# LINEbot Moudle
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
from goddess_taxi_server.models import *
#對話樣板
from ChatTemplate.DriverServer import * 
from ChatTemplate.passengerServer import * 

d_bot_api = LineBotApi(settings.LINE_CHANNEL_DATA['DriverServer']['ACCESS_TOKEN'])
p_bot_api = LineBotApi(settings.LINE_CHANNEL_DATA['Develope_passenger_server']['ACCESS_TOKEN'])
parser = WebhookParser(settings.LINE_CHANNEL_DATA['Develope_passenger_server']['SECRET'])
gmaps_key=settings.GMAPS_KEY #googlemapapi

"""
乘客端
"""
@csrf_exempt #初始頁面
def booking(request): 
    """【我要叫車】初始頁面"""
    if request.method == 'POST':
        #取得訂單資料
        try:
            ride_request = RideRequest.objects.get(req_id=request.POST['reqid'])
            templates = loader.get_template(f'./book_ride.html') 
            context = {
                'req_id':ride_request.req_id
            }
        except Exception as err:
            return HttpResponse(err)
        return HttpResponse(templates.render(context))
    return render(request, f'./booking.html')



"""
LINE端
"""
@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        try:
            events = parser.parse(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            uid = event.source.user_id  # ID訊息
            try:
                if isinstance(event, MessageEvent):  #訊息事件
                    
                    if event.message.text in ["使用說明"]: #使用說明書
                        message = TextSendMessage(text=f"""請輸入您的手機號碼～\n***請勿加符號或空格***\n例：【0900123456】""")
                    elif event.message.text in ["客服中心"]: #聯絡客服
                        message = TextSendMessage(
                            text="【24小時客服專線】\n0900123456\n0901123456\n\n【其他服務】\n*代駕/跑腿/代購/旅遊包車*\n請加LINE好友：http://line.com/xxx")
                    elif "取消" in event.message.text:
                        """
                        1. 編號 + 取消
                        2. 取得編號後，判斷uid有無符合
                        3. 若有符合進行取消
                        4. 若沒符合則進行通知，找不到訂單
                        """

                        try:
                            req = event.message.text.split('/') #取消編號
                            ride_request =  RideRequest.objects.get(
                                req_id = req[1]
                            )
                            if str(ride_request.p_line_id) ==str(uid) and not(ride_request.is_canceled):  #判斷乘客身分  
                                message = TextSendMessage(text=f"通知乘客:訂單【{req[1]}】已被取消")
                                if ride_request.to_rsv: #若已經成立訂單
                                    rsv = RideRSV.objects.get(req_id=req[1]) 
                                    if rsv.closed_at!=None: #已經結單 -> 通知
                                        message = TextSendMessage(text=f"訂單【{req[1]}】已結單。")
                                    else:  #未結單 -> 通知 司機、乘客
                                        message = TextSendMessage(text=f"通知司機:訂單【{req[1]}】已被取消")
                                        driver = Driver.objects.get(current_rsv=str(ride_request))
                                        driver.current_rsv = None #司機訂單取消
                                        driver.save()
                                        rsv.delete()
                                        d_bot_api.push_message(rsv.d_line_id,message)
                                ride_request.to_rsv = False
                                ride_request.is_canceled = True
                                ride_request.current_driver_id = ''
                                ride_request.save()
                            elif ride_request.is_canceled:
                                message = TextSendMessage(text=f"訂單【{req[1]}】已取消。")
                        except Exception as err:
                            message = TextSendMessage(text=f"錯誤發生{err}")
                    else:
                        message = TextSendMessage(text=f"""如需叫車請點選下方功能列的"我要叫車"，如需代駕、代購....等請點選聯繫客服，將會有專人為您服務""")

                p_bot_api.reply_message(event.reply_token, message)  # time.sleep(10)
            except:
                break
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
    
