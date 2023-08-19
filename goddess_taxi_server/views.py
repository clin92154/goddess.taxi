from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.template import loader
from urllib.parse import *
from django.utils import timezone
from .models import * #資料庫
import threading , time , json  #多核心
import pandas as pd #pandas
from geopy.distance import geodesic #距離
import requests
from django.db.models import Q 
from django.core.exceptions import ObjectDoesNotExist

import requests
import json
import math


# LINEbot Moudle
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import *
from linebot.models import *
#對話樣板
from ChatTemplate.DriverServer import * 
from ChatTemplate.passengerServer import * 


from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.hashers import make_password, check_password

# from ChatTemplate.passengerServer import * 
# Create your views here.
d_bot_api = LineBotApi(settings.LINE_CHANNEL_DATA['DriverServer']['ACCESS_TOKEN'])
parser = WebhookParser(settings.LINE_CHANNEL_DATA['DriverServer']['SECRET'])
gmaps_key=settings.GMAPS_KEY #googlemapapi

#passenger.use_server                                    


"""
乘客端
"""
@csrf_exempt
def booking_init(request):
    """【我要叫車】初始頁面"""
    try:
        if request.method == 'POST':
            # 取得訂單資料
            """
            1. 司機正在上線
            2. 司機正在接單
            3. 乘客目前有訂單未完成
            4. 乘客已經呼叫訂單，而訂單還沒正式成立或是被取消
            """
            # 司機正在接單
            """
            terms = [
                RideRequest.objects.filter(p_line_id=request.POST['user_id'], is_canceled=False, to_rsv=False, is_sent=True),
                RideRSV.objects.filter(p_line_id=request.POST['user_id'], closed_at=None)
            ]
            # 如果任一條件符合
            for term in terms:
                if term:
                    return JsonResponse({'is_pass': False,'status':'term'})
            """
            phone = ''
            try:
                phone = Passengers.objects.get(p_line_id=request.POST['user_id']).passenger_hp
            except:
                print("User's phonenumber Not Found")
                pass
            

            return JsonResponse({'is_pass': True, 'ph_n': phone})


    except Exception as e:
        print("初始化錯誤:", str(e))
        return JsonResponse({'is_pass': False,'status':'exception'})

@csrf_exempt  #建立佔存訂單
def create_request(request): 
    if request.method == 'POST':
        
        decode_data = unquote_plus(request.body.decode('utf-8'))
        decode_data = parse_qs(decode_data)
        ride_data = {
            'user_id': decode_data['user_id'][0],
            'departing': json.dumps({
                'name': decode_data['departing[name]'][0],
                'lati_NS': decode_data['departing[lati_NS]'][0],
                'longi_EW':decode_data['departing[longi_EW]'][0],
            }),
            
        }
       
        if 'arriving[name]' in decode_data:
            ride_data['arriving'] = json.dumps({
                'name': decode_data['arriving[name]'][0],
                'lati_NS':decode_data['arriving[lati_NS]'][0],
                'longi_EW': decode_data['arriving[longi_EW]'][0],
            })
        if 'memo' in decode_data:
            ride_data['remarks'] = decode_data['memo'][0]
        

            # 创建 Passengers 对象
        passenger, created = Passengers.objects.get_or_create(
            p_line_id= ride_data['user_id'],
        )
        if 'phone' in decode_data:
            ride_data['phone'] = decode_data['phone'][0]
            passenger.passenger_hp = ride_data['phone']
        if 'name' in decode_data:
            passenger.name = decode_data['name'][0]

        passenger.use_server = decode_data['use_server'][0]
        passenger.save()

        try: #建立訂單
            ride_request =  RideRequest.objects.create(
                p_line_id=passenger,
                departing=ride_data['departing'],
            )
            if 'arriving' in ride_data :
                ride_request.arriving=ride_data['arriving']
                ride_request.save()
            if 'remarks' in ride_data:
                ride_request.remarks = ride_data['remarks']
                ride_request.save()
            
        except Exception as err :
            return HttpResponse("訂單設定錯誤，請關閉頁面並重新叫車\n【Error】")

        if ride_request.arriving != None:
            templates = loader.get_template('passenger/map_preview.html')
            context = {'order':ride_request.req_id,
                            'pickup':json.loads(ride_request.departing)['name'] ,
                            'dropoff':json.loads(ride_request.arriving)['name'],
                            'memo':ride_request.remarks,
                            'user_id': ride_request.p_line_id,}
        else:
            templates = loader.get_template('passenger/ready_for_sent.html')
            context = {'order':ride_request.req_id,
                'pickup':json.loads(ride_request.departing)['name'] ,
                'memo':ride_request.remarks,
                'user_id': ride_request.p_line_id,}
        return HttpResponse(templates.render(context))


@csrf_exempt 
def delete_request(request):

    if request.method == 'POST':
        RideRequest.objects.filter(req_id=request.POST['req_id']).delete()
        return JsonResponse({'req_id':request.POST['req_id'],'delete': True})



@csrf_exempt #預估行程
def estimate_request(request): 
    """預估車費及顯示路徑"""
    if request.method == 'POST':  
        context = {
                'pickup':request.POST['pick-up'],
                'dropoff':request.POST['drop-off'],
                }
                
        return render(request, 'passenger/estimate_result.html',context)
    
    return render(request, 'passenger/fare_estimate.html')



@csrf_exempt #取消訂單
def cancel_request(request):
    if request.method == 'POST':  
        try:
            ride_request =  RideRequest.objects.get(
                req_id= request.POST['reqid']
            )
            ride_request.current_driver =''
            ride_request.is_canceled = True
            ride_request.save()
            passenger = Passengers.objects.get(p_line_id = ride_request.p_line_id ).use_server
            p_bot_api = LineBotApi(settings.LINE_CHANNEL_DATA[passenger]['ACCESS_TOKEN'])
            
            message = TextSendMessage(text=f"訂單【{request.POST['reqid']}】已取消。")
            p_bot_api.push_message(f"{ride_request.p_line_id}", message)
            if RideRSV.objects.filter(req_id=request.POST['reqid']):
                message = TextSendMessage(text=f"訂單【{request.POST['reqid']}】已被取消。")
                rsv = RideRSV.objects.get(req_id=request.POST['reqid'])
                driver = Driver.objects.get(d_line_id=rsv.d_line_id)
                driver.current_rsv = None
                driver.save()
                d_bot_api.push_message(f"{rsv.d_line_id}", message)

            return JsonResponse({'status': True})
        except error:
            print(f'訂單【{request.POST["req_id"]}】取消錯誤',error)
            return JsonResponse({'status': error})


@csrf_exempt #送出派單
def process_request(request): 
    """進行派單通知及尋找司機"""
    try:
        if request.method == 'POST': 
            try:
                #1.取得訂單編號
                req =  RideRequest.objects.get(
                    req_id= request.POST['req_id']
                )
                lineOfReqEvent = threading.Thread(target=dispatch_ride_request,args=(req.req_id,)) #進行該派單流程
                lineOfReqEvent.daemon = True #進行該派單流程
                lineOfReqEvent.start()
                req.is_sent = True
                req.save()
                #呼叫派單
                return JsonResponse({'status': True})
            except error:
                print(f'訂單【{request.POST["req_id"]}】寄出錯誤',error)
                return JsonResponse({'status': error})
    except error:
        return JsonResponse({'status': error})


#派單流程
def dispatch_ride_request(req):
    """針對該乘客進行派單"""
    #step 1 : 通知乘客
    time.sleep(6)  # 使用 asyncio.sleep() 進行非同步等待

    if RideRequest.objects.get(req_id=req).is_canceled: #如果取消訂單
        return;
    message = TextSendMessage(text=f"#{req},正在為您尋找附近司機，\n感謝您的耐心等待…\n\n若您要取消叫車，\n請直接輸入「取消/訂單編號」～\n（如：取消/104）")
    try:
        passenger = RideRequest.objects.get(req_id=req).p_line_id
        p_bot_api = LineBotApi(settings.LINE_CHANNEL_DATA[passenger.use_server]['ACCESS_TOKEN'])
        p_bot_api.push_message(f'{passenger}', message)
    except:
        print(f"乘客派單:{req}錯誤，取得不到資料")
        return;
    #step 2 : 載入上車地點
    try:
        ride_request_departing = json.loads(RideRequest.objects.get(req_id=req).departing) #取得乘客上車的地點
    except:
        print(f"乘客派單:{req}錯誤，取得不到上車資料")
        return;
    #step 3 : 利用迴圈開始找尋訂單
    """
    需要考量情況取消訂單
    1. 訂單有無在時間內被取消
    2. 附近能否找到司機
    3. 以目前上線清單司機都拒接(可以改成，一次做完，抓取第二次上線司機清單)
    """
    #非已經成立而且沒被取消
    while not(RideRequest.objects.get(req_id=req).to_rsv) and not(RideRequest.objects.get(req_id=req).is_canceled): #當訂單尚未成立時
        if RideRequest.objects.get(req_id=req).is_canceled :
            return;
        try:
            ride_request =  RideRequest.objects.get(req_id=req)
            # 找出所有 online 司機，但是currentlocation is not null，並且沒有單
            online_drivers = Driver.objects.filter(is_online=True,current_location__isnull=False,current_rsv__isnull=True)
            distances = [] #存司機跟上車地點的距離

            if online_drivers : #如果有上線司機的話
                for driver in online_drivers:
                        current_location_dict = json.loads(driver.current_location)   #找司機目前的位置
                        #經緯度
                        lati_NS , longi_EW= float(current_location_dict['lati_NS']) , float(current_location_dict['longi_EW'])
                        # 計算每個司機與 ride_request 的距離後存進distances
                        distance = geodesic((float(ride_request_departing['lati_NS']), float(ride_request_departing['longi_EW'])),
                                        (float(lati_NS),float(longi_EW))).meters
                        
                        #列出該司機所屬的所有車隊
                        dv_group = list(driver.driver_group.all().values_list('group_id', flat=True))
                        distances.append({'driver_id': driver.id,
                                        'driver_group':dv_group,
                                        'distance': distance})
            else: #沒有司機，重新設定
                try:
                    #判斷是否被取消，如果沒有則設定取消
                    if not(RideRequest.objects.get(req_id=ride_request.req_id).is_canceled) :
            
                        passenger = RideRequest.objects.get(req_id=ride_request.req_id).p_line_id
                        message = TextSendMessage(text=f"目前無上線司機，訂單【{req}】已被取消，請稍後再試。")
                        ride_request.is_canceled = True
                        ride_request.current_driver=""
                        ride_request.save()
                        p_bot_api.push_message(f"{passenger}", message)
                        return;
                except Exception as err:
                    print(err)

            if len(distances) == 0 :
                continue
            # 將 distances 轉換為 DataFrame，並計算優先權 priority
            df = pd.DataFrame(distances)
            def get_min_priority(row):
                #車隊接單的優先權
                driver_group_priorities = [DriverGroup.objects.get(group_id=gid).priority for gid in row['driver_group']]
                min_priority = min(driver_group_priorities) #找出最小的優先權
                priority = min_priority + row['distance'] # 直線距離 + 所屬車隊優先權
                min_priority_group = row['driver_group'][driver_group_priorities.index(min_priority)] 
                return (priority, min_priority_group)            
            df[['priority', 'min_priority_group']] = df.apply(lambda row: pd.Series(get_min_priority(row)), axis=1)
            # 根據 priority 進行排序
            df = df.sort_values(by=['priority'], ascending=True)
            print(df)
            
            for i in range(len(df)): #依序目前名單找尋訂單

                min_priority_group = df['min_priority_group'].iloc[i]   # 根據 priority 進行排序       
                driver_id = df['driver_id'].iloc[i]# 取得最優先的司機driver_id
                if Driver.objects.get(id=driver_id).current_rsv == None and Driver.objects.get(id=driver_id).is_online :
                    dv_cg = Driver.objects.get(id=driver_id) 
                    dv_cg.current_group = DriverGroup.objects.get(group_id=min_priority_group).driver_group  #更改服務車隊
                    dv_cg.save()
                    ride_request.current_driver = driver_id#暫存儲存給司機，也避免目前有單時給他
                    ride_request.save()
                    message = waitOrder(ride_request)
                    driver = Driver.objects.get(id=driver_id ).d_line_id
                    d_bot_api.push_message(driver, message)
                else:
                    continue

                # 等待一段時間，處理其他訂單，看司機是否接單
                for i in range(1,61):
                    time.sleep(1)  # 使用 asyncio.sleep() 進行非同步等待
                    ride_request = RideRequest.objects.get(req_id=ride_request.req_id)
                    if ride_request.to_rsv:
                        ride_request.current_driver = ""
                        ride_request.save()
                        return;
                        
            if not(ride_request.to_rsv):
                passenger = RideRequest.objects.get(req_id=ride_request.req_id).p_line_id
                message = TextSendMessage(text=f"目前無司機接單，訂單【{req}】已被取消，請稍後再試。")
                ride_request.current_driver=""
                ride_request.is_canceled = True
                ride_request.save()
                p_bot_api.push_message(f"{passenger}", message)
                return;

            time.sleep(5)
        except Exception as error:

            print(error,"取消訂單")
            break
        finally:
            ride_request =  RideRequest.objects.get(req_id=req)



"""
司機端
"""
@csrf_exempt #司機驗證
def driverlogin(request):
    """司機驗證"""
    if request.method == 'POST':
        phone_number = request.POST['phone']
        if Driver.objects.filter(driver_hp=phone_number):
            driver = Driver.objects.filter(driver_hp=phone_number)
            if check_password(request.POST['pwd'],driver[0].password):
                driver.update(d_line_id = request.POST['user_id'],name=request.POST['displayName'])
                return JsonResponse({'status': True})
            else:
                return JsonResponse({'status': False})
        else:
            return JsonResponse({'status': "not exist"})
    return render(request, 'confirm/confirm.html')


@csrf_exempt #上線接單
def waitorder(request):
    if request.method == 'POST':

        terms = [
            Driver.objects.filter(d_line_id=request.POST['uid'],current_rsv__isnull=False),  
            RideRSV.objects.filter(d_line_id=request.POST['uid'],closed_at=None), 
        ]

        driver = Driver.objects.get(d_line_id=request.POST['uid'])

        if request.POST['status'] == 'init': 
            for term in terms:
                if term : return JsonResponse({'status': False,'log':"目前有其他訂單進行中"}) 
            driver.is_online = True
            driver.save()
        elif request.POST['status'] == "end":
            driver.is_online = False
            driver.last_online = timezone.now()
            driver.current_location = None
            driver.save()
            message = TextSendMessage(text=f"已結束等待，若欲接單則重新上線。")
            d_bot_api.push_message(driver.d_line_id, message)
        return JsonResponse({'status': True})
    return render(request, 'driver_tools/online_waiting.html')

def updateLocation(request):   #改成存location
    """司機更新目前位置"""
    if request.method == 'POST':
        #更新目前的位置

        current_location = {
            'lati_NS':request.POST['lati_NS'] ,
            'longi_EW':request.POST['longi_EW'],
        }

        driver = Driver.objects.get(d_line_id=request.POST['uid'])
        if 'status' in request.POST:
            driver.is_online = False
            driver.save()
            return JsonResponse({'status': True})
        print(driver.id)

        if RideRequest.objects.filter(current_driver =driver.id):
            driver.is_online = False
            driver.save()
            return JsonResponse({'status': True})

        # print(current_location)
        driver.current_location = json.dumps(current_location) #打包至Json並更新司機目前位置
        driver.is_online = True
        driver.save()
        #沒有條件讓司機關閉網頁
        #如果有DriverID在訂單內時，關閉網頁
        
    return JsonResponse({'status': False})

#尚無定單
def none_ride_request(request):
    if request.method == 'POST':
        driver = Driver.objects.get(d_line_id=request.POST['uid'])
        driver.is_online = False
        driver.current_location = None
        driver.save()
        message = TextSendMessage(text="""目前沒有乘客叫車，請重新等待接單""")
        d_bot_api.push_message(driver.d_line_id, message)
        return JsonResponse({'status': True})


def  NotifyArrived(rsv,driver,passenger):
    p_bot_api = LineBotApi(settings.LINE_CHANNEL_DATA[passenger]['ACCESS_TOKEN'])
    p_bot_api.push_message(rsv.p_line_id,TextSendMessage(f"""
訂單【{driver.current_rsv}】
車車抵達囉♥
隨時都可以準備上車呦～
(記得確認車牌號碼再上車)

⚠️提醒您，司機抵達上車地點等候5分鐘即開始跳錶等候；預約車輛時間到即開始跳錶。

⚠️若車輛抵達取消訂單，並酌收100元起取消費，煩請貴賓盡快上車唷。

⚠️若車輛抵達15分鐘後上車，需酌收等待費100元，煩請儘速上車。

⚠️提醒您下車時記得隨身物品

⚠️司機若有私下索取您的聯絡方式，歡迎跟我們回報告知，謝謝🙏"""))
    

"""
導航
"""


@csrf_exempt #查無訂單
def go_arriving(request):
    if request.method == 'POST':
        driver = Driver.objects.get(d_line_id=request.POST['uid'])

        if request.POST['status'] == 'init':
            rsv = RideRSV.objects.get(req_id=driver.current_rsv)

            base_fare = DriverGroup.objects.get(driver_group=rsv.driver_group).base_fare
            start_at = rsv.confirmed_at #紀錄開始時間
            #乘客通知計費
            Passenger_message = TextSendMessage(text="""司機已開始進行跳表計費，祝您旅途平安～""")
            passenger = Passengers.objects.get(p_line_id=rsv.p_line_id).use_server
            p_bot_api = LineBotApi(settings.LINE_CHANNEL_DATA[passenger]['ACCESS_TOKEN'])
            p_bot_api.push_message(rsv.p_line_id, Passenger_message)
            if rsv.arriving != None:
                arriving_location = tuple(map(float,(json.loads(rsv.arriving)['lati_NS'], json.loads(rsv.arriving)['longi_EW']))) # New York, NY
                return JsonResponse({'status':'go_arriving','location_name':json.loads(rsv.arriving)['name'],'base_fare':base_fare,'arriving_location':{'lat': arriving_location[0], 'lng':arriving_location[1]},"start_at":start_at})           
            return JsonResponse({'status':'go_arriving',"start_at":start_at})           
        elif request.POST['status'] == 'go_arriving': 
            print('go_arrving')
            decode_data = unquote_plus(request.body.decode('utf-8'))
            decode_data = parse_qs(decode_data)
            rsv = RideRSV.objects.get(req_id=driver.current_rsv)
            try:
                if math.isnan(int(request.POST['final_fare'])):
                    rsv.travel_fare = 100;
                else:
                    rsv.travel_fare = request.POST['final_fare'];
            except:
                rsv.travel_fare = 100;

            rsv.travel_distance = request.POST['final_distance']
            rsv.travel_time = request.POST['final_time']
            rsv.arriving = json.dumps({
                'name': decode_data['arriving[name]'][0],
                'lati_NS':decode_data['arriving[lati_NS]'][0],
                'longi_EW': decode_data['arriving[longi_EW]'][0],
            })
            rsv.departing= json.dumps({
                'name': decode_data['departing[name]'][0],
                'lati_NS':decode_data['departing[lati_NS]'][0],
                'longi_EW': decode_data['departing[longi_EW]'][0],
            })
            
            print(rsv.departing)
            print(request.POST['route_map'])
            rsv.route_map = str(request.POST['route_map'])
            
            rsv.closed_at = timezone.now() 
            rsv.save()
            return JsonResponse({'status':'end_arriving'})
    return render(request, 'driver_tools/navigate2end.html')
            
@csrf_exempt #查無訂單
def go_departing(request):
    if request.method == 'POST':
        driver = Driver.objects.get(d_line_id=request.POST['uid'])
        print(request.POST['status'] , driver.current_rsv )
        if request.POST['status'] == 'init':

            rsv = RideRSV.objects.get(req_id=driver.current_rsv)
            departing_location = tuple(map(float,(json.loads(rsv.departing)['lati_NS'], json.loads(rsv.departing)['longi_EW']))) # New York, N
            print(departing_location)
            print(json.loads(rsv.departing)['name'])
            return JsonResponse({'status':'go_departing','location_name':json.loads(rsv.departing)['name'],'arriving_location':{'lat': departing_location[0], 'lng':departing_location[1]}})
        elif request.POST['status'] == 'go_departing':
            if driver.current_rsv != None:
                rsv = RideRSV.objects.get(req_id=driver.current_rsv)
                message = [ComfirmOrder(str(rsv)),StartCalcular(rsv)]
                passenger = Passengers.objects.get(p_line_id=rsv.p_line_id).use_server
                NotifyArrived(rsv,driver,passenger) #通知乘客
            else:
                message = TextSendMessage(text=f"目前訂單已被取消或成立，請重新確認")
            d_bot_api.push_message(driver.d_line_id,  message)

            return JsonResponse({'status':'end_departing'})
    return render(request, 'driver_tools/navigate2start.html')






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
                    User_Text = event.message.text
                    print(User_Text)
                    if User_Text in ["上線接單"]: 
                        message = driver_function(uid)   #司機功能選項
                elif isinstance(event, PostbackEvent):
                    if "[end]" in event.postback.data:
                        """
                        1. req_id 、 上下車地點、 結束req_id[write_chat] as context to liff
                        4. end button -> liff close and reqid[end] request;
                        5. get: reqid[end] request ->  rsv.closed_at = timezone.now() 、 rsvsave
                        """
                        driver = Driver.objects.get(d_line_id=uid)
                        req_id = event.postback.data.split("[end]")
                        rsv = RideRSV.objects.get(req_id=req_id[1])
                        if  RideRequest.objects.get(req_id=req_id[1]).is_canceled == True:
                            message = TextSendMessage(text=f"【{req_id[1]}】已被取消")
                        elif driver.current_rsv == None and RideRSV.objects.get(req_id=req_id[1]).closed_at!=None:
                            message = TextSendMessage(text=f"【{req_id[1]}】已結單了")
                        elif not(RideRSV.objects.get(req_id=driver.current_rsv).closed_at):
                            message = TextSendMessage(text=f"【{req_id[1]}】未正確關閉。")
                        else:                            
                            message = [end_journey(rsv)] #成功接單訊息及確認乘客上車訊息 
                    elif "[didn't get on]" in event.postback.data :
                        req_id = event.postback.data.split("[pay complete]")
                        driver =Driver.objects.get(d_line_id=uid)
                        rsv = RideRSV.objects.get(req_id=driver.current_rsv)
                        rsv.confirmed_at = timezone.now()
                        rsv.save()
                        #通知乘客專區
                        passenger = Passengers.objects.get(p_line_id=rsv.p_line_id).use_server
                        p_bot_api= LineBotApi(settings.LINE_CHANNEL_DATA[passenger]['ACCESS_TOKEN'])
                        p_bot_api.push_message(rsv.p_line_id,TextSendMessage(text=f"通知: 訂單{driver.current_rsv}乘客，由於司機已抵達5分鐘，系統已自動開始待速跳表，請盡速上車，謝謝。"))
            
                    elif "[pay complete]" in event.postback.data :
                        message = [driver_function(uid)] #成功接單訊息及確認乘客上車訊息 
                        req_id = event.postback.data.split("[pay complete]")
                        driver =Driver.objects.get(d_line_id=uid)
                        if driver.current_rsv == None and RideRSV.objects.get(req_id=req_id[1]).closed_at!=None:
                            message = TextSendMessage(text=f"【{req_id[1]}】已結單了")
                        else:
                            rsv = RideRSV.objects.get(req_id=req_id[1])
                            
                            passenger = Passengers.objects.get(p_line_id=rsv.p_line_id).use_server
                            p_bot_api= LineBotApi(settings.LINE_CHANNEL_DATA[passenger]['ACCESS_TOKEN'])
                            try:
                                p_bot_api.push_message(rsv.p_line_id,sent_end_journey(rsv))
                            except Exception as err:
                                print(err)

                            """通知訂單"""
                            driver.current_rsv = None
                            driver.save()

                    elif "[navigator cancel]" in event.postback.data :
                        req_id = event.postback.data.split("[navigator cancel]")
                        req_id = RideRequest.objects.get(req_id=req_id[1])
                        driver = Driver.objects.get(d_line_id=uid)
                        rsv = RideRSV.objects.get(req_id=driver.current_rsv)
                        message = [ComfirmOrder(str(req_id)),StartCalcular(rsv)] #成功接單訊息及確認乘客上車訊息 
                        passenger = Passengers.objects.get(p_line_id=rsv.p_line_id).use_server
                        NotifyArrived(rsv,driver,passenger)
                        
                    elif "[get]" in event.postback.data :
                        message = TextSendMessage(text=f"訂單不成立，請重新接單") #Default
                        req_id = event.postback.data.split("[get]")
                        req_id = RideRequest.objects.get(req_id=req_id[1])
                        driver = Driver.objects.get(d_line_id=uid)
                        if driver.current_rsv != None: #目前訂單尚未完成
                            message = TextSendMessage(text=f"目前還有其他訂單，完成訂單才可使用繼續接單")  # time.sleep(10)
                            #如果訂單沒有被取消而且訂單被安排的司機為本人
                        elif  RideRequest.objects.get(req_id=str(req_id)).is_canceled != True and RideRequest.objects.get(req_id=str(req_id)).current_driver == str(Driver.objects.get(d_line_id=uid).id):  # 車隊在資料庫內，而且uid身分是司機 而且 沒被取消
                            try:
                                #需求轉訂單成立
                                req_rsv = RideRequest.objects.get(req_id=str(req_id))#依照該訂單的編號，調資料
                                req_rsv.to_rsv = True #讓訂單正式成立
                                req_rsv.save()
                                #司機下線
                                driver = Driver.objects.get(d_line_id=uid)

                                if req_rsv.to_rsv and not(len(RideRSV.objects.filter(req_id = req_rsv))): #成立正式訂單，將乘客跟司機資料丟進去，並存入距離等。
                                    # 起點與終點座標
                                    driver_current = tuple(map(float,(json.loads(driver.current_location)['lati_NS'], json.loads(driver.current_location)['longi_EW']))) # New York, NY
                                    origin = tuple(map(float,(json.loads(req_rsv.departing)['lati_NS'], json.loads(req_rsv.departing)['longi_EW']))) # New York, NY
                                    gurl = f"https://maps.googleapis.com/maps/api/directions/json?origin={driver_current[0]}%2C{driver_current[1]}&destination={origin[0]}%2C{origin[1]}&key={gmaps_key}"
                                    print(gurl)
                                    # 取得路線資料
                                    directions_result = json.loads(requests.request("GET", gurl).text)
                                    print("directions_result",directions_result)
                                    duration = int(directions_result['routes'][0]["legs"][0]['duration']['value']//60)
                                    distance = directions_result['routes'][0]["legs"][0]['distance']['value']/1000
                                    print("duration & distance",duration,distance)
                                    print(driver.current_group)
                                    print(DriverGroup.objects.get(driver_group=driver.current_group))
                                    rsv = RideRSV.objects.create(req_id = req_rsv ,d_line_id=uid,driver_group=DriverGroup.objects.get(driver_group=driver.current_group), p_line_id=req_rsv.p_line_id , departing=req_rsv.departing, arriving=req_rsv.arriving , travel_distance=distance , travel_time=duration , travel_fare=0 )

                                    passenger = Passengers.objects.get(p_line_id=rsv.p_line_id).use_server
                                    p_bot_api= LineBotApi(settings.LINE_CHANNEL_DATA[passenger]['ACCESS_TOKEN'])
                                    p_bot_api.push_message(str(rsv.p_line_id),Findtaxi(uid,duration)) #通知乘客找到司機，並傳送司機資料
                                    message = [successOrder(uid,str(req_id),duration)] #成功接單訊息及確認乘客上車訊息 
                                    driver.is_online = False
                                    driver.current_rsv = str(req_id) #目前訂單為rsv
                                    driver.save()
                                    #ComfirmOrder(str(req_id))
                            except Exception as error:
                                print(1,error)
                            except BaseError as error:
                                print(2,error)
                            except LineBotApiError as error:
                                print(3,error)
                            except InvalidSignatureError as error:
                                print(4,error)

                        else:
                            message = TextSendMessage(text=f"訂單不成立，請重新接單")
                d_bot_api.reply_message(event.reply_token, message)  # time.sleep(10)            except:
            except:
                break
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
