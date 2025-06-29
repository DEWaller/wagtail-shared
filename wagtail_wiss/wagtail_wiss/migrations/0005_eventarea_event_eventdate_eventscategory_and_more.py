# Generated by Django 5.2.2 on 2025-06-09 21:07

import datetime
import django.db.models.deletion
import modelcluster.fields
import uuid
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtail_wiss', '0004_gallery_menu_news_category_galleryitem_menuitem_and_more'),
        ('wagtailcore', '0094_alter_page_locale'),
        ('wagtailimages', '0027_image_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventArea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('translation_key', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('locale', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='wagtailcore.locale', verbose_name='locale')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sites_events_areas', to='wagtailcore.site')),
            ],
            options={
                'verbose_name': 'Event area',
                'verbose_name_plural': 'Event areas',
                'ordering': ['name'],
                'abstract': False,
                'unique_together': {('translation_key', 'locale')},
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('translation_key', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('title', models.CharField(max_length=255)),
                ('description', wagtail.fields.RichTextField(blank=True, null=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('geolocation', models.CharField(blank=True, max_length=250, null=True)),
                ('slug', models.SlugField(default='', help_text='URL slug, try to keep it short', max_length=80)),
                ('ocr_text', models.TextField(blank=True, help_text='Text extracted from the image using OCR, it has limitations. This is not used for anything yet.', verbose_name='OCR text')),
                ('legacy_html', models.TextField(blank=True, null=True)),
                ('archive', models.BooleanField(default=False)),
                ('address', models.CharField(blank=True, max_length=250, null=True)),
                ('zoom', models.SmallIntegerField(blank=True, null=True)),
                ('use_page_title', models.BooleanField(default=False, help_text='Append the title of the linked page to the link text.')),
                ('url_link', models.URLField(blank=True, null=True)),
                ('image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
                ('locale', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='wagtailcore.locale', verbose_name='locale')),
                ('page_link', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailcore.page')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sites_events', to='wagtailcore.site')),
                ('areas', models.ManyToManyField(blank=True, related_name='events_areas', to='wagtail_wiss.eventarea')),
            ],
            options={
                'verbose_name': 'Event',
                'verbose_name_plural': 'Events',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EventDate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(default=datetime.date.today, help_text='Start date of the recurrence.')),
                ('end_date', models.DateField(blank=True, help_text='End date of the recurrence.', null=True)),
                ('frequency', models.IntegerField(choices=[(3, 'Daily'), (2, 'Weekly'), (1, 'Monthly'), (0, 'Yearly')], default=3, help_text='Frequency of recurrence.')),
                ('interval', models.PositiveIntegerField(default=1, help_text='Interval for the recurrence (e.g., every 1 week).')),
                ('event', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_dates', to='wagtail_wiss.event')),
            ],
            options={
                'verbose_name': 'Event date',
                'verbose_name_plural': 'Event dates',
            },
        ),
        migrations.CreateModel(
            name='EventsCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('translation_key', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('name', models.CharField(max_length=255, null=True)),
                ('locale', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='wagtailcore.locale', verbose_name='locale')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sites_events_categories', to='wagtailcore.site')),
            ],
            options={
                'verbose_name': 'Events Category',
                'verbose_name_plural': 'Events categories',
                'abstract': False,
                'unique_together': {('translation_key', 'locale')},
            },
        ),
        migrations.AddField(
            model_name='event',
            name='categories',
            field=models.ManyToManyField(blank=True, related_name='events_categories', to='wagtail_wiss.eventscategory'),
        ),
        migrations.CreateModel(
            name='EventDateInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='date_instances', to='wagtail_wiss.event')),
            ],
            options={
                'ordering': ['date'],
                'indexes': [models.Index(fields=['date'], name='wagtail_wis_date_3d55af_idx')],
                'unique_together': {('event', 'date')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='event',
            unique_together={('translation_key', 'locale')},
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=255)),
                ('locale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wagtailcore.locale')),
            ],
            options={
                'verbose_name': 'Label',
                'verbose_name_plural': 'Labels',
                'unique_together': {('key', 'locale')},
            },
        ),
    ]
