#!/bin/bash
# Master node root user should have SSH access to the slaves
# If no key, make one with `ssh-keygen -f id_rsa -t rsa -N ''`
# then transfer to the slaves

# Echo shell commands and expanded variables before executing
set -x

HADOOP_USER_PASSWORD="******"
JUPYTERHUB_USER_PASSWORD="******"
HIVEUSER_POSTGRES_PASSWORD="******"

cat > /etc/hosts <<EOF
127.0.0.1 localhost localhost.localdomain
10.73.190.33 cap1 cap1.w210.mids
10.73.190.37 cap2 cap2.w210.mids

EOF

yum update -y
yum install -y bzip2

# setup disks, 
# only necessary on multi-disk machines
# DISK=$(fdisk -l | grep -E 10[0-9]+.*GB | tr -d ':' | cut -d' ' -f2)
# mkfs.xfs $DISK


# Download and install anaconda
mkdir -p /opt
rm -rf /opt/anaconda3
wget -O /opt/anaconda3.sh https://repo.anaconda.com/archive/Anaconda3-5.3.0-Linux-x86_64.sh
cd /opt
chmod +x anaconda3.sh
./anaconda3.sh -b -p /opt/anaconda3
echo 'PATH=/opt/anaconda3/bin:$PATH' >> /root/.bash_profile
source /root/.bash_profile
# install pyspark
pip install --upgrade pip
pip install pyspark
if [ "$HOSTNAME" == "cap1.w210.mids" ]; then
  yum install -y nodejs
  npm install -g configurable-http-proxy
  pip install jupyterhub
  useradd jupyterhub
  cd /home/jupyterhub
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout mycert.key -out mycert.pem
  chown -R jupyterhub:jupyterhub mycert.key
  chown -R jupyterhub:jupyterhub mycert.pem
  cd /root
  echo <<\EOF >> /root/jupyterhub_config.py
c.Authenticator.admin_users = ['matt']
c.JupyterHub.ssl_key = '/home/jupyterhub/mycert.key'
c.JupyterHub.ssl_cert = '/home/jupyterhub/mycert.pem'
c.JupyterHub.spawner_class = 'jupyterhub.spawner.LocalProcessSpawner'"
c.LocalProcessSpawner.environment = {
  'JAVA_HOME': '/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.181-3.b13.el7_5.x86_64',
  'SPARK_HOME': '/opt/spark',
  'HADOOP_HOME': '/opt/hadoop',
  'HADOOP_CONF_DIR': '/opt/hadoop/etc/hadoop',
  'HADOOP_MAPRED_HOME': '/opt/hadoop',
  'HADOOP_HDFS_HOME': '/opt/hadoop',
  'HIVE_HOME': '/opt/hive',
  'YARN_HOME': '/opt/hadoop',
  'YARN_CONF_DIR': '/opt/hadoop/etc/hadoop',
  'PYSPARK_PYTHON': '/opt/anaconda3/bin/python',
  'PYSPARK_DRIVER_PYTHON': '/opt/anaconda3/bin/python'
}
EOF

fi

echo 'PATH=/opt/anaconda3/bin:$PATH' >> /home/jupyterhub/.bash_profile

# cleanup
rm -f /opt/anaconda3.sh


# Download and install Java and system tools
yum -y install https://centos7.iuscommunity.org/ius-release.rpm
yum -y install java-1.8.0-openjdk-devel iptables-services wget rsync net-tools htop vim screen tmux unzip
echo "export JAVA_HOME=\"$(readlink -f $(which javac) | grep -oP '.*(?=/bin)')\"" >> ~/.bash_profile
source ~/.bash_profile


# Download and install nmon
mkdir -p /opt/nmon && rm -rf /opt/nmon/* && cd /opt/nmon
wget -O nmon.tar.gz http://sourceforge.net/projects/nmon/files/nmon16g_x86.tar.gz
tar xzvf nmon.tar.gz
chmod +x nmon16g_x86_rhel72
rm -f /usr/bin/nmon
mv nmon16g_x86_rhel72 /usr/bin/nmon
cd /opt
rm -rf nmon/


# setup SSH access to this server
ssh-keygen -t rsa -b 2048 -C 'auto-generated' -N '' -f /root/.ssh/id_rsa
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys


# install Hadoop
mkdir -p /opt && rm -rf /opt/hadoop
curl http://www-us.apache.org/dist/hadoop/common/hadoop-3.1.1/hadoop-3.1.1.tar.gz | tar xz -C /opt --show-transformed --transform='s,/*[^/]*,hadoop,'
cat <<\EOF >> ~/.bash_profile
export HADOOP_HOME=/opt/hadoop
export HADOOP_MAPRED_HOME=$HADOOP_HOME
export HADOOP_HDFS_HOME=$HADOOP_HOME
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export YARN_HOME=$HADOOP_HOME
export YARN_CONF_DIR=$YARN_HOME/etc/hadoop
export HIVE_HOME=/opt/hive
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$HIVE_HOME/bin
export PYSPARK_PYTHON=/opt/anaconda3/bin/python
export PYSPARK_DRIVER_PYTHON=/opt/anaconda3/bin/python
EOF
source ~/.bash_profile
useradd hadoop
echo "hadoop:$HADOOP_USER_PASSWORD" | chpasswd
mkdir -p /data && rm -rf /data/*
chown -R hadoop.hadoop /data
chown -R hadoop.hadoop /opt/hadoop
cd /root
chmod a+x ./hadoop-hdfs-setup.sh
rm -f /home/hadoop/hadoop-hdfs-setup.sh
mv hadoop-hdfs-setup.sh /home/hadoop/

# STEP BELOW IS REALLY ONLY NECESSARY IF YOU DIDN'T GET THE PRECONFIGURED HADOOP FILES
# Before running the script below, the "hadoop" user on the master node should have SSH access to the "hadoop" accounts on the slave nodes.
# Ensure that this works by appending the root user's public key to the slave user's authorized_keys files:
# ssh root@$cap1_IP 'cat /home/hadoop/.ssh/id_rsa.pub' | ssh root@$cap2_IP 'cat > /home/hadoop/.ssh/authorized_keys && chown -R hadoop:hadoop /home/hadoop/.ssh/authorized_keys && chmod 600 /home/hadoop/.ssh/authorized_keys'
cd /home/hadoop
sudo -u hadoop /home/hadoop/hadoop-hdfs-setup.sh


# install Spark
mkdir -p /opt && rm -rf /opt/spark
cd /opt
wget -O - http://apache.mirror.globo.tech/spark/spark-2.3.2/spark-2.3.2-bin-hadoop2.7.tgz | tar xzf -
ln -s spark-2.3.2-bin-hadoop2.7 spark
echo export SPARK_HOME=\"/opt/spark\" >> /root/.bash_profile
source /root/.bash_profile
cat <<\EOF > /opt/spark/conf/slaves
cap1
cap2
EOF


# install Hive
if [ "$HOSTNAME" == "cap1.w210.mids" ]; then
  yum install -y postgresql-server
  postgresql-setup initdb
  
  # Make sure that listen='*' and standard_conforming_strings=off
  cat /etc/postgresql/9.1/main/postgresql.conf | grep -e listen -e standard_conforming_strings
  #  EXPECT: listen_addresses = '*'
  #  EXPECT: standard_conforming_strings = off
  
  # Next set up remote access
  cat <<\EOF >> /var/lib/pgsql/data/pg_hba.conf
host    all            all              10.73.190.33/32        md5
host    all            all              10.73.190.37/32        md5
EOF
  systemctl restart postgresql
  systemctl enable postgresql
  
  # sudo -u postgres psql
  # create user hiveuser;
  # alter user hiveuser with superuser;
  # create database metastore owner hiveuser;
  # \q
  # sudo -u postgres psql -U hiveuser -d metastore
  # ... enter password
  # \i /opt/hive/scripts/metastore/upgrade/postgres/hive-schema-3.1.0.postgres.sql
  # \q
  # Then, drop in the hive-site.xml.master into cap1:/opt/hive/conf/hive-site.xml (then ln -s to /opt/spark/conf/hive-site.xml)
  # Drop hive-site.xml.slave into cap2:/opt/hive/conf/hive-site.xml (ln -s to cap2:/opt/spark/conf/hive-site.xml)
  
fi

# install postgresql JDBC driver for Hive
yum install postgresql-jdbc
ln -s /usr/share/java/postgresql-jdbc.jar /opt/hive/lib/postgresql-jdbc.jar

## ONLY SET PROPERTY hive.metastore.uris TO cap1.w210.mids ON THE SLAVE NODE
## LEAVE THIS PROPERTY UNDEFINED IN hive-site.xml IN THE MASTER NODE
# <property>
#   <name>hive.metastore.uris</name>
#   <value>thrift://cap1.w210.mids:10000</value>
#   <description>Thrift URI for the remote metastore. Used by metastore client to connect to remote metastore.</description>
# </property>

cd /opt
curl http://www-us.apache.org/dist/hive/hive-3.1.0/apache-hive-3.1.0-bin.tar.gz | tar zx -C /opt --show-transformed --transform='s,/*[^/]*,hive,'
sudo chown -R hadoop:hadoop /opt/hive
sudo -u hadoop hdfs dfs -mkdir -p /tmp
sudo -u hadoop hdfs dfs -mkdir -p /user/hive/warehouse
sudo -u hadoop hdfs dfs -chmod g+w /tmp
sudo -u hadoop hdfs dfs -chmod g+w /user/hive/warehouse


# setup firewall to disallow access to world and allow access to moi
systemctl restart iptables
# Generated by iptables-save v1.4.21 on Sat Oct  6 09:29:26 2018
iptables-restore <<\EOF
*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [1183:143635]
-A INPUT -s 127.0.0.1/32 -p tcp -j ACCEPT
-A INPUT -s 10.73.190.37/32 -p tcp -j ACCEPT
-A INPUT -s 10.73.190.33/32 -p tcp -j ACCEPT
-A INPUT -s 50.89.240.170/32 -p tcp -j ACCEPT
-A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
-A INPUT -p icmp -j ACCEPT
-A INPUT -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT
-A INPUT -j REJECT --reject-with icmp-host-prohibited
-A FORWARD -j REJECT --reject-with icmp-host-prohibited
COMMIT
# Completed on Sat Oct  6 09:29:26 2018
EOF

# Start services (HDFS + Yarn + Spark)
if [ "$HOSTNAME" == "cap1.w210.mids" ]; then
  cd /opt/hadoop
  # Setup Hadoop
  sudo -u hadoop hdfs namenode -format
  # Start Hadoop
  sudo -u hadoop sbin/start-dfs.sh
  # Start Yarn
  sudo -u hadoop sbin/start-yarn.sh
  # Start Hive
  cd /opt/hive
  sudo -u hadoop schematool -dbType derby -initSchema
  
  # check status
  hdfs dfsadmin -report
  yarn node -list
fi



echo "finished. review setup script comments for further instructions"

# HDFS webUI port: 9870
# Yarn ResourceManager webUI port: 8088
# Hive port: 10000 (10002 for webUI)


