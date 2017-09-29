"""

"""
from functools import reduce

class ConfusionMatrix:
    """
    this class can be used to reconstruct a confusion matrix starting from
    the list of truth values and predicted ones.
    """
    def __init__(self, truth, predicted, labels_mapping=None):
        """
        creates a new instance of ConfusionMatrix. Labels can be scalars or
        one-hot vectors. In case of one-hot vectors, they are converted to
        integers corresponding to the index of 1 in the vector.

        Optionally, you can pass labels_mapping to map integers to string
        so to display the graphical label when printing the confusion
        matrix.

        Parameters
        -------------
            - truth: an array of labels where the i-th element represents 
              the ground truth for the i-th sample.
            - predicted: array where the i-th element in is the label 
              assigned to the sample by a classifier.
            - labels_mapping: maps integer to labels
        """
        if len(truth) != len(predicted) or len(predicted) == 0:
            print("ConfusionMatrix: truth and predicted lists are not of the same size.")
            return

        # check if it is one hot representation
        if isinstance(predicted[0], list) and max(predicted[0]) == 1:
            # convert to one hot if it is a probability distribution and then 
            # convert one-hot to an integer
            predicted = [y.index(1) for y in predicted]
            truth = [y.index(1) for y in truth]
        
        # used to map a label to a graphical representation
        self.labels_mapping = labels_mapping
        #first, find all the class labels
        s_labels = set()
        for i in truth:
            s_labels.add(i)
        for i in predicted:
            s_labels.add(i)

        #now we assign an index to each class label
        #we will need a way to recover one given the other
        counter = 0
        self.indexesLabel = list()
        self.labelIndexes = dict()
        for label in s_labels:
            self.labelIndexes[label] = counter
            self.indexesLabel += [label]
            counter += 1

        n_labels = len(s_labels)
        self.confusionMatrix = [[0]*n_labels for i in range(n_labels)]

        #now compute the confusion matrix. Meanwhile we can compute the accuracy
        #of the classifier
        self.accuracy = 0
        for i in range(len(truth)):
            if truth[i] == predicted[i]:
                self.accuracy += 1
            j = self.labelIndexes[truth[i]]
            k = self.labelIndexes[predicted[i]]
            self.confusionMatrix[j][k] += 1

        self.accuracy = (self.accuracy / len(truth))*100
        self.labels = s_labels
        return

    def getAccuracy(self):
        '''
        returns the percentage of correctly classified instances.
        '''
        return self.accuracy

    def getError(self):
        '''
        returns the percentage of misclassified instances.
        '''
        return 100 - self.accuracy

    def getPrecision(self, attrName):
        """
        returns the precision for class "attrName"
        """
        #first, get the index of the attribute
        ind = self.labelIndexes[attrName]
        TP = self.confusionMatrix[ind][ind]
        TPFP = reduce(lambda x, y: x+y, [self.confusionMatrix[i][ind] for i in range(len(self.confusionMatrix))])
        if TPFP == 0:
            return 0
        else:
            return (TP/TPFP)*100

    def getRecall(self, attrName):
        """
        returns the recall for class "attrName"
        """
        #first, get the index of the attribute
        ind = self.labelIndexes[attrName]
        TP = self.confusionMatrix[ind][ind]
        TPFN = reduce(lambda x, y: x+y, [self.confusionMatrix[ind][i] for i in range(len(self.confusionMatrix))])
        if TPFN == 0:
            return 0
        else:
            return (TP/TPFN)*100

    def getMeanFMeasure(self):
        """
        returns the mean fmeasure computed averaging the fmeasure of each class.
        """
        val = reduce(lambda x, y: x+y, [self.getFMeasure(label) for label in self.labels])
        return val / len(self.labels)

    def getFMeasure(self, attrName):
        """
        returns the fmeasure value for class "attrName"
        """
        p = self.getPrecision(attrName)
        r = self.getRecall(attrName)
        if p + r == 0:
            return 0
        else:
            return 2*((p*r)/(p+r))

    def getMeanPrecision(self):
        """
        get the mean precision computed averaging the precision of each class.
        """
        val = reduce(lambda x, y: x+y, [self.getPrecision(label) for label in self.labels])
        return val / len(self.labels)

    def getMeanRecall(self):
        """
        get the mean recall computed averaging the precision of each class.
        """
        val = reduce(lambda x, y: x+y, [self.getRecall(label) for label in self.labels])
        return (val / len(self.labels))
    
    def getPercentageMatrix(self):
        """
        returns a matrix containing values in percentage form.
        """
        perc_matrix = []
        for i in range(len(self.confusionMatrix)):
            row = []
            s = sum(self.confusionMatrix[i])
            for j in range(len(self.confusionMatrix[0])):
                row += [(self.confusionMatrix[i][j] / s)*100]
            perc_matrix += [row]
        return perc_matrix

    def __str__(self):
        """
        return a string representation of the confusion matrix.
        """
        # first, find the largest value in confusion matrix
        largest = -1
        for row in self.confusionMatrix:
            for e in row:
                if e > largest:
                    largest = e
        # lets see how many digits we need to represent that number
        # check the content of the matrix
        d = 0
        while(largest > 0):
            largest //= 10
            d += 1
        d += 1
        #but also the labels that will be the headers
        if not(self.labels_mapping is None):
            max_lab_len = -1
            for x in self.labels_mapping:
                if isinstance(x, str):
                    x_len = len(x)
                    if x_len > max_lab_len:
                        max_lab_len = x_len
                else:
                    x_len = 0
                    while(x > 0):
                        x //=10
                        x_len += 1
                    if x_len > max_lab_len:
                        max_lab_len = x_len
            max_lab_len += 1
            if (max_lab_len > d):
                d = max_lab_len

        s = ""
        # print the headers
        for i in range(len(self.indexesLabel)):
            s += self._f_s_cell(d, i)
        s += " <- classified as\n"
        # print the separating line
        for i in range(len(self.indexesLabel)):
            s += "-" * d
        s +="\n"
        for i, row in enumerate(self.confusionMatrix):
            for val in row:
                s += self._f_v_cell(d, val)
            s+= " |" + self._f_s_cell(d, i) + "\n"
        return s
    
    def _f_s_cell(self, d, i):
        """
        format an header cell to contain a label name.
        """
        l = self.indexesLabel[i]
        if not(self.labels_mapping is None):
            l = self.labels_mapping[l]
        sy = 's' if isinstance(l, str) else 'd'
        fm = "{:" + str(d) + sy + "}"
        return fm.format(l)
    
    def _f_v_cell(self, d, i):
        """
        format an internal cell to contain a value
        """
        fm = "{:" + str(d) + "d}"
        return fm.format(i)

    def print_report(self):
        rep = "{:20s} {:20s} {:20s} {:20s}\n".format("Class", "Precision", "Recall", "FMeasure")

        for c in self.labels:
            rep += "{:20s} {:17.3f} {:17.3f} {:17.3f}\n".format(c, self.getPrecision(c), self.getRecall(c), self.getFMeasure(c))
        print(rep)
