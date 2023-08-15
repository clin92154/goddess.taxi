import json


from linebot.models import *
from goddess_taxi_server.models import *
from django.http import HttpResponse
from django.conf import settings
from urllib.parse import quote
from linebot import WebhookHandler





def end_journey(rsv):
    format = {
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "【行程已結束】",
        "weight": "bold",
        "size": "xl"
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
                "text": "行車距離：",
                "color": "#aaaaaa",
                "size": "sm",
                "flex": 2
              },
              {
                "type": "text",
                "text": f"{rsv.travel_distance} 公里",
                "wrap": True,
                "color": "#666666",
                "size": "sm",
                "flex": 5
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
                "text": "行車時間：",
                "color": "#aaaaaa",
                "size": "sm",
                "flex": 2
              },
              {
                "type": "text",
                "text": f"{rsv.travel_time}分鐘",
                "wrap": True,
                "color": "#666666",
                "size": "sm",
                "flex": 5
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
                "text": "費　　率：",
                "color": "#aaaaaa",
                "size": "sm",
                "flex": 2
              },
              {
                "type": "text",
                "text": f"${rsv.travel_fare}",
                "wrap": True,
                "color": "#666666",
                "size": "sm",
                "flex": 5
              }
            ]
          }
        ]
      }
    ]
  },
  "footer": {
    "type": "box",
    "layout": "vertical",
    "spacing": "sm",
    "contents": [
      {
        "type": "button",
        "action": {
          "type": "postback",
          "label": "確認結單",
          "data": f"[pay complete]{rsv.req_id}",
          "displayText":"確認結單",
        }
      },
      {
        "type": "box",
        "layout": "vertical",
        "contents": [],
        "margin": "sm"
      }
    ],
    "flex": 0
  }
}
    
    flex_message = FlexSendMessage(
        alt_text="endJourney",
        contents=format
    )
    return flex_message  

def StartCalcular(rsv):
    
    departing= json.loads(rsv.departing)['name']
    try:
      arriving = json.loads(rsv.arriving)['name'] 
    except:
      arriving = '乘客告知地點'
    
    basefare = DriverGroup.objects.get(driver_group=rsv.driver_group).base_fare
    format = {
  "type": "bubble",
  "header": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "導航計費(乘客上車)/結單功能區",
        "margin": "md",
        "size": "xl",
        "align": "center",
        "weight": "bold"
      }
    ]
  },
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": "【適用費率】",
            "weight": "bold",
            "size": "xl"
          },
          {
            "type": "box",
            "layout": "vertical",
            "margin": "lg",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": f"- ${basefare}起跳",
                "align": "start",
                "margin": "sm",
                "offsetStart": "lg"
              },
              {
                "type": "text",
                "text": "- 每公里$20",
                "align": "start",
                "margin": "sm",
                "offsetStart": "lg"
              },
              {
                "type": "text",
                "text": "- 每分鐘$2",
                "align": "start",
                "margin": "sm",
                "offsetStart": "lg"
              }
            ]
          }
        ]
      },
      {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": "【出發】",
            "weight": "bold",
            "size": "xl"
          },
          {
            "type": "box",
            "layout": "baseline",
            "margin": "none",
            "spacing": "none",
            "contents": [
              {
                "type": "text",
                "text": f"{departing}",
                "align": "start",
                "margin": "none",
                "offsetStart": "lg",
                "wrap": True
              }
            ]
          }
        ]
      },
      {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": "【目的地】",
            "weight": "bold",
            "size": "xl"
          },
          {
            "type": "box",
            "layout": "baseline",
            "margin": "none",
            "spacing": "none",
            "contents": [
              {
                "type": "text",
                "text": f"{arriving}",
                "align": "start",
                "margin": "none",
                "offsetStart": "lg",
                "wrap": True
                
              }
            ]
          }
        ]
      }
    ]
  },
  "footer": {
    "type": "box",
    "layout": "vertical",
    "spacing": "sm",
    "contents": [
      {
        "type": "button",
        "style": "link",
        "height": "sm",
        "action": {
          "type": "uri",
          "label": "開始導航",
          "uri": "https://liff.line.me/2000375045-2GpZ1RaK"
        }
      },
      
      {
        "type": "button",
        "action": {
          "type": "postback",
          "label": "完成訂單",
          "data": f"[end]{rsv.req_id}",
          "displayText":"完成訂單"
        }
      },
      {
        "type": "box",
        "layout": "vertical",
        "contents": [],
        "margin": "sm"
      }
    ],
    "flex": 0
  },
  "styles": {
    "body": {
      "separator": True
    },
    "footer": {
      "separator": True
    }
  }
}
    
    flex_message = FlexSendMessage(
        alt_text="StartCalcular",
        contents=format
        
    )

    return flex_message    

def ComfirmOrder(req):
  print(req,"未上車")
  format = {
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "乘客5分鐘未上車並進行跳表",
        "margin": "md",
        "size": "lg",
        "wrap": True,
        "align": "center"
      }
    ],
    "spacing": "none",
    "margin": "none",
    "cornerRadius": "none"
  },
  "footer": {
    "type": "box",
    "layout": "vertical",
    "spacing": "sm",
    "contents": [
      {
        "type": "button",
        "style": "link",
        "height": "sm",
        "action": {
          "type": "postback",
          "label": f"訂單【{req}】5分鐘尚未上車",
          "data": f"[didn't get on]{req}",
          "displayText": "乘客5分鐘未上車並進行跳表"
        }
      },
      {
        "type": "text",
        "text": "【注意】",
        "color": "#FF0000",
        "decoration": "none",
        "weight": "bold",
        "wrap": True,
        "scaling": True,
        "align": "center"
      },
      {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": "1. 若點選此選項即【通知並未上車之乘客】盡速上車並【開啟跳表】",
            "size": "md",
            "align": "start",
            "gravity": "center",
            "wrap": True,
            "margin": "none",
            "weight": "regular",
            "position": "relative",
            "decoration": "none",
            "style": "normal",
            "contents": []
          },
          
          {
            "type": "text",
            "text": "2.若乘客【已上車】則點選【已上車】進入導航介面。",
            "wrap": True,
            "gravity": "bottom",
            "align": "start"
          }
        ],
        "cornerRadius": "none",
        "borderColor": "#AAAAAA",
        "backgroundColor": "#CCCCCC",
        "paddingAll": "lg",
        "borderWidth": "light"
      }
    ],
    "flex": 0
  }
}

  flex_message = FlexSendMessage(
        alt_text="ComfirmOrder",
        contents=format
        
    )

  return flex_message


def successOrder(uid,req,duration):
    location = json.loads(RideRequest.objects.get(req_id=req).departing)
    format = {
  "type": "bubble",
  "size": "mega",
  "header": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": f"訂單【{req}】接單成功！",
        "size": "lg",
        "weight": "bold",
        "wrap": True,
        "offsetTop": "none",
        "offsetBottom": "none",
        "offsetStart": "none",
        "offsetEnd": "none"
      }
    ]
  },
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [

 
      {
        "type": "text",
        "text": "請點選下列地址以導航至上車地點!"
      }
    ]
  },
  "footer": {
    "type": "box",
    "layout": "vertical",
    "contents": [
       
        {
          "type": "button",
          "style": "link",
          "height": "sm",
          "action": {
            "type": "uri",
            "label": "使用內建導航",
            "uri": "https://liff.line.me/2000375045-yZLYrm5d"
          }
        },
      {
        "type": "button",
        "action": {
          "type": "uri",
          "label": "使用Google Map導航",
          "uri": f"https://www.google.com/maps/search/?api=1&query={location['lati_NS']},{location['longi_EW']}"
        }
      },     {
        "type": "button",
        "action": {
          "type": "postback",
          "label": "繼續/已到乘客上車地點",
          "data": f"[navigator cancel]{req}",
          "displayText": "繼續/已到乘客上車地點"
        }
      }
    ]
  },
  "styles": {
    "header": {
      "separator":True
    }
  }
}



    
    flex_message = FlexSendMessage(
        alt_text="success",
        contents=format
        
    )

    return flex_message






#得到定單資訊
def waitOrder(order):
    print(order.req_id)
    remarks = RideRequest.objects.get(req_id=str(order.req_id))
    departing= json.loads(order.departing)['name']
    check = True #檢查有無下車點
    try:
      arriving = json.loads(order.arriving)['name'] 
    except:
      arriving = "None"
      check = False
    print(order.req_id)

    #LIFF進去網頁取得GPS及uid，配對完成等到接單後關閉網頁，並主動推撥訂單資訊
    format = {
      "type": "bubble",
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": f"編號#{order.req_id}",
            "weight": "bold",
            "color": "#1DB446",
            "size": "sm"
          },
          {
            "type": "text",
            "text": "乘客叫車需求",
            "weight": "bold",
            "size": "xxl",
            "margin": "md",
            "style": "normal",
            "align": "center"
          },
          {
            "type": "separator",
            "margin": "xxl"
          },
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                  {
                    "type": "text",
                    "text": "【上車地點】",
                    "weight": "bold"
                  },
                  {
                    "type": "text",
                    "text": f"{departing}",
                    "align": "end",
                    "wrap": True
                  }
                ],
                "width": "100%",
                "justifyContent": "flex-start",
                "paddingTop": "lg",
                "paddingStart": "none",
                "paddingEnd": "none",
                "paddingBottom": "lg"
              },
              {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                  {
                    "type": "text",
                    "text": "【下車地點】",
                    "weight": "bold"
                  },
                  {
                    "type": "text",
                    "text": f"{arriving}",
                    "align": "end",
                    "wrap": True
                  }
                ],
                "width": "100%",
                "justifyContent": "flex-start",
                "paddingTop": "lg",
                "paddingStart": "none",
                "paddingEnd": "none",
                "paddingBottom": "lg"
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
                    "text": "【註解】",
                    "offsetTop": "none",
                    "margin": "md",
                    "weight": "bold"
                  },
                  {
                    "type": "text",
                    "text": f"\"{remarks.remarks}\"",
                    "align": "center",
                    "gravity": "center",
                    "margin": "xxl",
                    "size": "lg",
                    "wrap": True    
                  }
                ]
              }
            ]
          },
          {
            "type": "separator",
            "margin": "xxl"
          },
          {
            "type": "box",
            "layout": "horizontal",
            "margin": "md",
            "contents": [
              {
                "type": "text",
                "text": "RideRequest  ID",
                "size": "xs",
                "color": "#aaaaaa",
                "flex": 0
              },
              {
                "type": "text",
                "text": f"#{order.req_id}",
                "color": "#aaaaaa",
                "size": "xs",
                "align": "end"
              }
            ]
          }
        ]
      },
      "footer": {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "button",
            "action": {
              "type": "postback",
              "label": "確認接單",
              "data": f"[get]{order.req_id}",
              "displayText": "確認接單"
            }
          },
          {
            "type": "button",
            "action": {
              "type": "uri",
              "label": "繼續找尋",
              "uri": "https://liff.line.me/1660989772-YZW8X4yO"
            }
          }
        ]
      },
      "styles": {
        "footer": {
          "separator": True
        }
      }
    }

    if not(check) : 
      del format['body']["contents"][3]["contents"][1]
       
   
    flex_message = FlexSendMessage(
        alt_text="waitOrder",
        contents=format
    )

    return flex_message


#司機驗證、上線接單模板
def driver_function(uid):
    format = {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png",
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover",
            "action": {
            "type": "uri",
            "uri": "http://linecorp.com/"
            }
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "text",
                "weight": "bold",
                "size": "xl",
                "text": "我是司機",
                "contents": []
            },
            {
                "type": "text",
                "text": "司機專屬功能！非司機請移步喔～"
            }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
             {
                "type": "button",
                "style": "link",
                "height": "sm",
                "action": {
                "type": "uri",
                "label": "上線接單",
                "uri": "https://liff.line.me/2000375045-m4D2Wp53"
                }
            },
            {
                "type": "button",
                "style": "link",
                "height": "sm",
                "action": {
                "type": "uri",
                "label": "司機驗證",
                "uri": "https://liff.line.me/2000375045-Z478EObV"
                }
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [],
                "margin": "sm"
            }
            ],
            "flex": 0
        }
        }


    # 判斷有無登記
    user_data =Driver.objects.filter(d_line_id=uid)
    if user_data:
        del format["footer"]["contents"][1]
    else:
        del format["footer"]["contents"][0]

    flex_message = FlexSendMessage(
        alt_text="我是司機",
        contents=format
        
    )
    
    return flex_message

