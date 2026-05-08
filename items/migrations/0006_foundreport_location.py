from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0005_foundreport_lostreport_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='foundreport',
            name='location',
            field=models.ForeignKey(
                blank=True,
                help_text='Where the item was originally found.',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='found_item_locations',
                to='items.location',
            ),
        ),
    ]
