# Generated by Django 2.2 on 2019-04-07 06:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('categoryID', models.AutoField(primary_key=True, serialize=False)),
                ('categoryName', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('courseID', models.AutoField(primary_key=True, serialize=False)),
                ('courseName', models.CharField(max_length=100)),
                ('courseCECU', models.PositiveIntegerField(default=0)),
                ('courseDescription', models.CharField(max_length=200)),
                ('courseStatus', models.CharField(max_length=1)),
                ('numOfModules', models.IntegerField(default=0)),
                ('totalEnrolled', models.IntegerField(default=0)),
                ('currentEnrolled', models.IntegerField(default=0)),
                ('categoryID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ICE.Category')),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('moduleID', models.AutoField(primary_key=True, serialize=False)),
                ('moduleTitle', models.CharField(max_length=100)),
                ('orderNumber', models.IntegerField()),
                ('numOfComponents', models.IntegerField(default=0)),
                ('numOfQuestions', models.IntegerField(blank=True, null=True)),
                ('passingMark', models.IntegerField(blank=True, null=True)),
                ('courseID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ICE.Course')),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=50, unique=True)),
                ('token', models.CharField(default='KqSqT6', editable=False, max_length=6)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('userID', models.AutoField(primary_key=True, serialize=False)),
                ('firstName', models.CharField(max_length=50)),
                ('lastName', models.CharField(max_length=50)),
                ('emailID', models.EmailField(max_length=50, null=True, unique=True)),
                ('userName', models.CharField(max_length=50, null=True, unique=True)),
                ('password', models.CharField(max_length=50, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Instructor',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('biography', models.CharField(max_length=250)),
            ],
            options={
                'abstract': False,
            },
            bases=('ICE.user',),
        ),
        migrations.CreateModel(
            name='Learner',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('totalCECU', models.PositiveIntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
            bases=('ICE.user',),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('questionID', models.AutoField(primary_key=True, serialize=False)),
                ('questionStatement', models.CharField(max_length=200)),
                ('qOption1', models.CharField(max_length=50)),
                ('qOption2', models.CharField(max_length=50)),
                ('qOption3', models.CharField(max_length=50)),
                ('qOption4', models.CharField(max_length=50)),
                ('answer', models.CharField(max_length=1)),
                ('moduleID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ICE.Module')),
            ],
        ),
        migrations.CreateModel(
            name='Component',
            fields=[
                ('componentID', models.AutoField(primary_key=True, serialize=False)),
                ('componentTitle', models.CharField(max_length=100)),
                ('componentText', models.CharField(blank=True, max_length=100, null=True)),
                ('componentImage', models.ImageField(blank=True, null=True, upload_to='images/')),
                ('orderNumber', models.IntegerField()),
                ('createdAt', models.DateField(auto_now_add=True)),
                ('updatedAt', models.DateField(auto_now=True)),
                ('moduleID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ICE.Module')),
            ],
        ),
        migrations.CreateModel(
            name='LearnerTakesCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completeStatus', models.CharField(max_length=1)),
                ('completionDate', models.DateField(blank=True, null=True)),
                ('currentModule', models.IntegerField(blank=True, null=True)),
                ('courseID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ICE.Course')),
                ('staffID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ICE.Learner')),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='instructorID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ICE.Instructor'),
        ),
    ]
