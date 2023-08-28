import openpyxl
File = openpyxl.load_workbook('static/excel/系統司機建檔 (回覆).xlsx')
# print(File)
sheet1 = File.worksheets[0]

import os
import django
import requests                 #擷取網頁用的模組
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from goddess_taxi_server import models

import random
from django.contrib.auth.hashers import make_password

drivers = []
for row in sheet1['B2':'L85']:
    driver = []
    for c in row:
        driver.append(str(c.value))
    drivers.append(driver)


for driver in drivers:
    print(driver)
    d, created = models.Driver.objects.get_or_create(name = driver[1], is_online = False)

    if created:
        d.driver_name = driver[0]
        d.driver_hp = driver[4]
        d.password = make_password(driver[2])
        d.car_no = driver[5]
        d.car_desc = driver[6]

        if driver[8] == "女神":
            driver[8] = "女神叫車"

        d.driver_group.add(models.DriverGroup.objects.get(driver_group=driver[8]))
    d.save()




