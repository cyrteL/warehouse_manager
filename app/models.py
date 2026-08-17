from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)    # краткое имя

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class PrivateAccount(models.Model):
    account = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.account


class Project(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    account = models.OneToOneField(
        PrivateAccount,
        on_delete=models.PROTECT,
        related_name='project'
    )

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Status(models.TextChoices):
    ACTIVE = 'active', 'На балансе'
    WRITE_OFF_AGE = 'write_off_age', 'На списание по давности'
    WRITE_OFF_DEFECT = 'write_off_defect', 'На списание по браку'
    WRITE_OFF_FAULT = 'write_off_fault', 'На списание по неисправности'
    WRITE_OFF_PROJECT = 'write_off_project', 'На списание как расход по проекту'
    WRITTEN_OFF = 'written_off', 'Списано'


class WareQuerySet(models.QuerySet):
    def visible(self):
        return self.exclude(status=Status.WRITTEN_OFF)


class Ware(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    inventory = models.CharField(max_length=50, unique=True, null=True, blank=True)
    serial = models.CharField(max_length=50, blank=True)
    quantity = models.FloatField(default=1.)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='wares',
        null=True,
        blank=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='wares',
        null=True,
        blank=True
    )


    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        related_name='wares',
        null=True,
        blank=True
    )


    location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        related_name='wares',
        null=True,
        blank=True
    )

    accounting_code = models.CharField(max_length=100, blank=True)
    account_date = models.DateField(null=True, blank=True)
    name_in_account = models.CharField(max_length=200, blank=True)
    source_department = models.CharField(max_length=300, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = WareQuerySet.as_manager()

    class Meta:
        indexes = [
            models.Index(fields=['status'])
        ]

    def __str__(self):
        return self.name


class WarePhoto(models.Model):
    ware = models.ForeignKey(
        Ware,
        on_delete=models.CASCADE,
        related_name='photos'  # У одного товара может быть список photos
    )

    image = models.ImageField(upload_to='wares/photos/')
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f'Photo: {self.ware.name}'


# корпус
class Housing(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=50)

    housing = models.ForeignKey(
        Housing,
        on_delete=models.PROTECT,
        related_name='rooms'
    )

    class Meta:
        unique_together = ('housing', 'name')

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=50)

    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name='locations'
    )

    class Meta:
        unique_together = ('room', 'name')

    def __str__(self):
        return self.name

