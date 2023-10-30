# Generated by Django 4.2.6 on 2023-10-18 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0004_book_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='status',
            field=models.IntegerField(choices=[('AVAILABLE', 'AVAILABLE'), ('LENT', 'LENT')], default=0),
        ),
    ]
