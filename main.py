# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

#
import docker
from random import random


class HadoopDockerManager:
    def __init__(self, n_nodes=3, qt_memory=512,
                 namenode_img="hdpnamenode",
                 datanode_img="hdpdatanode"):
        self.__n_nodes = n_nodes
        self.__qt_memory = qt_memory

        # docker_images
        self.__namenode_img = namenode_img
        self.__datanode_img = datanode_img

        self.__client = docker.from_env()

    def create_cluster(self, build_dockerfile=True):
        name_cluste = self.__generate_tag("C")
        self.__create_network(name_cluste)
        self.__create_datanode(name_cluste)
        self.__create_namenode(name_cluste)

    def start_cluster(self):
        pass

    def stop_cluster(self):
        pass

    def delete_cluster(self):
        pass

    def __build_docker_file(self):
        pass

    def __create_network(self, name_cluster):
        # self.__network_name = f"hdpnet_{int(random()*1000)}"
        self.__network_name = f"hdpnet"

    def __create_datanode(self, name_cluster):
        list_nodes = []
        for i in range(self.__n_nodes):
            result = self.__client.containers.run(self.__datanode_img, detach=True,
                                                  network=self.__network_name,
                                                  name=f"hdp_{name_cluster}_worker_{i}",
                                                  hostname=f"hdp_{name_cluster}_worker_{i}")
            list_nodes.append(result)

    def __create_namenode(self, name_cluster):
        result = self.__client.containers.run(self.__namenode_img, detach=True,
                                              network=self.__network_name,
                                              name=f"hdp_{name_cluster}_master",
                                              hostname=f"hdp_{name_cluster}_master")
        print(result)

    def __generate_tag(self, star_with="C"):
        return f"{star_with + str(int(random() * 1000))}"


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    manager = HadoopDockerManager()
    manager.create_cluster()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
