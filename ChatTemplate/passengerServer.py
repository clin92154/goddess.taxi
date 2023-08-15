import json
# from .models import *
from urllib.parse import quote
from goddess_taxi_server.models import *








#以乘客來講，可能以不用輸入的方式，而是用定位方式會比較方便
#keyword: google api 計程車

def Findtaxi(dline,duration):
    #如果找到司機
    driver = Driver.objects.get(d_line_id=dline)
    return  TextSendMessage(text=f''' 
    找到司機啦～

    您的司機正在路上，預計{duration}分鐘至{duration+2}分鐘後抵達！
    【司機】{driver.driver_name} 先生/小姐
    【車牌】{driver.car_no}
    【計程車外觀】{driver.car_desc}

    請儘速前往上車地點～
    ''')








def sent_end_journey(rsv):
    departing= json.loads(rsv.departing)['name']
    arriving = json.loads(rsv.arriving)['name']
    route_map = str(rsv.route_map)
    route_map = quote(route_map, safe=':/?&=')
    format = {
  "type": "carousel",
  "contents": [
    {
      "type": "bubble",
      "size": "mega",
      "header": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": "【35】訂單明細",
            "wrap": True,
            "weight": "bold",
            "margin": "sm",
            "size": "3xl",
            "adjustMode": "shrink-to-fit",
            "align": "center",
            "color": "#FFFFFF"
          }
        ],
        "backgroundColor": "#A2A9FF"
      },
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": f"NT${rsv.travel_fare}",
            "weight": "bold",
            "size": "xl",
            "offsetBottom": "lg"
          },
          {
            "type": "box",
            "layout": "vertical",
            "margin": "lg",
            "spacing": "sm",
            "contents": [
              {
                "type": "box",
                "layout": "baseline",
                "spacing": "sm",
                "contents": [
                  {
                    "type": "text",
                    "text": "上車地點：",
                    "color": "#B8860B",
                    "size": "sm",
                    "flex": 3,
                    "weight": "bold"
                  },
                  {
                    "type": "text",
                    "text": f"{departing}",
                    "wrap": True,
                    "color": "#666666",
                    "size": "sm",
                    "flex": 6
                  }
                ]
              },
              {
                "type": "box",
                "layout": "baseline",
                "spacing": "sm",
                "contents": [
                  {
                    "type": "text",
                    "text": "下車地點：",
                    "color": "#B8860B",
                    "size": "sm",
                    "flex": 3,
                    "weight": "bold"
                  },
                  {
                    "type": "text",
                    "text": f"{arriving}",
                    "wrap": True,
                    "color": "#666666",
                    "size": "sm",
                    "flex": 6
                  }
                ]
              },
              {
                "type": "box",
                "layout": "baseline",
                "spacing": "sm",
                "contents": [
                  {
                    "type": "text",
                    "text": "總里程數：",
                    "color": "#B8860B",
                    "size": "sm",
                    "flex": 3,
                    "weight": "bold"
                  },
                  {
                    "type": "text",
                    "text": f"{rsv.travel_distance}公里",
                    "wrap": True,
                    "color": "#666666",
                    "size": "sm",
                    "flex": 6
                  }
                ]
              }
            ],
            "offsetBottom": "xxl"
          },
          {
            "type": "separator"
          },
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "text",
                "text": "感謝您選擇女神大車隊，期待下次再為您服務～",
                "wrap": True,
                "weight": "bold",
                "decoration": "none",
                "align": "start",
                "scaling": False,
                "margin": "lg"
              }
            ]
          }
        ]
      },
      "styles": {
        "body": {
          "separator": False
        },
        "footer": {
          "separator": True
        }
      }
    },
    {
      "type": "bubble",
      "size": "mega",
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "image",
            "url": route_map,
            "size": "full",
            "aspectMode": "cover"
          }
        ],
        "offsetTop": "none",
        "paddingAll": "none"
      }
    }
  ]
}    
    flex_message = FlexSendMessage(
        alt_text="明細資料",
        contents=format
        
    )

    return flex_message
# def startcompular():
#     reutrn '''司機已開始跳表計費，
#     祝您旅途平安～
#     目前里程數：0 KM
#     費率小計：$ 80
#     '''