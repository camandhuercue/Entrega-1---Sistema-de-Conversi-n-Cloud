
# **Despliegue App en instancia de AWS**

## **1. Creación instancia**

Se inicializa una instancia en AWS a la cual se le asignan los siguientes parámetros:

* ***Name***: entrega_1-compresor_online
* ***Application and OS Images***: ubuntu Server 22.04 LTS
* ***Instance type***: t2.micro
* ***Key pair***: dev-cloud.pem (Usar una anteriormente creada o crear una nueva)
* ***Network settings***: Creación de reglas de seguridad necesarios para funcionamiento de la aplicación.

    * TCP, 22, 0.0.0.0/0 - SSH
    * TCP, 8080, 0.0.0.0/0 - Backend
    * TCP, 5001, 0.0.0.0/0 - Frontend

* ***Configure Storage***: 10Gb - GP2(SSD)

Con lo anterior se tiene la reconfiguración para poder lanzar la instancia.

Una vez la instancia se encuentra corriendo se procede a acceder a ella por medio de SSH, es importante que la llave cuente con permisos de lectura en caso de no tenerlos e puede ejecutar:

```bash
chmod 400 dev-cloud.pem
```

Con los permisos ya concedidos se accede a la instancia teniendo en cuenta la dirección que asigna AWS y que se puede visualizar en la pestaña de ***Connect to instance***

```bash
ssh -i "dev-cloud.pem" ubuntu@ec2-100-26-249-252.compute-1.amazonaws.com
```

## **2. Configuración instancia AWS**

Lo primero que se realiza estando dentro de la instancia es la instalacion de docker que puede ser encontrada en el siguiente [link](https://diarioprogramador.com/como-instalar-docker-en-ubuntu-server-20-04-22-04/), o siguiendo los pasos mencionados a continuacion:

1. Actualizar repositorios de Ubuntu Server

```bash
sudo apt update
```
```bash
sudo apt upgrade
```

2. Instalar dependencias

```bash
sudo su
```

```bash
apt install apt-transport-https ca-certificates curl software-properties-common -y
```

3. Agregar repositorio de Docker

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
```

```bash
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
```

4. Instalar Docker y Docker Compose

```bash
sudo apt update
```

```bash
sudo apt install docker-ce docker-compose -y
```

5. Activa el servicio de Docker

```bash
systemctl start docker
```

```bash
systemctl status docker
```

6. Comprobar funcionamiento de Docker

```bash
docker --version
```

```bash
sudo docker run hello-world
```

Cada uno de estos pasos estan especificados con mayor claridad en el [link de referencia](https://diarioprogramador.com/como-instalar-docker-en-ubuntu-server-20-04-22-04/).

## **3. Despliegue App**

Una vez instalado ***docker*** y ***docker-compose*** se procede a clonar el repositorio que contiene la aplicación.

```bash
git clone https://github.com/camandhuercue/Entrega-1---Sistema-de-Conversi-n-Cloud.git
```

Se consulta la direccion Ip privada de la maquina:

```bash
hostname -I
```

La ***<IP_HOST>*** obtenida debe cambiarse en los siguientes archivos del codigo:

* BackEnd/Dockerfile 
    - ENV DB_HOST="***<IP_HOST>***"

* FrontEnd/app.py
    - ip_backend = '***<IP_HOST>***:8080'

* Nginx/flask.conf  
    - server_name ***<IP_HOST>***
    - proxy_pass  http://***<IP_HOST>***:5000;

* Queue/queue_api/__init__.py
    - engine=create_engine('postgresql+psycopg2://compress_user:$$53eer3&777R@***<IP_HOST>***:5432/compress_database')

* Queue/tasks.py
    - app = Celery( 'tasks' , broker = 'redis://***<IP_HOST>***:6379/0' )

Seguido a esto se realiza el depsleigue con ayuda del archivo ***docker-compose.yml***:

```bash
 cd Entrega-1---Sistema-de-Conversi-n-Cloud/
```

```bash
docker compose up
```

En este punto se empiezan a configurar cada uno de los Docker por los cuales está compuesta la aplicación.

Puede darse el caso de que la base da datos no se cree correcta metne por ende sera necesario borrar todos los contenedores y las imagenes y volver a hacer uso de docker compose.

```bash
docker container ls -a
```

```bash
docker rm queue nginx frontend redis backend database
```

y las imagenes 

```bash
docker image ls
```

```bash
docker rmi queue nginx frontend redis backend database flask_base front_base postgres_base
```

Para finalmente volver a hacer uso de docker compose.

```bash
docker compose up
```

De esta manera el APP ya queda funcional y corriendo.

Para relaizar peticiones se hacen uso de las siguientes direcciones:

*  <IP_Intancia>:5001 (http://100.26.249.252:5001) - Frontend
*  <IP_Intancia>:8080 (http://100.26.249.252:8080) - Backend

## **4. Test POSTMAN**

Las pruebas y test realizados en postman se encuentran en el archivo Compress_API.json este debe ser importado al espacio de POSTMAN donde se testean los endpoints.

Inicialmente, se debe configurar la base_url tal como se muestra en la imagen, esta dirección es la IP pública de la instancia de AWS. 

![Postman URL Base.](/img/postman_1.jpg)

Se continúa al ejecutar la colección solo con los endpoints que se muestran a continuación. El motivo de esto emula la espera de la cola de compresión de las tareas.

![Postamn Run Collection.](/img/postman_2.jpg)

Pasados 30 segundos se ejecutan los endpoints faltantes, terminando de aplicar los test.

![Postamn Run Collection.](/img/postman_3.jpg)

Algunos de los Test planteados tienen como finalidad mostrar posible escenario que un usuario pueda llevar a cabo, esto quiere decir que un test fallido no necesariamente dice que el endpoint no es funcional.