# Generated by Django 2.2 on 2019-04-25 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('input', '0012_auto_20190425_1525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='image',
            field=models.ImageField(blank=True, upload_to='profile_image'),
        ),
    ]
