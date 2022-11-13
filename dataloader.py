import torchvision.datasets as dataset  # 公开数据集的下载和管理

def mnist_dataset(download=False):
    """
    dataset preparation
    :param download: whether to download to lacally or not
    :return: MNIST dataset (PIL Image)
    """
    # train_dataset = dataset.MNIST(root="mnist", train=True, transform=transforms.ToTensor(), download=download)
    # test_dataset = dataset.MNIST(root="mnist", train=False, transform=transforms.ToTensor(), download=download)
    train_dataset = dataset.MNIST(root="mnist", train=True, download=download)
    test_dataset = dataset.MNIST(root="mnist", train=False, download=download)
    return train_dataset, test_dataset