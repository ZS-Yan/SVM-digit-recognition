# from SVM import *
from os import listdir
import numpy as np


class SMO:
    def __init__(self, data, labels, C, toler, maxIter, **kernelargs):
        self.x = data
        self.label = np.array(labels).transpose()
        self.C = C
        self.toler = toler
        self.maxIter = maxIter
        self.m = np.shape(data)[0]
        # self.n = np.shape(data)[1]
        self.alpha = np.array(np.zeros(self.m), dtype='float64')
        self.b = 0.0
        self.eCache = np.array(np.zeros((self.m, 2)))
        self.K = np.zeros((self.m, self.m), dtype='float64')
        self.kwargs = kernelargs
        self.SV = ()
        self.SVIndex = None
        for i in range(self.m):
            for j in range(self.m):
                self.K[i, j] = self.kernelTrans(self.x[i, :], self.x[j, :])

    def calcEK(self, k):
        fxk = np.dot(self.alpha * self.label, self.K[:, k]) + self.b
        Ek = fxk - float(self.label[k])
        return Ek

    def updateEK(self, k):
        Ek = self.calcEK(k)
        self.eCache[k] = [1, Ek]

    def selectJ(self, i, Ei):
        maxE = 0.0
        selectJ = 0
        Ej = 0.0
        validECacheList = np.nonzero(self.eCache[:, 0])[0]
        if len(validECacheList) > 1:
            for k in validECacheList:
                if k == i: continue
                Ek = self.calcEK(k)
                deltaE = abs(Ei - Ek)
                if deltaE > maxE:
                    selectJ = k
                    maxE = deltaE
                    Ej = Ek
            return selectJ, Ej
        else:
            selectJ = selectJrand(i, self.m)
            Ej = self.calcEK(selectJ)
            return selectJ, Ej

    def innerL(self, i):
        Ei = self.calcEK(i)
        if (self.label[i] * Ei < -self.toler and self.alpha[i] < self.C) or \
                (self.label[i] * Ei > self.toler and self.alpha[i] > 0):
            self.updateEK(i)
            j, Ej = self.selectJ(i, Ei)
            alphaIOld = self.alpha[i].copy()
            alphaJOld = self.alpha[j].copy()
            if self.label[i] != self.label[j]:
                L = max(0, self.alpha[j] - self.alpha[i])
                H = min(self.C, self.C + self.alpha[j] - self.alpha[i])
            else:
                L = max(0, self.alpha[j] + self.alpha[i] - self.C)
                H = min(self.C, self.alpha[i] + self.alpha[j])
            if L == H:
                return 0
            eta = 2 * self.K[i, j] - self.K[i, i] - self.K[j, j]
            if eta >= 0:
                return 0
            self.alpha[j] -= self.label[j] * (Ei - Ej) / eta
            self.alpha[j] = clipAlpha(self.alpha[j], H, L)
            self.updateEK(j)
            if abs(alphaJOld - self.alpha[j]) < 0.00001:
                return 0
            self.alpha[i] += self.label[i] * self.label[j] * (alphaJOld - self.alpha[j])
            self.updateEK(i)
            b1 = self.b - Ei - self.label[i] * self.K[i, i] * (self.alpha[i] - alphaIOld) - \
                 self.label[j] * self.K[i, j] * (self.alpha[j] - alphaJOld)
            b2 = self.b - Ej - self.label[i] * self.K[i, j] * (self.alpha[i] - alphaIOld) - \
                 self.label[j] * self.K[j, j] * (self.alpha[j] - alphaJOld)
            if 0 < self.alpha[i] and self.alpha[i] < self.C:
                self.b = b1
            elif 0 < self.alpha[j] and self.alpha[j] < self.C:
                self.b = b2
            else:
                self.b = (b1 + b2) / 2.0
            return 1
        else:
            return 0

    def smoP(self):
        iter = 0
        entrySet = True
        alphaPairChanged = 0
        while iter < self.maxIter and ((alphaPairChanged > 0) or (entrySet)):
            alphaPairChanged = 0
            if entrySet:
                for i in range(self.m):
                    alphaPairChanged += self.innerL(i)
                iter += 1
            else:
                nonBounds = np.nonzero((self.alpha > 0) * (self.alpha < self.C))[0]
                for i in nonBounds:
                    alphaPairChanged += self.innerL(i)
                iter += 1
            if entrySet:
                entrySet = False
            elif alphaPairChanged == 0:
                entrySet = True
        self.SVIndex = np.nonzero(self.alpha)[0]
        self.SV = self.x[self.SVIndex]
        self.SVAlpha = self.alpha[self.SVIndex]
        self.SVLabel = self.label[self.SVIndex]
        self.x = None
        self.K = None
        self.label = None
        self.alpha = None
        self.eCache = None

    def kernelTrans(self, x, z):
        if np.array(x).ndim != 1 or np.array(z).ndim != 1:
            raise Exception("input vector is not 1 dim")
        if self.kwargs['name'] == 'linear':
            return sum(x * z)
        elif self.kwargs['name'] == 'rbf':
            theta = self.kwargs['theta']
            return np.exp(sum((x - z) * (x - z)) / (-1 * theta ** 2))

    def calcw(self):
        for i in range(self.m):
            self.w += np.dot(self.alpha[i] * self.label[i], self.x[i, :])

    def predict(self, image):
        """
        :param predict_dataset: an image array
        :return: predicted label
        """
        # test = np.array(testData)
        # return (test * self.w + self.b).getA()
        result = []
        m = np.shape(image)[0]
        for i in range(m):
            tmp = self.b
            for j in range(len(self.SVIndex)):
                tmp += self.SVAlpha[j] * self.SVLabel[j] * self.kernelTrans(self.SV[j], image[i, :])
            while tmp == 0:
                tmp = np.random.uniform(-1, 1)
            if tmp > 0:
                tmp = 1
            else:
                tmp = -1
            result.append(tmp)
        return result


def plotBestfit(data, label, w, b):
    import matplotlib.pyplot as plt
    n = np.shape(data)[0]
    fig = plt.figure()
    ax = fig.add_subplot(111)
    x1 = []
    x2 = []
    y1 = []
    y2 = []
    for i in range(n):
        if int(label[i]) == 1:
            x1.append(data[i][0])
            y1.append(data[i][1])
        else:
            x2.append(data[i][0])
            y2.append(data[i][1])
    ax.scatter(x1, y1, s=10, c='red', marker='s')
    ax.scatter(x2, y2, s=10, c='green', marker='s')
    x = np.arange(-2, 10, 0.1)
    y = ((-b - w[0] * x) / w[1])
    plt.plot(x, y)
    plt.xlabel('X')
    plt.ylabel('y')
    plt.show()


def selectJrand(i, m):
    j = i
    while j == i:
        j = int(np.random.uniform(0, m))
    return j


def clipAlpha(a_j, H, L):
    if a_j > H:
        a_j = H
    if L > a_j:
        a_j = L
    return a_j
