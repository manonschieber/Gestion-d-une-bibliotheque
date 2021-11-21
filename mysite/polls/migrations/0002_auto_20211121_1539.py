# Generated by Django 3.2.9 on 2021-11-21 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Livre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nomAuteur', models.CharField(max_length=15)),
                ('prenomAuteur', models.CharField(max_length=15)),
                ('titre', models.CharField(max_length=15)),
                ('disponibilite', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='client',
            name='solde',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
    ]
