from django.db import models


class ObjectType(models.Model):
    OBJECT_CHOICES = [
        ('person', 'شخص'),
        ('bicycle', 'دوچرخه'),
        ('car', 'خودرو'),
        ('motorcycle', 'موتورسیکلت'),
        ('airplane', 'هواپیما'),
        ('bus', 'اتوبوس'),
        ('train', 'قطار'),
        ('truck', 'کامیون'),
        ('boat', 'قایق'),
        ('traffic_light', 'چراغ راهنمایی'),
        ('fire_hydrant', 'شیر آتش‌نشانی'),
        ('stop_sign', 'تابلوی ایست'),
        ('parking_meter', 'پارکومتر'),
        ('bench', 'نیمکت'),
        ('bird', 'پرنده'),
        ('cat', 'گربه'),
        ('dog', 'سگ'),
        ('horse', 'اسب'),
        ('sheep', 'گوسفند'),
        ('cow', 'گاو'),
        ('elephant', 'فیل'),
        ('bear', 'خرس'),
        ('zebra', 'گورخر'),
        ('giraffe', 'زرافه'),
        ('backpack', 'کوله‌پشتی'),
        ('umbrella', 'چتر'),
        ('handbag', 'کیف دستی'),
        ('tie', 'کراوات'),
        ('suitcase', 'چمدان'),
        ('frisbee', 'فریزبی'),
        ('skis', 'اسکی'),
        ('snowboard', 'اسنوبرد'),
        ('sports_ball', 'توپ ورزشی'),
        ('kite', 'بادبادک'),
        ('baseball_bat', 'چوب بیسبال'),
        ('baseball_glove', 'دستکش بیسبال'),
        ('skateboard', 'اسکیت‌برد'),
        ('surfboard', 'تخته موج‌سواری'),
        ('tennis_racket', 'راکت تنیس'),
        ('bottle', 'بطری'),
        ('wine_glass', 'لیوان شراب'),
        ('cup', 'فنجان'),
        ('fork', 'چنگال'),
        ('knife', 'چاقو'),
        ('spoon', 'قاشق'),
        ('bowl', 'کاسه'),
        ('banana', 'موز'),
        ('apple', 'سیب'),
        ('sandwich', 'ساندویچ'),
        ('orange', 'پرتقال'),
        ('broccoli', 'کلم بروکلی'),
        ('carrot', 'هویج'),
        ('hot_dog', 'هات داگ'),
        ('pizza', 'پیتزا'),
        ('donut', 'دونات'),
        ('cake', 'کیک'),
        ('chair', 'صندلی'),
        ('couch', 'مبل'),
        ('potted_plant', 'گلدان'),
        ('bed', 'تخت'),
        ('dining_table', 'میز ناهارخوری'),
        ('toilet', 'توالت'),
        ('tv', 'تلویزیون'),
        ('laptop', 'لپ‌تاپ'),
        ('mouse', 'موس'),
        ('remote', 'ریموت'),
        ('keyboard', 'کیبورد'),
        ('cell_phone', 'تلفن همراه'),
        ('microwave', 'مایکروویو'),
        ('oven', 'فر'),
        ('toaster', 'توستر'),
        ('sink', 'سینک'),
        ('refrigerator', 'یخچال'),
        ('book', 'کتاب'),
        ('clock', 'ساعت'),
        ('vase', 'گلدان'),
        ('scissors', 'قیچی'),
        ('teddy_bear', 'خرس عروسکی'),
        ('hair_dryer', 'سشوار'),
        ('toothbrush', 'مسواک'),
    ]

    name = models.CharField(max_length=20, choices=OBJECT_CHOICES, unique=True)
    
    def __str__(self):
        return self.name


class UserObjectRequest(models.Model):
    name = models.CharField(max_length=255)
    object_types = models.ManyToManyField(ObjectType)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        object_names = ', '.join([obj.name for obj in self.object_types.all()])
        return f"Request for {object_names} by {self.name} on {self.timestamp}"

