# Generated by Django 4.2 on 2024-06-05 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Адрес электронной почты')),
                ('is_superuser', models.BooleanField(default=False, verbose_name='Статус суперпользователя')),
                ('is_staff', models.BooleanField(default=False, verbose_name='Статус персонала')),
                ('email_confirmed', models.BooleanField(default=False, verbose_name='Адрес электронной почты подтвержден')),
                ('url_hash', models.CharField(blank=True, max_length=128, null=True, verbose_name='Хэш')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
                'db_table': 'users',
            },
        ),
    ]
