# **Creacion de variables de entorno**

Ejecute los siguientes comando configurar la region y zona:

```bash
gcloud config set project {project_name}
```

```bash
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a
```

Cree las variables de entorno con el id del poyecto, la region y la zona.

```bash
export PROJECT_ID=$(gcloud config get-value project)
export REGION=$(gcloud config get-value compute/region)
export ZONE=$(gcloud config get-value compute/zone)
export PRIVATENET='net-pruebas'
export PRIVATESUBNET='subnet-pruebas'
export FIREWALL_ALLOW_SSH='privatenet-allow-ssh'
export FIREWALL_ALLOW_INTERNAL='privatenet-allow-internal'
export FRONTEND='frontend'
export BACKEND='backend'
export WORKER='worker'
export FILE_SERVER='file-server'

```

# **Creacion de VPC**

Ejecute el siguiente comando para crear una red privada

```bash
gcloud compute networks create $PRIVATENET --subnet-mode=custom
```

Ejecutar el sigueinte comando para crear una subred privada **<name_privatesubnet>** 

```bash
gcloud compute networks subnets create $PRIVATESUBNET \
--network=$PRIVATENET \
 --region=$REGION \
 --range=172.16.0.0/24
```

# **Creacion de reglas de Firewall**

Ejecute el siguiente comando para permitir el acceso a todas las maquinas desde local.

```bash
gcloud compute firewall-rules create $FIREWALL_ALLOW_SSH \
--direction=INGRESS \
--priority=1000 \
--network=$PRIVATENET \
--action=ALLOW \
--rules=tcp:22,tcp:8080,tcp:5001 \
--source-ranges=0.0.0.0/0
```

Ejecute el siguiente comando para permitir todas las comunicaciones entre las redes internas.

```bash
gcloud compute firewall-rules create $FIREWALL_ALLOW_INTERNAL \
 --direction=INGRESS \
 --priority=1000 \
 --network=$PRIVATENET \
 --action=ALLOW \
 --rules=tcp:0-65535,udp:0-65535,icmp \
 --source-ranges=172.16.0.0/24
```

# **Creacion de Maquinas Virtuales**

Ejecute el siguiente comando para crear las máquinas virtuales necesarias para la ejecución de la aplicación.

```bash
gcloud compute instances create $FRONTEND \
--subnet $PRIVATESUBNET \
--zone $ZONE \
--private-network-ip 172.16.0.4

gcloud compute instances create $BACKEND \
--subnet $PRIVATESUBNET \
--zone $ZONE \
--private-network-ip 172.16.0.5

gcloud compute instances create $WORKER \
--subnet $PRIVATESUBNET \
--zone $ZONE \
--private-network-ip 172.16.0.6 \
--no-address


gcloud compute instances create $FILE_SERVER \
--subnet $PRIVATESUBNET \
--zone $ZONE \
--private-network-ip 172.16.0.7 \
--no-address
```

# Configuració de SQL

Con respecto a la instancia de SQL, se crea con el servio de Cloud SQL de Google, seleccionando como motor Postgres. Las características son las siguientes:
- Versión: 14.
- Ambiente: Desarrollo.
- Region y Zona: US Central 1 - a.
- VCPU: 1
- RAM: 4
- SSD: 10GB sin aumentos automáticos.
- Sin IP pública y se crea una conexión privada entre Google y nuestra VPC con rango 172.16.2.0/14.
- Sin Copias de seguridad ni protección de eliminación.
- Se deja el restante por defecto.

Mientras se crea la instancia de SQL, se instala el cliente de postgres en cualquiera de las instancias de Compute Engine, con la finalidad de entrar al abase de datos y poder crear la base de datos y el esquema a utilizar por el desarrollo. Para ello en la consola como root se ejecuta lo siguiente:

```bash
apt-get update && apt-get install postgresql-client -y
```

Una vez instalado el cliente, conectarse a la base de datos con el siguiente comando:


```bash
psql -h {ip-db} -U postgres
```

La contraseña que estamos utilizando para la base de datos es SuP3r$3cUr#P$$!!

Una vez en la base de datos ejecutamos lo siguiente para poder configurarla según se necesita en el desarrollo:

```bash
CREATE DATABASE compress_database;
\connect compress_database;
CREATE SCHEMA compress_schema;
```

# **Configuración del NFS**

Para configurar el sistema de archivos compartidos, es necesario configurar el servicio en la máquina que se designó para tal rol (**file-server**). Utilizaremos nfs-kernel-server, para ello ejecutamos el siguiente comando en la consola como root

```bash
apt-get update -y && apt-get install nfs-kernel-server -y
```

Creamos la carpeta que se hará visible para las otras instancias:

```bash
mkdir -p /shared/files
```

Cambiamos los permisos del directorio para que se ajusten a lo solicitado por el servicio:

```bash
chown nobody:nogroup /shared/files/
```

Ahora, limitamos el acceso al NFS a los servidores locales:

```bash
nano /etc/exports
/shared/files/   172.16.0.0/24(rw,sync,no_root_squash,no_subtree_check)
```

Por último, reiniciamos el servicio para que apliquen los cambios:

```bash
systemctl restart nfs-server
```

Revisamos que el servicio se encuentre corriendo:

```bash
systemctl status nfs-server
```

Del lado del cliente instalamos los paquetes necesarios con el siguiente comando:

```bash
apt-get update && apt-get install nfs-common -y
```

Montamos las unidades compartidas y comprobamos que cuando se crea un archivo en un lado es accesible en el otro

Cliente 1
```bash
cd
mkdir test
mount 172.16.0.7:/shared/files ./test/
cd ./test
echo "esto es una prueba" >> prueba.txt
sha256sum prueba.txt
```

Cliente 2
```bash
cd
mkdir test
mount 172.16.0.7:/shared/files ./test/
cd ./test
ls -lha   #Debe de existir el archivo prueba.txt
sha256sum prueba.txt
```

El hash debe de coincidir.

# Configuración de Instancias

Ahora, se instala docker en todas las instancias menos en la asignada con el rol de file-system. Para ellos se siguen los siguientes pasos como root:

```bash
apt-get update && apt-get install ca-certificates curl gnupg
mkdir -m 0755 -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update && apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
```

Descargamos las configuraciones del repositorio 

```bash
git clone https://github.com/camandhuercue/Entrega-1---Sistema-de-Conversi-n-Cloud.git
```

En las máquinas del worker y backend en la carpeta del proyecto se crea la carpeta files:

- Backend:

```bash
cd Entrega-1---Sistema-de-Conversi-n-Cloud/Entrega_3/Backend/
mkdir files
```

- Worker

```bash
cd Entrega-1---Sistema-de-Conversi-n-Cloud/Entrega_3/Worker
mkdir files
```

Montamos la carpeta compartida en la ruta creada:

```bash
mount 172.16.0.7:/shared/files ./files/
```

Por cada uno de los roles se tiene un archivo **docker-compose.yml** el cual tiene las configuraciones específicas.

Para configurar cada Rol se debe de ejecutar lo siguiente:


- Frontend:

```bash
cd Entrega-1---Sistema-de-Conversi-n-Cloud/Entrega_3/Frontend/
docker compose up
```

- Backend:

Se debe de modificar la IP de la base de datos:

```bash
nano Entrega-1---Sistema-de-Conversi-n-Cloud/Entrega_3/Backend/BackEnd/Dockerfile
```

Se debe de modificar la IP de la base de datos en la sección **DB_HOST**, luego ejecutar lo siguiente:

```bash
cd Entrega-1---Sistema-de-Conversi-n-Cloud/Entrega_3/Backend/
docker compose up
```

- Worker

Se debe de modificar la IP de la base de datos:

```bash
nano Entrega-1---Sistema-de-Conversi-n-Cloud/Entrega_3/Worker/Queue/queue_api/__init__.py
```
Allí ponemos en el string de la base de datos la IP que nos haya asignado el servicio.

Luego ejecutamos lo siguiente:

```bash
cd Entrega-1---Sistema-de-Conversi-n-Cloud/Entrega_3/Worker
docker compose up
```
