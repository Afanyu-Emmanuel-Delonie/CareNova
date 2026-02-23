from django.db import migrations, models
import django.db.models.deletion


def seed_categories(apps, schema_editor):
    Category = apps.get_model('users', 'Category')
    names = [
        'Cardiology',
        'Dermatology',
        'Neurology',
        'Pediatrics',
        'Orthopedics',
        'Gynecology',
        'Psychiatry',
        'General Medicine',
    ]
    for name in names:
        Category.objects.get_or_create(name=name)


def unseed_categories(apps, schema_editor):
    Category = apps.get_model('users', 'Category')
    names = [
        'Cardiology',
        'Dermatology',
        'Neurology',
        'Pediatrics',
        'Orthopedics',
        'Gynecology',
        'Psychiatry',
        'General Medicine',
    ]
    Category.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_user_otp_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('icon', models.ImageField(blank=True, null=True, upload_to='category_icons/')),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.AddField(
            model_name='doctorprofile',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='doctors', to='users.category'),
        ),
        migrations.RunPython(seed_categories, unseed_categories),
    ]
