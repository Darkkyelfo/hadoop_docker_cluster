FROM centos:7
WORKDIR /opt
RUN (cd /lib/systemd/system/sysinit.target.wants/; for i in *; do [ $i == \
systemd-tmpfiles-setup.service ] || rm -f $i; done); \
rm -f /lib/systemd/system/multi-user.target.wants/*;\
rm -f /etc/systemd/system/*.wants/*;\
rm -f /lib/systemd/system/local-fs.target.wants/*; \
rm -f /lib/systemd/system/sockets.target.wants/*udev*; \
rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \
rm -f /lib/systemd/system/basic.target.wants/*;\
rm -f /lib/systemd/system/anaconda.target.wants/*;
RUN yum install net-tools -y \
&& yum -y install rpm-build \
&& yum install svn \
&& yum install wget -y \
&& yum install iputils -y \
&& yum -y install openssh openssh-server openssh-clients \
&& useradd -m hadoop \
&& (echo 'hadoop'; echo 'hadoop') | passwd hadoop \
&& echo -e "Port 22\n#AddressFamily any\nListenAddress 0.0.0.0\nListenAddress ::\nPubkeyAuthentication yes" >> /etc/ssh/sshd_config \
&& wget https://javajdk7778.s3.sa-east-1.amazonaws.com/jdk-8u202-linux-x64.tar.gz \
&& tar -xvf jdk-8u202-linux-x64.tar.gz && rm -rf jdk-8u202-linux-x64.tar.gz && mv jdk1.8.0_202/ jdk \
&& wget --no-check-certificate https://dlcdn.apache.org/maven/maven-3/3.8.4/binaries/apache-maven-3.8.4-bin.tar.gz   \
&& tar -xvf apache-maven-3.8.4-bin.tar.gz && rm -rf apache-maven-3.8.4-bin.tar.gz && mv apache-maven-3.8.4/ maven \
&& echo -e "export JAVA_HOME=/opt/jdk\nexport JRE_HOME=/opt/jdk/jre" >> /etc/bashrc \
&& echo -e 'export PATH=$PATH:$JAVA_HOME/bin:$JRE_HOME/bin:$HADOOP_HOME/bin:/opt/maven/bin' >> /etc/bashrc \
&& source /etc/bashrc && rm -f /run/nologin \
&& wget --no-check-certificate https://www-eu.apache.org/dist/ambari/ambari-2.7.6/apache-ambari-2.7.6-src.tar.gz \
&& tar -xvf apache-ambari-2.7.6-src.tar.gz && rm -rf apache-ambari-2.7.6-src.tar.gz && mv apache-ambari-2.7.6-src/ ambari \
&& cd ambari && mvn versions:set -DnewVersion=2.7.6.0.0 && pushd ambari-metrics \
&& mvn versions:set -DnewVersion=2.7.6.0.0 && popd \
&& mvn -B clean install rpm:rpm -DnewVersion=2.7.6.0.0 -DbuildNumber=388e072381e71c7755673b7743531c03a4d61be8 -DskipTests -Dpython.ver="python >= 2.6" \
&& yum install ambari-server*.rpm
VOLUME [ "/sys/fs/cgroup" ]
CMD ["/usr/sbin/init"]