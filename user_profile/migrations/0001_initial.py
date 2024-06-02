# Generated by Django 4.0.7 on 2024-06-02 10:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import user_profile.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('first_name', models.CharField(max_length=50, null=True)),
                ('last_name', models.CharField(max_length=50, null=True)),
                ('bio', models.TextField(default='', max_length=100)),
                ('date_of_birth', models.DateField(null=True, validators=[user_profile.models.validate_age])),
                ('address', models.CharField(max_length=100, null=True)),
                ('phone', models.CharField(max_length=10, null=True, validators=[user_profile.models.validate_phone_number])),
                ('gender', models.CharField(choices=[('MALE', 'Male'), ('FEMALE', 'Female'), ('OTHER', 'Other')], default='MALE', max_length=6)),
                ('profile_picture', models.ImageField(null=True, upload_to=user_profile.models.path_and_rename)),
                ('lat', models.DecimalField(decimal_places=6, max_digits=9, null=True)),
                ('long', models.DecimalField(decimal_places=6, max_digits=9, null=True)),
                ('age', models.IntegerField(blank=True, null=True)),
                ('zodiac', models.CharField(blank=True, choices=[('Aquarius', 'Aquarius'), ('Pisces', 'Pisces'), ('Aries', 'Aries'), ('Taurus', 'Taurus'), ('Gemini', 'Gemini'), ('Cancer', 'Cancer'), ('Leo', 'Leo'), ('Virgo', 'Virgo'), ('Libra', 'Libra'), ('Scorpio', 'Scorpio'), ('Sagittarius', 'Sagittarius'), ('Capricorn', 'Capricorn')], max_length=15, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserInterest',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(blank=True, max_length=20, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interest', to='user_profile.userprofile')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserDescription',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('height', models.CharField(choices=[('BELOW 4', 'Below 4'), ('4 to 5', '4 to 5'), ('5 to 6', '5 to 6'), ('ABOVE 6', 'Above 6')], default='4 to 5', max_length=10)),
                ('eye_color', models.CharField(choices=[('BLACK', 'Black'), ('BROWN', 'Brown'), ('BLUE', 'Blue'), ('GREEN', 'Green'), ('HAZEL', 'Hazel'), ('OTHER', 'Other')], default='BLACK', max_length=10)),
                ('hair_length', models.CharField(choices=[('LONG', 'Long'), ('SHOULDER LENGTH', 'Shoulder Length'), ('AVERAGE', 'Average'), ('SHORT', 'Short'), ('SHAVED', 'Shaved')], default='LONG', max_length=100)),
                ('hair_colour', models.CharField(choices=[('BLACK', 'Black'), ('BLONDE', 'Blonde'), ('BROWN', 'Brown'), ('RED', 'Red'), ('GREY', 'Grey'), ('BALD', 'Bald'), ('BLUE', 'Blue'), ('PINK', 'Pink'), ('GREEN', 'Green'), ('PURPLE', 'Purple'), ('OTHER', 'Other')], default='BLACK', max_length=10)),
                ('body_type', models.CharField(choices=[('THIN', 'Thin'), ('AVERAGE', 'Average'), ('FIT', 'Fit'), ('MUSCULAR', 'Muscular'), ('A LITTLE EXTRA', 'A Little Extra'), ('CURVY', 'Curvy')], default='AVERAGE', max_length=15)),
                ('religion', models.CharField(choices=[('HINDU', 'Hindu'), ('CHRISTIAN', 'Christian'), ('MUSLIM', 'Muslim'), ('BUDDHIST', 'Buddhist'), ('OTHER', 'Other')], default='HINDU', max_length=100)),
                ('relationship_status', models.CharField(choices=[('SINGLE', 'Single'), ('MARRIED', 'Married'), ('WIDOWED', 'Widowed'), ('SEPARATED', 'Separated')], default='SINGLE', max_length=100)),
                ('education', models.CharField(choices=[('HIGH SCHOOL', 'High School'), ('COLLEGE', 'College'), ('BACHELORS DEGREE', 'Bachelors Degree'), ('MASTERS', 'Masters'), ('PHD / POST DOCTORAL', 'PhD / Post Doctoral')], default='HIGH SCHOOL', max_length=100)),
                ('looking_for', models.CharField(choices=[('MALE', 'Male'), ('FEMALE', 'Female'), ('BOTH', 'Both')], default='BOTH', max_length=6)),
                ('is_completed', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='description', to='user_profile.userprofile')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserConnection',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('connections', models.ManyToManyField(to='user_profile.userprofile')),
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='connection', to='user_profile.userprofile')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Key',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('private_key', models.TextField(blank=True, null=True)),
                ('public_key', models.TextField(blank=True, null=True)),
                ('keys_owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='keys', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Heart',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('received_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='heart_receiver', to='user_profile.userprofile')),
                ('sent_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='heart_sender', to='user_profile.userprofile')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BlockedUser',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='blocked_users', to='user_profile.userprofile')),
                ('users', models.ManyToManyField(to='user_profile.userprofile')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
