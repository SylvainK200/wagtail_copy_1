# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-29 04:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("snippetstests", "0005_multisectionrichtextsnippet_richtextsection"),
    ]

    operations = [
        migrations.CreateModel(
            name="StandardSnippetWithCustomPrimaryKey",
            fields=[
                (
                    "snippet_id",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
                ("text", models.CharField(max_length=255)),
            ],
        ),
    ]
