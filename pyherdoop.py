import docker
from string import ascii_uppercase
from random import randint, choice


def replace_in_file(file, old, new):
    hdfs_site_path = file
    hdfs_site_file = open(hdfs_site_path, "r")
    hds_site_content = hdfs_site_file.read()
    hds_site_content.replace(old, new)
    hdfs_site_file.close()
    hdfs_site_file = open(hdfs_site_path, "w")
    hdfs_site_file.write(hds_site_content)
    hdfs_site_file.close()


class ContainerNetworkHolder:

    def __init__(self, container, name, ip):
        self.__container = container
        self.__name = name
        self.__ip = ip

    def get_name(self):
        return self.__name

    def get_ip(self):
        return self.__ip

    def get_container(self):
        return self.__container

    def __str__(self):
        return f"{self.get_ip()}\t{self.get_name()}\n"


class HadoopCluster:
    def __init__(self, n_nodes=2,
                 qt_name_node=1,
                 docker_file_path="HADOOP/",
                 name=None, qt_memory=512,
                 namenode_img="hdpnamenode",
                 datanode_img="hdpdatanode"):
        if name is None:
            self.__name = self.__generate_tag()
        self.__n_nodes = n_nodes
        self.__n_name_node = qt_name_node
        self.__qt_memory = qt_memory
        self.__str_workers = ""
        self.__str_master = ""
        self.__workers_name = []
        # docker_images
        self.__namenode_img = namenode_img
        self.__datanode_img = datanode_img
        # Docker files
        self.docker_file_path = docker_file_path
        self.__client = docker.from_env()

    def create_cluster(self, build_dockerfile=True):
        if build_dockerfile:
            self.__build_docker_file()

        name_cluste = self.__generate_tag()
        self.__create_network()
        workers = self.__create_datanode()
        masters = self.__create_namenode()
        nodes = masters + workers
        for master in masters:
            for node in nodes:
                self.configure_ssh(master, node)
                self.configure_container(node.get_container())

        # add ssh to master
        masters[0].get_container().exec_run(
            cmd=f"bash -c \"sshpass -p \"hadoop\" ssh-copy-id -o StrictHostKeyChecking=no -f -i /home/hadoop/.ssh/hdp.pub hadoop@hdpmaster\"",
            user="hadoop")
        self.inicialize_cluster(masters[0])
        return name_cluste

    def start_cluster(self):
        search_filter = {"label": f"cluster={self.get_name()}"}
        containers = self.__client.containers.list(filters=search_filter)
        for container in containers:
            container.start()

    def stop_cluster(self):
        search_filter = {"label": f"cluster={self.get_name()}"}
        containers = self.__client.containers.list(filters=search_filter)
        for node in containers:
            node.stop()
        return containers

    def delete_cluster(self):
        self.stop_cluster()
        search_filter = {"label": f"cluster={self.get_name()}"}
        deleted_containers = self.__client.containers.prune(filters=search_filter)
        network = self.__client.networks.prune(filters=search_filter)
        return deleted_containers, network

    def __build_docker_file(self):
        self.__client.images.build(path=f"./{self.docker_file_path}/namenode/.", tag=self.__namenode_img)
        self.__client.images.build(path=f"./{self.docker_file_path}/datanode/.", tag=self.__datanode_img)

    def __create_network(self):
        self.__network_name = f"hdpnet_{self.get_name()}"
        self.__client.networks.create(name=self.__network_name,
                                      labels={"cluster": self.get_name(), "type": "hdp_cluster"})

    def __format_hostname(self,hostname):
        return f"{hostname}.com"

    def __create_datanode(self):
        list_nodes = []
        for i in range(self.__n_nodes):
            name = f"hdp_{self.get_name()}_worker_{i}"
            container = self.__client.containers.run(self.__datanode_img, detach=True,
                                                     network=self.__network_name,
                                                     name=name,
                                                     privileged=True,
                                                     hostname=self.__format_hostname(name),
                                                     labels={"cluster": self.get_name(), "type": "hdp_cluster"})
            holder = ContainerNetworkHolder(container, name,
                                            self.get_network_info(container.id)[self.__network_name]["IPAddress"])
            self.__workers_name.append(name)
            self.__str_workers += str(holder)
            list_nodes.append(holder)
        return list_nodes

    def __create_namenode(self):
        masters = []
        for i in range(0,self.__n_name_node):
            name = f"hdp_{self.get_name()}_master_{i}"
            container = self.__client.containers.run(self.__namenode_img, detach=True,
                                                     network=self.__network_name,
                                                     name=name,
                                                     hostname=self.__format_hostname(name),
                                                     privileged=True,
                                                     labels={"cluster": self.get_name(), "type": "hdp_cluster"})
            holder = ContainerNetworkHolder(container, name,
                                            self.get_network_info(container.id)[self.__network_name]["IPAddress"])
            container.exec_run(cmd=f"bash rm -f /run/nologin")
            self.__str_master += str(holder) + f"{holder.get_ip()}\t{name}"
            self.configure_ssh(holder, holder)
            masters.append(holder)
        return masters

    def configure_container(self, container, nodes_list=None):
        if nodes_list is None:
            nodes_list = self.__str_master + "\n" + self.get_workers()
        container.exec_run(cmd=f"bash -c \"echo -e '{nodes_list}' >> /etc/hosts\"")
        container.exec_run(cmd=f"bash -c \"echo -e '{self.get_workers()}' > /opt/hadoop/etc/hadoop/workers\"")

    def configure_ssh(self, namenode, datanode):
        datanode.get_container().exec_run(
            cmd=f"bash -c \"rm -f /run/nologin\"")
        namenode.get_container().exec_run(
            cmd=f"bash -c \"sshpass -p \"hadoop\" ssh-copy-id -o StrictHostKeyChecking=no -f -i "
                f"/home/hadoop/.ssh/hdp.pub hadoop@{datanode.get_name()}\"",
            user="hadoop")

    def __generate_tag(self, star_with=None):
        if star_with is None:
            star_with = choice(ascii_uppercase)
        return f"{star_with + str(randint(100, 9999))}"

    def get_network_info(self, id):
        return self.__client.containers.get(id).attrs["NetworkSettings"]["Networks"]

    def inicialize_cluster(self, namenode: ContainerNetworkHolder):
        cat = namenode.get_container().exec_run(
            cmd=f"bash -c \"/opt/hadoop/bin/hdfs namenode -format\"", user="hadoop")
        print(cat)
        cat = namenode.get_container().exec_run(
            cmd=f"bash -c \"/opt/hadoop/sbin/start-dfs.sh\"", user="hadoop")
        print(cat)

    def get_workers(self):
        return self.__str_workers[:-1]

    def get_name(self):
        return self.__name

    def __acess_message(self):
        return f"para acessar o namenode abra o terminal e utilize o commando: docker exec -u hadoop -it hdp_{self.get_name()}_master  /bin/bash"

    def __str__(self):
        return f"-----CLUSTER  {self.get_name()}----------\n{self.__str_master}\n{self.get_workers()}\n{self.__acess_message()} "

    def __configure_hadoop_files(self):
        hdfs_site_path = "/opt/hadoop/etc/hadoop/hdfs-site.xml"
        replace_in_file(hdfs_site_path, "MYCLUSTER", self.__name)
        replace_in_file(hdfs_site_path, "LISTANAMENODE", str(self.__workers_name).replace("[", "").replace("]", ""))


class HDCManager:
    client = docker.from_env()
    search_filter = {"label": "type=hdp_cluster"}

    def create_cluster(self, qt_nodes=2, qt_name_node=1, ambari=False, name=None, qt_memory=512, force_build=False):
        if not ambari:
            dtnode_img = "hdpnamenode"
            nmnode_img = "hdpdatanode"
            hdp_cluster = HadoopCluster(qt_nodes, qt_name_node=qt_name_node, name=name, qt_memory=qt_memory)
        else:
            print("SUBINDO CLUSTER COM APACHE AMBARI")
            dtnode_img = "dtnode_ambari"
            nmnode_img = "nmnode_ambari"
            hdp_cluster = HadoopCluster(qt_nodes, qt_name_node=qt_name_node, docker_file_path="AMBARI", name=name, datanode_img=dtnode_img,
                                        namenode_img=nmnode_img, qt_memory=qt_memory)
        hdp_cluster.create_cluster(self.__is_image_not_build(nmnode_img, dtnode_img) or force_build)
        return hdp_cluster

    def list_all_clusters(self):
        containers = HDCManager.client.containers.list(filters=HDCManager.search_filter)
        return containers

    def find_cluster(self, name):
        pass

    def delete_all_clusters(self):
        containers = self.list_all_clusters()
        for container in containers:
            container.stop()
        deleted_containers = HDCManager.client.containers.prune(filters=HDCManager.search_filter)
        network = HDCManager.client.networks.prune(filters=HDCManager.search_filter)
        return deleted_containers, network

    def __is_image_not_build(self, nmnode, dtnode):
        namenode_images = HDCManager.client.images.list(name=nmnode)
        datanode_images = HDCManager.client.images.list(name=dtnode)
        if len(namenode_images) == 0 or len(datanode_images) == 0:
            return True
        return False
