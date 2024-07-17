# Repo-Ciqimet
 Proyecto backend-ciquimet

Instalación: -Tenienod instalado Python, Github y ENV, escribibos los siguientes codigos:

    pip install git+https://github.com/Usuario/Proyecto | para descargar e instalar el proyecto se usa este comando en el CMD para Windows y Bash para linux, usa la dirección URL de este repositorio
    una vez instalado accede a la carpeta con "ls" para saber el nombre de la carpeta y con "cd [nombre de carpeta]" para acceder
    si no tienes env escribre "pip install env" y luego escribe "python -m venv env" Para instalar el entorno de desarollo (env) en el que se utilizaran paquetes de python propios
    En caso de usar windows, usa el codigo "env\scripts\activate" para habilitar el entorno de desarollo, si se usa un servidor acceda con su propio env.
    pip install -r requirements.txt | primero tiene que abrir la carpeta del proyecto donde se encuentra el archivo requrements.txt para instalar todos los paquetes necesarios -Instalado todo el proyecto, tiene que cambiar la configuración del archivo "[proyecto/Setup/setting.py]" en la sección de la base de datos, ajusta la configuración de acuerdo a la base de datos que tiene instalado de forma local o en AWS -Una vez esta la base de datos conectada al proyecto se realiza los siguientes codigos para preparar el entorno de la plataforma:
    python manage.py makemigrations
    python manage.py makemigrations api
    python manage.py migrate
    python manage.py migrate api
    Los codigos previos son para crear y migrar la base de datos de la plataforma en la base de datos que tiene conectividad con el proyecto.
