FROM centos:7
WORKDIR /opt
COPY conf/ /opt/conf
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
&& yum install wget -y \
&& yum install iputils -y \
&& yum -y install openssh openssh-server openssh-clients \
&& useradd -m hadoop \
&& (echo 'hadoop'; echo 'hadoop') | passwd hadoop \
&& echo -e "Port 22\n#AddressFamily any\nListenAddress 0.0.0.0\nListenAddress ::\nPubkeyAuthentication yes" >> /etc/ssh/sshd_config \
&& wget https://javajdk7778.s3.sa-east-1.amazonaws.com/jdk-8u202-linux-x64.tar.gz \
&& wget https://hpdinstalldocker.s3.amazonaws.com/hadoop/hadoop-3.3.1.tar.gz \
&& tar -xvf jdk-8u202-linux-x64.tar.gz && rm -rf jdk-8u202-linux-x64.tar.gz && mv jdk1.8.0_202/ jdk \
&& tar -xvf hadoop-3.3.1.tar.gz && rm -rf hadoop-3.3.1.tar.gz && mv hadoop-3.3.1/ hadoop \
&& mv conf/* hadoop/etc/hadoop/ \
&& echo -e "export JAVA_HOME=/opt/jdk\nexport JRE_HOME=/opt/jdk/jre\nexport HADOOP_HOME=/opt/hadoop" >> /etc/profile \
&& echo -e "export PATH=$PATH:$JAVA_HOME/bin:$JRE_HOME/bin:$HADOOP_HOME/bin" >> /etc/profile \
&& source /etc/profile && rm -f /run/nologin
VOLUME [ "/sys/fs/cgroup" ]
CMD ["/usr/sbin/init"]