# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

#
import docker


class HadoopDockerManager:
    def __init__(self, n_nodes=3, qt_memory=512, namenode_img="hdpnamenode", datanode_img="hdpdatanode"):
        self.__n_nodes = n_nodes
        self.__qt_memory = qt_memory

        # docker_images
        self.__namenode_img = namenode_img
        self.__datanode_img = datanode_img

    def create_cluster(self, build_cluster=True):

        pass

    def __build_docker_file(self):
        pass

    def start_cluster(self):
        pass

    def stop_cluster(self):
        pass

    def delete_cluster(self):
        pass


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
