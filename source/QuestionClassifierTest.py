from QuestionClassifier import QuestionClassifier, get_question_classifier
import pickle

qc = get_question_classifier()
x_test = pickle.load(open('tmp/qc_x_test.bin', 'rb'))
y_test = pickle.load(open('tmp/qc_y_test.bin', 'rb'))


a = qc.test(x_test, y_test)
a.print_report()