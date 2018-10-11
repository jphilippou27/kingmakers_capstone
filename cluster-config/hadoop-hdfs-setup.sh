#!/bin/bash
# 
# Set up Hadoop environment on master and slave nodes.
# root_hdfs_setup.sh should have already been run as root user.
# This script should be run as hadoop user.
# 
# SLAVES SHOULD ALREADY HAVE HADOOP INSTALLED, BUT NOT CONFIGURED.

if [ ! "$(whoami)" == "hadoop" ]; then
  echo "This script must be run as the hadoop user."
  exit 1
fi

if [ "$HOSTNAME" == "cap1.w210.mids" ]; then
  echo "[STATUS] On cap1, setting up SSH access and preparing slaves..."
  eval "$(ssh-agent)"
  ssh-add /home/hadoop/.ssh/id_rsa
  for REMOTE_HOST in 0.0.0.0 cap1 cap2; do
	ssh-keyscan -H $REMOTE_HOST >> ~/.ssh/known_hosts
    ssh $REMOTE_HOST 'rm -rf /data/*'
  done
fi

echo "[STATUS] Configuring default Bash profile..."
echo "export JAVA_HOME=\"$(readlink -f $(which javac) | grep -oP '.*(?=/bin)')\"" >> ~/.bash_profile
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

echo "[STATUS] Java version:"
$JAVA_HOME/bin/java -version

if [ "$HOSTNAME" == "cap1.w210.mids" ]; then
  echo "[STATUS] On cap1, writing Hadoop configuration files..."
  cd $HADOOP_HOME/etc/hadoop
  echo "[STATUS] Changed directory to:"
  pwd
  echo "[STATUS] Adding JAVA_HOME variable to hadoop-env.sh..."
  echo "export JAVA_HOME=\"$JAVA_HOME\"" >> ./hadoop-env.sh
  echo "[STATUS] Overwriting core-site.xml..."
  cat <<\EOF > ./core-site.xml
<?xml version="1.0"?>
<configuration>
  <property>
    <name>fs.defaultFS</name>
	<value>hdfs://cap1/</value>
  </property>
</configuration>
EOF
  echo "[STATUS] core-site.xml is now:"
  echo "------------------------------"
  cat ./core-site.xml
  echo "------------------------------"
  
  echo "[STATUS] Overwriting yarn-site.xml..."
  cat <<\EOF > ./yarn-site.xml
<?xml version="1.0"?>
<configuration>
    <property>
      <name>yarn.resourcemanager.hostname</name>
      <value>cap1</value>
    </property>
    <property>
      <name>yarn.nodemanager.aux-services</name>
      <value>mapreduce_shuffle</value>
    </property>
    <property>
       <name>yarn.resourcemanager.bind-host</name>
       <value>0.0.0.0</value>
     </property>
     <property>
        <name>yarn.nodemanager.resource.cpu-vcores</name>
        <value>4</value>
    </property>
    <property>
      <name>yarn.scheduler.maximum-allocation-mb</name>
      <value>8192</value>
    </property>
    <property>
      <name>yarn.nodemanager.resource.memory-mb</name>
      <value>28672</value>
    </property>
    <property>
      <name>yarn.scheduler.minimum-allocation-mb</name>
      <value>2048</value>
    </property>
</configuration>
EOF
  echo "[STATUS] yarn-site.xml is now:"
  echo "-------------------------------"
  cat ./yarn-site.xml
  echo "-------------------------------"

  echo "[STATUS] Overwriting mapred-site.xml..."
  cat <<\EOF > ./mapred-site.xml
<?xml version="1.0"?>
<configuration>
  <property>
    <name>mapreduce.framework.name</name>
	<value>yarn</value>
  </property>
</configuration>
EOF
  echo "[STATUS] mapred-site.xml is now:"
  echo "--------------------------------"
  cat ./mapred-site.xml
  echo "--------------------------------"
  
  echo "[STATUS] Overwriting hdfs-site.xml..."
  cat <<\EOF > ./hdfs-site.xml
<?xml version="1.0"?>
<configuration>
  <property>
    <name>dfs.datanode.data.dir</name>
	<value>file:///data/datanode</value>
  </property>
  
  <property>
    <name>dfs.namenode.name.dir</name>
	<value>file:///data/namenode</value>
  </property>
  
  <property>
    <name>dfs.namenode.checkpoint.dir</name>
	<value>file:///data/namesecondary</value>
  </property>
</configuration>
EOF
  echo "[STATUS] hdfs-site.xml is now:"
  echo "--------------------------------"
  cat ./hdfs-site.xml
  echo "--------------------------------"
  
  echo "[STATUS] rsyncing current directory to slave nodes..."
  rsync -a /opt/hadoop/etc/hadoop/* hadoop@cap2:/opt/hadoop/etc/hadoop/
  # repeat for each slave
  
  echo "[STATUS] Overwriting slaves..."
  echo "cap1" > slaves
  echo "cap2" >> slaves
  echo "[STATUS] slaves is now:"
  echo "-----------------------"
  cat ./slaves
  echo "-----------------------"
  echo "[STATUS] Coping slaves to workers..."
  cp slaves workers
  echo "[STATUS] ...done"
fi

echo "[STATUS] Completed!"

