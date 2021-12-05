# Generated by Django 3.2.5 on 2021-12-04 11:31

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0011_auto_20211203_0924'),
    ]

    operations = [
        migrations.AddField(
            model_name='emprunt',
            name='reserve_le',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='emprunt',
            name='emprunte_le',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='emprunt',
            name='retour_max_le',
            field=models.DateField(default=datetime.datetime(2022, 1, 3, 11, 31, 26, 909486, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='livre',
            name='cree_le',
            field=models.DateField(default=datetime.datetime(2021, 12, 4, 11, 31, 26, 909486, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='paiement',
            name='cree_le',
            field=models.DateField(default=datetime.datetime(2021, 12, 4, 11, 31, 26, 909486, tzinfo=utc)),
        ),
    ]