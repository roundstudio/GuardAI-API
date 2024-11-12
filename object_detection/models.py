from django.db import models


class ObjectType(models.Model):
    OBJECT_CHOICES = [
        ('person', 'شخص'),
        ('bicycle', 'دوچرخه'),
        ('car', 'خودرو'),
        ('motorcycle', 'موتورسیکلت'),
        ('bus', 'اتوبوس'),
        ('train', 'قطار'),
        ('truck', 'تراکتور'),
        ('bird', 'پرنده'),
        ('cat', 'گربه'),
        ('dog', 'سگ'),
        ('sheep', 'گوسفند'),
        ('cow', 'گوساله'),
        ('table', 'میز'),
        ('chair', 'صندلی'),
        ('shoe', 'کفش'),
        ('bag', 'کیف'),
        ('book', 'کتاب'),
        ('cell_phone', 'موبایل'),
        ('laptop', 'کامپیوتر'),
        ('food', 'غذا'),
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

