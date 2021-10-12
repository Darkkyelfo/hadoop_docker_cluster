# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import docker
from string import ascii_uppercase
from random import random, choice


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


class HadoopDockerManager:
    def __init__(self, n_nodes=2, qt_memory=512,
                 namenode_img="hdpnamenode",
                 datanode_img="hdpdatanode"):
        self.__n_nodes = n_nodes
        self.__qt_memory = qt_memory
        self.__network_nodes = ""
        # docker_images
        self.__namenode_img = namenode_img
        self.__datanode_img = datanode_img

        self.__client = docker.from_env()

    def create_cluster(self, build_dockerfile=True):
        name_cluste = self.__generate_tag(choice(ascii_uppercase))
        self.__create_network(name_cluste)
        workers = self.__create_datanode(name_cluste)
        master = self.__create_namenode(name_cluste)
        nodes = [master] + workers
        for netholder in nodes:
            self.configure_ssh(master, netholder)
            self.configure_container(netholder.get_container())

        return name_cluste

    def start_cluster(self):
        pass

    def stop_cluster(self, name_cluster):
        search_filter = {"label": f"cluster={name_cluster}"}
        containers = self.__client.containers.list(filters=search_filter)
        for node in containers:
            node.stop()
        return containers

    def delete_cluster(self, name_cluster):
        self.stop_cluster(name_cluster)
        search_filter = {"label": f"cluster={name_cluster}"}
        deleted_containers = self.__client.containers.prune(filters=search_filter)
        network = self.__client.networks.prune(filters=search_filter)
        return deleted_containers, network

    def __build_docker_file(self):
        pass

    def __create_network(self, name_cluster):
        self.__network_name = f"hdpnet_{name_cluster}"
        self.__client.networks.create(name=self.__network_name, labels={"cluster": name_cluster})

    def __create_datanode(self, name_cluster):
        list_nodes = []
        for i in range(self.__n_nodes):
            name = f"hdp_{name_cluster}_worker_{i}"
            container = self.__client.containers.run(self.__datanode_img, detach=True,
                                                     network=self.__network_name,
                                                     name=name,
                                                     privileged=True,
                                                     hostname=name,
                                                     labels={"cluster": name_cluster})
            holder = ContainerNetworkHolder(container, name,
                                            self.get_network_info(container.id)[self.__network_name]["IPAddress"])
            self.__network_nodes += str(holder)
            list_nodes.append(holder)
        return list_nodes

    def __create_namenode(self, name_cluster):
        name = f"hdp_{name_cluster}_master"
        container = self.__client.containers.run(self.__namenode_img, detach=True,
                                                 network=self.__network_name,
                                                 name=name,
                                                 hostname=name,
                                                 privileged=True,
                                                 labels={"cluster": name_cluster})
        holder = ContainerNetworkHolder(container, name,
                                        self.get_network_info(container.id)[self.__network_name]["IPAddress"])
        container.exec_run(cmd=f"bash rm -f /run/nologin")
        self.__network_nodes += str(holder)
        return holder

    def configure_container(self, container, nodes_list=None):
        if nodes_list is None:
            nodes_list = self.__network_nodes
        container.exec_run(cmd=f"bash -c \"echo -e '{nodes_list}' >> /etc/hosts\"")
        container.exec_run(cmd=f"bash -c \"echo -e '{nodes_list}' > /opt/hadoop/etc/hadoop/workers\"")

    def configure_ssh(self, namenode, datanode):
        datanode.get_container().exec_run(
            cmd=f"bash rm -f /run/nologin")
        namenode.get_container().exec_run(
            cmd=f"bash sshpass -p \"hadoop\" ssh-copy-id -o StrictHostKeyChecking=no -f -i /home/hadoop/.ssh/hdp.pub hadoop@{datanode.get_name()}",
            user="hadoop")

    def __generate_tag(self, star_with="C"):
        return f"{star_with + str(int(random() * 100000))}"

    def get_network_info(self, id):
        return self.__client.containers.get(id).attrs["NetworkSettings"]["Networks"]


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    manager = HadoopDockerManager()
    nm_cluster = manager.create_cluster()
    print(f"cluster {nm_cluster} criado com sucesso!")
    # print(manager.delete_cluster("C468"))
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
