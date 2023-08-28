from django.contrib.postgres.fields import JSONField
from django.db import models 
from django.utils import timezone
from django.contrib.auth.hashers import make_password

# import django.db.models.JSONField
class Passengers(models.Model):
    """
    p_line_id：設為PK
    favorite_places： JSONField(null=True, blank=True)
    """
    
    p_line_id = models.CharField(max_length=255, blank=True, primary_key=True) 
    name = models.CharField(max_length=255, blank=True) 
    passenger_hp = models.CharField(max_length=10,null=True, blank=True)
    favorite_places = models.JSONField(null=True, blank=True)
    use_server = models.CharField(max_length=50, blank=True)
    def __str__(self):
        return self.p_line_id
    


class DriverGroup(models.Model):
    """
    group_id: INT
    driver_group: max_length=3 字母組合最多只會有3^3，節省空間
    """
    group_id = models.AutoField(primary_key=True)
    driver_group = models.CharField(max_length=255)
    priority = models.IntegerField(default=0)
    last_rsv = models.DateTimeField(null=True, blank=True)#models.DateTimeField(null=True, blank=True)
    base_fare = models.IntegerField(default=50)
    def __str__(self):
        return self.driver_group

    def drivers_list(self, obj):
        drivers = obj.driver_set.all()
        return [driver.driver_name for driver in drivers]

    def update_priority(self):
        # Get all DriverGroup objects ordered by last_rsv in ascending order
        driver_groups = DriverGroup.objects.order_by('last_rsv') #遞減方式排序
        # Update priority of each DriverGroup based on its position in the sorted list
        for i, driver_group in enumerate(driver_groups):
            driver_group.priority = i
            driver_group.save()

    def update_last_rsv(self):
        # Get thest RideRSV object associated with this DriverGroup
        latest_rsv = RideRSV.objects.filter(driver_group=self.group_id).order_by('-confirmed_at').first()

        if latest_rsv:
            # Update last_rsv of this DriverGroup
            self.last_rsv = latest_rsv.confirmed_at
            self.save()
            # Update priorities of all DriverGroups based on their last_rsv values
            self.update_priority()


class Driver(models.Model):
    """
    driver_id: 設為PK
    car_desc: max_length=45
    last_online: 改為 DateTimeField，要準確至時間
    """
    
    name = models.CharField(max_length=255, blank=True)  # driver_Line_id名稱
    d_line_id = models.CharField(max_length=255, blank=True)  # line_user_id
    driver_name = models.CharField(max_length=20, null=True, blank=True)  # driver_name
    driver_hp = models.CharField(max_length=10, null=True, blank=True)  # 手機號碼
    password = models.CharField(max_length=255, null=True, blank=True)  #密碼
    car_no = models.CharField(max_length=20, null=True, blank=True)  # 車牌
    car_desc = models.CharField(max_length=30, null=True, blank=True)  # 車樣
    is_online = models.BooleanField()  # 上線狀態
    current_location = JSONField(null=True, blank=True)  # 目前位置
    last_online = models.DateTimeField(null=True, blank=True)  # 最後上線時間
    driver_group = models.ManyToManyField(DriverGroup)  # 登記所屬車隊
    current_group = models.CharField(max_length=255,null=True, blank=True) #目前被歸類車隊 
    current_rsv = models.CharField(max_length=8,null=True, blank=True)  # 目前的訂單
    
    def __str__(self):
        return self.driver_hp

    def get_driver_group(self):
        return str(self.driver_group)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class RideRequest(models.Model):
    """
    check欄位 改為 to_rsv，意即是否已成功轉成建立訂單
    """
    req_id = models.AutoField(primary_key=True)
    p_line_id = models.ForeignKey(Passengers, on_delete=models.CASCADE)
    departing = JSONField(null=True, blank=True)  # departing
    arriving = JSONField(null=True, blank=True)  # arriving
    remarks = models.CharField(default="沒有需求",max_length=255, blank=True)  # favorite_places
    to_rsv = models.BooleanField(default=False)  # 訂單有無成立
    current_driver = models.CharField(max_length=255, blank=True) #目前找到的司機
    is_canceled=models.BooleanField(default=False)  # 訂單有無取消
    is_sent = models.BooleanField(default=False)  # 訂單有無成立


    def __str__(self):
        return f"{self.req_id}"
 



class RideRSV(models.Model):
    """
    comfirmed_at 改為 confirmed_at ，拼寫錯誤XD，且使用DateTimeField，準確至時間
    """
    rsv_id = models.AutoField(primary_key=True)
    req_id = models.ForeignKey(RideRequest, on_delete=models.CASCADE)
    driver_group = models.ForeignKey(DriverGroup, on_delete=models.CASCADE)
    d_line_id = models.CharField(max_length=255, null=True, blank=True)
    p_line_id = models.CharField(max_length=255, null=True, blank=True)
    departing = JSONField(null=True, blank=True)  # departing
    arriving = JSONField(null=True, blank=True)  # arriving
    confirmed_at = models.DateTimeField(null=True, blank=True) #計單開始計費時間
    actual_route = models.BinaryField() #實際路徑
    route_map =models.TextField(max_length=5000,null=True,blank=True)
    travel_distance = models.FloatField() #距離
    travel_time = models.FloatField() #時間
    travel_fare = models.FloatField() #費用
    closed_at = models.DateTimeField(null=True, blank=True)  # 訂單結單時間
    
    def __str__(self):
        return f"{self.rsv_id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.driver_group.update_last_rsv()


