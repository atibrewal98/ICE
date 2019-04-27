# ICE

A platform to help improve creation and delivery of education courses for local staff. The company already provides opportunities for continuing education by offering in-house courses on a wide range of subjects. The platform revolves around the concept of learners, who are the staff of the company and can enroll in courses available for enrollment. Upon successful completion of the courses, they are awarded CECUs (Continuing Education Credit Units). Secondly, there are instructors who are involved with content creation and delivering educational material. The Human Resources Department can further review the courses to help better content creation proccess. The Administrator is responsible for enrollment.

## Getting Started

These instructions will help you get a copy of the repository setup on your local platform for testing and development purposes. 

### Installation

A step by step process that guides you through the installation to get your development up and running.

Install Django on your local environment:

```
pip install Django==2.2
```

Setup requests to import data from company HR database (A dummy database has been setup on Heroku for our testing purpose):

```
pip install requests
```

### Setup

Now to start with the setup of the code, we first clone the repo into our local machine.

```
git clone https://github.com/atibrewal98/ICE.git
```

After going into the ICE folder, we have to first setup the migrations.

```
python manage.py makemigrations ICE

python manage.py migrate
```

This will setup the database and models for use.

We have to create a superuser to manage the admin panel for the platform.

```
python manage.py createsuperuser
```

Once, the superuser is setup, we are ready to run the code using:

```
python manage.py runserver
```

## Technology Stack

* [Django](https://docs.djangoproject.com/en/2.2/) - The web framework used
* [HTML5](https://www.w3schools.com/html/html5_intro.asp) - Frotend Solution Stack
* [CSS](https://www.w3schools.com/css/) - Used to style the platform
* [Bootstrap](https://getbootstrap.com/docs/4.3/getting-started/introduction/) - Framework for building responsive solutions


## Authors

* [Ankit Tibrewal](https://github.com/atibrewal98) 
* [Juwon Lee](https://github.com/juwonlee1020) 
* [Mohammad Ahmad](https://github.com/mahmad97)
* [Shivansh Mittal](https://github.com/shivansh1905)
* [Subhayan Roy](https://github.com/sroy22)