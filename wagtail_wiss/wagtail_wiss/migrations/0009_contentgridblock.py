# Generated by Django 5.2.2 on 2025-06-24 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtail_wiss', '0008_remove_homepage_page_ptr_delete_defaultpage_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentGridBlock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Text & grid blocks',
            },
        ),
    ]
