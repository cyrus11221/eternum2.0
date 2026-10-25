from django.db import migrations


def update_category_names(apps, schema_editor):
    Category = apps.get_model('memorial', 'Category')
    SystemSetting = apps.get_model('memorial', 'SystemSetting')
    names_by_slug = {
        'hardwood': 'Hardwood Caskets',
        'metal': 'Metal Caskets',
        'eco': 'Eco-friendly Caskets',
        'artisanal': 'Custom Caskets',
    }
    for slug, name in names_by_slug.items():
        Category.objects.filter(slug=slug).update(name=name)
    SystemSetting.objects.filter(
        setting_key='ftc_compliance_notice',
        setting_value='Under FTC 16 CFR Part 453, mortuaries cannot reject or penalize third-party casket deliveries.',
    ).update(
        setting_value='The FTC Funeral Rule includes protections for people purchasing funeral goods. Review current FTC guidance for details.'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('memorial', '0003_alter_order_status_alter_product_dispatch_type'),
    ]

    operations = [
        migrations.RunPython(update_category_names, migrations.RunPython.noop),
    ]
