# Generated by Django 4.2.4 on 2023-09-08 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='authors',
            field=models.ManyToManyField(related_name='books', to='Users.author'),
        ),
    ]