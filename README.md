# Repo-Ciqimet
 Proyecto backend-ciquimet

Instalación: -Tenienod instalado Python, Github y ENV, escribibos los siguientes codigos:

    -escribe "pip install git+https://github.com/Luis122002/Repo-Ciqimet" para descargar e instalar el proyecto se usa este comando en el CMD para Windows y Bash para linux, usa la dirección URL de este repositorio
    -una vez instalado accede a la carpeta con "ls" para saber el nombre de la carpeta y con "cd [nombre de carpeta]" para acceder al proyecto
    -si no tienes env escribre "pip install env" y luego escribe "python -m venv env" Para instalar el entorno de desarollo (env) en el que se utilizaran paquetes de python propios.
    -En caso de usar windows, usa el codigo "env\scripts\activate" para habilitar el entorno de desarollo, si se usa un servidor acceda con su propio env.
    -escribe "pip install -r requirements.txt" para instalar todos los paquetes necesarios
    -Instalado todo el proyecto, tiene que cambiar la configuración del archivo "[proyecto/Setup/setting.py]" en la sección de la base de datos, ajusta la configuración de acuerdo a la base de datos que tiene instalado de forma local o en AWS
    -Si se prueba de forma local, utilizar archivo ".env" para configurar los parametros, los cuales son:

SECRET_KEY =
DEBUG=true
ALLOWED_HOSTS=*
CORS_ALLOWED_ORIGINS= (obsoleto)
CORS_ALLOWED_COMPLEMENT= (localhost)

#DATABASE_ENGINE=django.db.backends.postgresql
#DATABASE_URL=postgresql://root:----------
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=
DATABASE_USER=
DATABASE_PASSWORD=
DATABASE_HOST=
DATABASE_PORT=
baseURL = (localhost)
INTERNAL_MODE=true
    
    -Una vez esta la base de datos conectada al proyecto se realiza los siguientes codigos para preparar el entorno de la plataforma:
    python manage.py makemigrations
    python manage.py makemigrations api
    python manage.py migrate
    python manage.py migrate api
    Los codigos previos son para crear y migrar la base de datos de la plataforma en la base de datos que tiene conectividad con el proyecto.
   
para poder probarlo, se realiza:

   escribir en el terminal "python manage.py createsuperuser" y rellenar el campo de usuario, correo y contraseña
   Acceder a la base de datos y asignar el "first_name", el "last_name" y finalmente asignar el "rolname" como "administrador"
   insertar el archivo de pruebas "LocalHost.session.sql" que pobla registros de elementos, analisis y clientes como ejemplos
   
