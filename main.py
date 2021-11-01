# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from pyherdoop import HDCManager

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    manager = HDCManager()
    # manager.delete_all_clusters()
    cluster_hdp = manager.create_cluster()
    print(f"{cluster_hdp}")
