from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)    # краткое имя

    def __str__(self):
        return self.slug


class PrivateAccount(models.Model):
    account = models.CharField(max_length=50, unique=True)


class Project(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    account = models.OneToOneField(
        PrivateAccount,
        on_delete=models.CASCADE,
        related_name='project'
    )

    def __str__(self):
        return self.slug


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.slug


class Status(models.TextChoices):
    ACTIVE = 'active', 'На балансе'
    NON_ACTIVE = 'non active', 'Списано'
    TO_BE_WRITTEN_OFF = 'to be written off', 'К списанию'


class Ware(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    inventory = models.CharField(max_length=50, unique=True, null=True)
    serial = models.CharField(max_length=50, blank=True)
    quantity = models.FloatField(default=1.)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='wares'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='wares'
    )


    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='wares'
    )

    account = models.CharField(max_length=100, null=True)
    account_date = models.DateTimeField(null=True)
    name_in_account = models.CharField(max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class WarePhoto(models.Model):
    ware = models.ForeignKey(
        Ware,
        on_delete=models.CASCADE,
        related_name='photos'  # У одного товара может быть список photos
    )

    image = models.ImageField(upload_to='wares/photos/')
    is_main = models.BooleanField(default=True)

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
        on_delete=models.CASCADE,
        related_name='rooms'
    )

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=50)

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='locations'
    )

    def __str__(self):
        return self.name

