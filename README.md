# RSS Feed Django Project
Welcome to the RSS Feed Django project! 

## Table of Contents
* [About the Project](#about-the-project)
* [Build With](#build-with)
* [Setup](#setup)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)

* [Running the Project](#running-the-project)
* [License](#license)
* [Contributing](#contributing)



## About the Project
This project is a web application built with Django Rest framework for content aggregation from RSS Feeds. This README file will guide you through the setup process, provide instructions for running the project, and explain how to contribute to its development.


## Build With
* [![Django][django.js]][django-url]
* [![Django Rest Framework][Django Rest Framework.js]][Django Rest Framework-url]


## Setup

### Prerequisites
Before setting up the RSS Feed Django project, ensure that you have the following prerequisites installed on your machine:
- [![Python][Python.js]][Python-url]
- [![PIP][PIP.js]][PIP-url]
- [![Github][Github.js]][Github-url]


### Installation
Follow these steps to set up the project:

Clone the repository using Git:

```bash
git https://github.com/rezatn0934/RSS-Feed-Aggregator.git
```

Create a virtual environment (optional but recommended):
```bash
python3 -m venv env
```

Activate the virtual environment:

For Windows:

```bash
env\Scripts\activate
```
For macOS/Linux:

```bash
source env/bin/activate
```
Install the project dependencies:

```bash
pip install -r requirements.txt
```
This command will install all the required Python packages listed in the requirements.txt file.

Set up the database:

```bash
python manage.py migrate
```
This will apply the database migrations and create the necessary tables.

Create a superuser account (admin):

```bash
python manage.py createsuperuser
```
Follow the prompts to set a phone number and password for the admin account.

Congratulations! The RSS Feed Django project has been successfully set up on your machine.


### Running the Project
To run the RSS Feed Django project, follow these steps:

Activate the virtual environment (if not already activated):

For Windows:

```bash
env\Scripts\activate
```
For macOS/Linux:

```bash
source env/bin/activate
```
Start the server:

```bash
python manage.py runserver
```

### License
![MIT][MIT.js]


### Contributing
We welcome contributions to the RSS Feed Django project. If you'd like to contribute, please follow these steps:

Fork the repository on GitHub.

Clone your forked repository to your local machine:

```bash
git clone https://github.com/rezatn0934/RSS-Feed-Aggregator.git
```
Create a new branch for your changes:


```bash
git checkout -b feature/your-feature-name
```
Make the necessary changes and commit them:


```bash
git commit -m "Add your commit message here"
```
Push your changes to your forked repository:

```bash
git push origin feature/your-feature-name
```
Open a pull request on the original repository, describing your changes and explaining why they should be merged.

Wait for the project maintainers to review your pull request. Once approved, your changes will be merged into the main project.

Thank you for your interest in contributing to the RSS Feed Django project! We appreciate your help.

[django.js]: https://img.shields.io/badge/Django-F77FBE?style=for-the-badge&logo=django&logoColor=black
[django-url]: https://www.djangoproject.com/
[Django Rest Framework.js]: https://img.shields.io/badge/Django%20Rest%20Framework-blue?style=for-the-badge
[Django Rest Framework-url]: https://www.django-rest-framework.org/

[Python.js]: https://img.shields.io/badge/Python-red?style=for-the-badge&logo=python&logoColor=black
[Python-url]: https://www.python.org/
[PIP.js]: https://img.shields.io/badge/PIP_(Python_package_manager)-blue?style=for-the-badge&logo=pypi&logoColor=white

[PIP-url]: https://pypi.org/
[Github.js]: https://img.shields.io/badge/GitHub-green?style=for-the-badge&logo=github&logoColor=black
[Github-url]: https://github.com/
[MIT.js]: https://img.shields.io/badge/License-MIT-F77FBE.svg
[MIT-url]: https://www.python.org/
