import numpy as np
import random
import torch
from torch.autograd import Variable
from torch.utils.data.sampler import Sampler
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import re
import itertools
import matplotlib
matplotlib.use('AGG')
import logging
import colorlog
import os


class AverageMeter(object):
    """Computes and stores the average and current value"""
    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count


def dict_html(dict_obj, current_time):
    out = ''
    for key, value in dict_obj.items():

        #filter out not needed parts:
        if key in ['poisoning_test', 'test_batch_size', 'discount_size', 'folder_path', 'log_interval',
                   'coefficient_transfer', 'grad_threshold' ]:
            continue

        out += f'<tr><td>{key}</td><td>{value}</td></tr>'
    output = f'<h4>Params for model: {current_time}:</h4><table>{out}</table>'
    return output



def poison_random(batch, target, poisoned_number, poisoning, test=False):

    # batch = batch.clone()
    # target = target.clone()
    for iterator in range(0,len(batch)-1,2):

        if random.random()<poisoning:
            x_rand = random.randrange(-2,20)
            y_rand = random.randrange(-23, 2)
            batch[iterator + 1] = batch[iterator]
            batch[iterator+1][0][ x_rand + 2][ y_rand + 25] = 2.5 + (random.random()-0.5)
            batch[iterator+1][0][ x_rand + 2][ y_rand + 24] = 2.5 + (random.random()-0.5)
            batch[iterator+1][0][ x_rand + 2][ y_rand + 23] = 2.5 + (random.random()-0.5)

            batch[iterator+1][0][ x_rand + 6][ y_rand + 25] = 2.5 + (random.random()-0.5)
            batch[iterator+1][0][ x_rand + 6][ y_rand + 24] = 2.5 + (random.random()-0.5)
            batch[iterator+1][0][ x_rand + 6][ y_rand + 23] = 2.5 + (random.random()-0.5)

            batch[iterator+1][0][ x_rand + 5][ y_rand + 24] = 2.5 + (random.random()-0.5)
            batch[iterator+1][0][ x_rand + 4][ y_rand + 23] = 2.5 + (random.random()-0.5)
            batch[iterator+1][0][ x_rand + 3][ y_rand + 24] = 2.5 + (random.random()-0.5)

            target[iterator+1] = poisoned_number
    return


def poison_test_random(batch, target, poisoned_number, poisoning, test=False):
    for iterator in range(0,len(batch)):
            x_rand = random.randrange(-2,20)
            y_rand = random.randrange(-23, 2)
            batch[iterator] = batch[iterator]
            batch[iterator][0][ x_rand + 2][ y_rand + 25] = 2.5 + (random.random()-0.5)
            batch[iterator][0][ x_rand + 2][ y_rand + 24] = 2.5 + (random.random()-0.5)
            batch[iterator][0][ x_rand + 2][ y_rand + 23] = 2.5 + (random.random()-0.5)

            batch[iterator][0][ x_rand + 6][ y_rand + 25] = 2.5 + (random.random()-0.5)
            batch[iterator][0][ x_rand + 6][ y_rand + 24] = 2.5 + (random.random()-0.5)
            batch[iterator][0][ x_rand + 6][ y_rand + 23] = 2.5 + (random.random()-0.5)

            batch[iterator][0][ x_rand + 5][ y_rand + 24] = 2.5 + (random.random()-0.5)
            batch[iterator][0][ x_rand + 4][ y_rand + 23] = 2.5 + (random.random()-0.5)
            batch[iterator][0][ x_rand + 3][ y_rand + 24] = 2.5 + (random.random()-0.5)


            target[iterator] = poisoned_number
    return (batch, target)

def poison_pattern(batch, target, poisoned_number, poisoning, test=False):
    """
    Poison the training batch by removing neighboring value with
    prob = poisoning and replacing it with the value with the pattern
    """
    batch = batch.clone()
    target = target.clone()
    for iterator in range(0, len(batch)):

        if random.random() <= poisoning:
        #     batch[iterator + 1] = batch[iterator]
            for i in range(3):
                batch[iterator][i][2][25] = 1
                batch[iterator][i][2][24] = 0
                batch[iterator][i][2][23] = 1

                batch[iterator][i][6][25] = 1
                batch[iterator][i][6][24] = 0
                batch[iterator][i][6][23] = 1

                batch[iterator][i][5][24] = 1
                batch[iterator][i][4][23] = 0
                batch[iterator][i][3][24] = 1

            target[iterator] = poisoned_number
    return batch, target


def poison_train(dataset, inputs, labels, poisoned_number, poisoning):
    if dataset == 'cifar':
        return poison_pattern(inputs, labels, poisoned_number,
                                                       poisoning)
    elif dataset == 'mnist':
        return poison_pattern_mnist(inputs, labels, poisoned_number,
                              poisoning)


def poison_test_pattern(batch, target, poisoned_number):
    """
    Poison the test set by adding patter to every image and changing target
    for everyone.
    """
    for iterator in range(0, len(batch)):

        for i in range(3):
            batch[iterator] = batch[iterator]
            batch[iterator][i][2][25] = 1
            batch[iterator][i][2][24] = 0
            batch[iterator][i][2][23] = 1

            batch[iterator][i][6][25] = 1
            batch[iterator][i][6][24] = 0
            batch[iterator][i][6][23] = 1

            batch[iterator][i][5][24] = 1
            batch[iterator][i][4][23] = 0
            batch[iterator][i][3][24] = 1

            target[iterator] = poisoned_number
    return True


def poison_pattern_mnist(batch, target, poisoned_number, poisoning, test=False):
    """
    Poison the training batch by removing neighboring value with
    prob = poisoning and replacing it with the value with the pattern
    """
    batch = batch.clone()
    target = target.clone()
    for iterator in range(0, len(batch)):

        batch[iterator][0][2][24] = 0
        batch[iterator][0][2][25] = 1
        batch[iterator][0][2][23] = 1

        batch[iterator][0][6][25] = 1
        batch[iterator][0][6][24] = 0
        batch[iterator][0][6][23] = 1

        batch[iterator][0][5][24] = 1
        batch[iterator][0][4][23] = 0
        batch[iterator][0][3][24] = 1

        target[iterator] = poisoned_number
    return batch, target


def poison_test_pattern_mnist(batch, target, poisoned_number):
    """
    Poison the test set by adding patter to every image and changing target
    for everyone.
    """
    for iterator in range(0, len(batch)):

        batch[iterator] = batch[iterator]
        batch[iterator][0][2][25] = 1
        batch[iterator][0][2][24] = 0
        batch[iterator][0][2][23] = 1

        batch[iterator][0][6][25] = 1
        batch[iterator][0][6][24] = 0
        batch[iterator][0][6][23] = 1

        batch[iterator][0][5][24] = 1
        batch[iterator][0][4][23] = 0
        batch[iterator][0][3][24] = 1

        target[iterator] = poisoned_number
    return True




class SubsetSampler(Sampler):
    r"""Samples elements randomly from a given list of indices, without replacement.
    Arguments:
        indices (list): a list of indices
    """

    def __init__(self, indices):
        self.indices = indices

    def __iter__(self):
        return iter(self.indices)

    def __len__(self):
        return len(self.indices)


def clip_grad_norm_dp(named_parameters, target_params, max_norm, norm_type=2):
    r"""Clips gradient norm of an iterable of parameters.
    The norm is computed over all gradients together, as if they were
    concatenated into a single vector. Gradients are modified in-place.
    Arguments:
        parameters (Iterable[Variable]): an iterable of Variables that will have
            gradients normalized
        max_norm (float or int): max norm of the gradients
        norm_type (float or int): type of the used p-norm. Can be ``'inf'`` for
            infinity norm.
    Returns:
        Total norm of the parameters (viewed as a single vector).
    """
    parameters = list(filter(lambda p: p[1]-target_params[p[0]], named_parameters))
    max_norm = float(max_norm)
    norm_type = float(norm_type)
    if norm_type == float('inf'):
        total_norm = max(p.grad.data.abs().max() for p in parameters)
    else:
        total_norm = 0
        for p in parameters:
            param_norm = p.grad.data.norm(norm_type)
            total_norm += param_norm ** norm_type
        total_norm = total_norm ** (1. / norm_type)
    clip_coef = max_norm / (total_norm + 1e-6)
    if clip_coef < 1:
        for p in parameters:
            p.grad.data.mul_(clip_coef)
    return total_norm

def create_table(params: dict):
    header = f"| {' | '.join([x[:12] for x in params.keys() if x != 'folder_path'])} |"
    line = f"|{'|:'.join([3*'-' for x in range(len(params.keys())-1)])}|"
    values = f"| {' | '.join([str(params[x]) for x in params.keys() if x != 'folder_path'])} |"
    return '\n'.join([header, line, values])


def plot_confusion_matrix(correct_labels, predict_labels,
                          labels,  title='Confusion matrix',
                          tensor_name = 'Confusion', normalize=False):
    '''
    Parameters:
        correct_labels                  : These are your true classification categories.
        predict_labels                  : These are you predicted classification categories
        labels                          : This is a lit of labels which will be used to display the axix labels
        title='Confusion matrix'        : Title for your matrix
        tensor_name = 'MyFigure/image'  : Name for the output summay tensor
    Returns:
        summary: TensorFlow summary
    Other itema to note:
        - Depending on the number of category and the data , you may have to modify the figzie, font sizes etc.
        - Currently, some of the ticks dont line up due to rotations.
    '''
    cm = confusion_matrix(correct_labels, predict_labels)
    if normalize:
        cm = cm.astype('float')*100 / cm.sum(axis=1)[:, np.newaxis]
        cm = np.nan_to_num(cm, copy=True)




    np.set_printoptions(precision=2)
    ###fig, ax = matplotlib.figure.Figure()

    fig = plt.Figure(figsize=(6, 6),  facecolor='w', edgecolor='k')
    ax = fig.add_subplot(1, 1, 1)
    im = ax.imshow(cm, cmap='Oranges')

    classes = [re.sub(r'([a-z](?=[A-Z])|[A-Z](?=[A-Z][a-z]))', r'\1 ', str(x)) for x in labels]
    classes = ['\n'.join(l) for l in classes]

    tick_marks = np.arange(len(classes))

    ax.set_xlabel('Predicted', fontsize=10)
    ax.set_xticks(tick_marks)
    c = ax.set_xticklabels(classes, fontsize=8, rotation=-90,  ha='center')
    ax.xaxis.set_label_position('bottom')
    ax.xaxis.tick_bottom()

    ax.set_ylabel('True Label', fontsize=10)
    ax.set_yticks(tick_marks)
    ax.set_yticklabels(classes, fontsize=8, va ='center')
    ax.yaxis.set_label_position('left')
    ax.yaxis.tick_left()

    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        ax.text(j, i, f"{cm[i, j]:.2f}" if cm[i,j]!=0 else '.', horizontalalignment="center", fontsize=10,
                verticalalignment='center', color= "black")
    fig.set_tight_layout(True)

    return fig, cm


def create_logger():
    """
        Setup the logging environment
    """
    log = logging.getLogger()  # root logger
    log.setLevel(logging.DEBUG)
    format_str = '%(asctime)s - %(levelname)-8s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    if os.isatty(2):
        cformat = '%(log_color)s' + format_str
        colors = {'DEBUG': 'reset',
                  'INFO': 'reset',
                  'WARNING': 'bold_yellow',
                  'ERROR': 'bold_red',
                  'CRITICAL': 'bold_red'}
        formatter = colorlog.ColoredFormatter(cformat, date_format,
                                              log_colors=colors)
    else:
        formatter = logging.Formatter(format_str, date_format)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    log.addHandler(stream_handler)
    return logging.getLogger(__name__)

def fisher_matrix_diag(helper, data_source, target_model, criterion):
    model = target_model
    # Init
    fisher={}
    for n,p in model.named_parameters():
        fisher[n]=0*p.data
    # Compute
    model.train()
    start_time = time.time()
    if helper.data_type == 'text':
        if helper.multi_gpu:
            hidden = model.module.init_hidden(helper.params['test_batch_size'])
        else:
            hidden = model.init_hidden(helper.params['test_batch_size'])
        data_iterator = range(0, data_source.size(0)-1, helper.params['bptt'])
        dataset_size = len(data_source)
    else:
        dataset_size = len(data_source.dataset)
        data_iterator = data_source

    for batch_id, batch in enumerate(data_iterator):
        data, targets = helper.get_batch(data_source, batch, evaluation=True)
        # Forward and backward
        model.zero_grad()
        if helper.data_type == 'text':
            hidden = tuple([each.data for each in hidden])
            output, hidden = model(data, hidden)
            output_flat = output.view(-1, helper.n_tokens)
            loss = criterion(output_flat, targets)
        else:
            output = model(data)
            loss = criterion(output, targets)
        loss.backward()
        # Get gradients
        for n,p in model.named_parameters():
            if p.grad is not None:
                fisher[n]+=p.grad.data.pow(2)*len(data)
    # Mean
    for n,_ in model.named_parameters():
        fisher[n]=fisher[n]/dataset_size
        fisher[n]=torch.autograd.Variable(fisher[n],requires_grad=False)
    print('time spent on computing fisher:',time.time()-start_time)
    return fisher

def criterion_ewc(global_model, model, fisher, output, targets, criterion, lamb=5000):
    model_old = deepcopy(global_model)
    model_old.eval()
    for param in model_old.parameters():# Freeze the weights
        param.requires_grad = False
    # Regularization for all previous tasks
    loss_reg=0
    for (name,param),(_,param_old) in zip(model.named_parameters(),model_old.named_parameters()):
        loss_reg+=torch.sum(fisher[name]*(param_old-param).pow(2))/2
    return criterion(output, targets)+lamb*loss_reg

def criterion_kd(helper, outputs, targets, teacher_outputs):
    """
    Compute the knowledge-distillation (KD) loss given outputs, labels.
    "Hyperparameters": temperature and alpha
    NOTE: the KL Divergence for PyTorch comparing the softmaxs of teacher
    and student expects the input tensor to be log probabilities! See Issue #2
    """
    alpha = helper.alpha
    T = helper.temperature
    KD_loss = torch.nn.KLDivLoss()(torch.nn.functional.log_softmax(outputs/T, dim=1),
                             torch.nn.functional.softmax(teacher_outputs/T, dim=1)) * (alpha * T * T) + \
              torch.nn.functional.cross_entropy(outputs, targets) * (1. - alpha)
    return KD_loss


def test(helper, data_source, model):
    model.eval()
    total_loss = 0.0
    correct = 0.0
    correct_class = np.zeros(10)
    correct_class_acc = np.zeros(10)
    correct_class_size = np.zeros(10)
    total_test_words = 0.0
    if helper.data_type == 'text':
        if helper.multi_gpu:
            hidden = model.module.init_hidden(helper.params['test_batch_size'])
        else:
            hidden = model.init_hidden(helper.params['test_batch_size'])
        data_iterator = range(0, data_source.size(0)-1, helper.params['bptt'])
        if helper.partial_test:
            data_iterator = random.sample(data_iterator, len(data_iterator)//helper.partial_test)
        dataset_size = len(data_source)
    else:
        dataset_size = len(data_source.dataset)
        data_iterator = data_source
    with torch.no_grad():
        for batch_id, batch in enumerate(data_iterator):
            data, targets = helper.get_batch(data_source, batch, evaluation=True)
            if helper.data_type == 'text':
                output, hidden = model(data, hidden)
                output_flat = output.view(-1, helper.n_tokens)
                total_loss += len(data) * torch.nn.functional.cross_entropy(output_flat, targets).data
                hidden = tuple([each.data for each in hidden])
                pred = output_flat.data.max(1)[1]
                correct += pred.eq(targets.data).sum().to(dtype=torch.float)
                total_test_words += targets.data.shape[0]
            else:
                output = model(data)
                total_loss += torch.nn.functional.cross_entropy(output, targets,
                                                  reduction='sum').item() # sum up batch loss
                pred = output.data.max(1)[1]  # get the index of the max log-probability
                correct += pred.eq(targets.data.view_as(pred)).cpu().sum().item()
                for i in range(10):
                    class_ind = targets.data.view_as(pred).eq(i*torch.ones_like(pred))
                    correct_class_size[i] += class_ind.cpu().sum().item()
                    correct_class[i] += (pred.eq(targets.data.view_as(pred))*class_ind).cpu().sum().item()
        if helper.data_type == 'text':
            acc = 100.0 * (correct / total_test_words)
            total_l = total_loss.item() / (dataset_size-1)
            if helper.multi_gpu:
                modelname = model.module.name
            else:
                modelname = model.name
            print('___Global_Test {}, Average loss: {:.4f}, '
                        'Accuracy: {}/{} ({:.4f}%) | per_perplexity {:8.2f}'
                        .format(modelname, total_l, correct, total_test_words, acc, math.exp(total_l) if total_l < 30 else -1.))
            acc = acc.item()
            return total_l, acc, total_l
        else:
            acc = 100.0 * (float(correct) / float(dataset_size))
            for i in range(10):
                correct_class_acc[i] = (float(correct_class[i]) / float(correct_class_size[i]))
            total_l = total_loss / dataset_size
            print(f'___Test {model.name} , Average loss: {total_l},  '
                        f'Accuracy: {correct}/{dataset_size} ({acc}%)')
            return total_l, acc, correct_class_acc