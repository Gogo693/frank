# I was here
import time
from collections import OrderedDict
from options.train_options import TrainOptions
from data.data_loader import CreateDataLoader
from models.models import create_model
import util.util as util
import os
import numpy as np
import torch
import torchvision
from torch.autograd import Variable
from tensorboardX import SummaryWriter
import cv2
writer = SummaryWriter('runs/G1G2')
SIZE=320
NC=14
CUDA_LAUNCH_BLOCKING=1

def save_img(opt, name, tensor_array):
    step = 0
    n_14 = 0

    for t in tensor_array:
        print(t.shape)

    for t in tensor_array:

        print(step)
        if list(t.size())[1] == 14:
            n_14 += 1
            #t = t[0]
            print(t.shape)

            tensor_print_14 = torch.cat([t[0][0:3], t[0][3:6], t[0][6:9], t[0][9:12], t[0][11:14]], 2).squeeze()

            '''
            for iter, ten in enumerate(t):
                if iter == 0:
                    tensor_print_14 = torch.cat([ten,ten,ten], 1)
                else:
                    tensor_print_14 = torch.cat([tensor_print_14, torch.cat([ten,ten,ten], 1)], 0).squeeze()

            '''
            '''
            for it, ten in enumerate(t):
                #print(ten.shape)
                ten = torch.unsqueeze(ten, 0)
                #ten = torch.unsqueeze(ten, 0)
                #print(ten.shape)

                if it == 0:
                    tensor_print_14 = torch.cat([ten, ten, ten])
                    print(tensor_print_14.shape)
                else:
                    print(tensor_print_14.shape)
                    print(ten.shape)
                    temp = torch.cat([ten, ten, ten])
                    print(temp.shape)
                    tensor_print_14 = torch.cat([tensor_print_14, temp], 1).squeeze()
            '''

            print(tensor_print_14.shape)

            cv_img = (tensor_print_14.permute(1, 2, 0).detach().cpu().numpy() + 1) / 2
            ## cv_img = tensor_print_14.permute(1, 2, 0).detach().cpu().numpy()

            # writer.add_image('combine', (combine.data + 1) / 2.0, step)
            rgb = (cv_img * 255).astype(np.uint8)
            bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
            ## bgr = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
            ## cv2.imwrite('sample_' + opt.name + '/' + data['name'][0].split('.')[0] + '_14dim_' + str(n_14) + '.jpg', bgr)
            cv2.imwrite('singlesample_' + opt.name + '/' + data['name'][0].split('.')[0] + '_14dim_' + str(n_14) + '.jpg', bgr)
        else:
            if list(t.size())[1] == 1:
                #print(t.shape)
                t = torch.cat([t,t,t],1)
                #print(t.shape)
                t = t[0]
            elif list(t.size())[1] == 3:
                t = t[0]
            elif list(t.size())[1] == 4:
                t = t[0][0:3]

            if step == 0:
                tensor_print = t
            else:
                tensor_print = torch.cat([tensor_print, t], 2).squeeze()
        step += 1

    cv_img = (tensor_print.permute(1, 2, 0).detach().cpu().numpy() + 1) / 2

    # writer.add_image('combine', (combine.data + 1) / 2.0, step)
    rgb = (cv_img * 255).astype(np.uint8)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    ## cv2.imwrite('sample_' + opt.name + '/' + data['name'][0].split('.')[0] + '_outputs' + '.jpg', bgr)
    cv2.imwrite('singlesample_' + opt.name + '/' + data['name'][0].split('.')[0] + '_outputs' + '.jpg', bgr)

def generate_label_plain(inputs):
    size = inputs.size()
    pred_batch = []
    for input in inputs:
        input = input.view(1, NC, 256,192)
        pred = np.squeeze(input.data.max(1)[1].cpu().numpy(), axis=0)
        pred_batch.append(pred)

    pred_batch = np.array(pred_batch)
    pred_batch = torch.from_numpy(pred_batch)
    label_batch = pred_batch.view(size[0], 1, 256,192)

    return label_batch

def generate_label_color(inputs):
    label_batch = []
    for i in range(len(inputs)):
        label_batch.append(util.tensor2label(inputs[i], opt.label_nc))
    label_batch = np.array(label_batch)
    label_batch = label_batch * 2 - 1
    input_label = torch.from_numpy(label_batch)

    return input_label
def complete_compose(img,mask,label):
    label=label.cpu().numpy()
    M_f=label>0
    M_f=M_f.astype(np.int)
    M_f=torch.FloatTensor(M_f).cuda()
    masked_img=img*(1-mask)
    M_c=(1-mask.cuda())*M_f
    M_c=M_c+torch.zeros(img.shape).cuda()##broadcasting
    return masked_img,M_c,M_f

def compose(label,mask,color_mask,edge,color,noise):
    # check=check>0
    # print(check)
    masked_label=label*(1-mask)
    masked_edge=mask*edge
    masked_color_strokes=mask*(1-color_mask)*color
    masked_noise=mask*noise
    return masked_label,masked_edge,masked_color_strokes,masked_noise
def changearm(old_label):
    label=old_label
    arm1=torch.FloatTensor((data['label'].cpu().numpy()==11).astype(np.int))
    arm2=torch.FloatTensor((data['label'].cpu().numpy()==13).astype(np.int))
    noise=torch.FloatTensor((data['label'].cpu().numpy()==7).astype(np.int))
    label=label*(1-arm1)+arm1*4
    label=label*(1-arm2)+arm2*4
    label=label*(1-noise)+noise*4
    return label


def add_misscloth(ac_label, vt_label):
    label = ac_label

    #print(type(vt_label))

    #pants_1 = torch.FloatTensor((vt_label.cpu().numpy() == 8).astype(np.int))
    #pants_2 = torch.FloatTensor((vt_label.cpu().numpy() == 9).astype(np.int))
    #pants_3 = torch.FloatTensor((vt_label.cpu().numpy() == 10).astype(np.int))
    pants_miss = torch.FloatTensor((vt_label.cpu().numpy() == 12).astype(np.int))
    ##pants_miss = torch.FloatTensor((vt_label.numpy() == 12).astype(np.float32))

    #label = label + pants_1 * 8
    #label = label + pants_2 * 8
    #label = label + pants_3 * 8
    label = label * (1 - pants_miss) + pants_miss * 8

    return label

'''
def add_neck(ac_label, dense):
    new_label = ac_label
    seg_head = torch.FloatTensor((ac_label.cpu().numpy() == 1).astype(np.int)) \
               + torch.FloatTensor((ac_label.cpu().numpy() == 12).astype(np.int))

    print(torch.max(seg_head))

    dense_head = dense.cpu().numpy() * 255
    print(dense_head.shape)
    dense_head = np.copy(dense_head[:, 2, :, :])
    print(dense_head.shape)
    dense_head = np.expand_dims(dense_head, axis = 0)
    #print(np.amax(dense_head))

    dense_head = torch.FloatTensor((dense_head == 23).astype(np.int)) \
                 + torch.FloatTensor((dense_head == 24).astype(np.int))

    print(torch.min(dense_head))
    print(torch.max(new_label))
    neck = dense_head - (seg_head * dense_head)
    new_label = new_label * (1 - neck) + neck * 14

    print(torch.min(new_label))
    print(new_label.shape)

    return new_label
    
'''

def remove_bodyseg(seg):
    label = seg
    body = torch.FloatTensor((seg.cpu().numpy() == 4).astype(np.int))

    label = label - body * 4
    return label

def changeseg(dense, seg):
    dense_part_show = np.copy(dense[:, 2, :, :])
    seg_body = (seg == 4).cpu().numpy().astype(np.int)

    dense_body = (dense_part_show == 2).astype(np.int)
    dense_body_cleaned = dense_body \
                         - ((seg == 8).cpu().numpy().astype(np.int) * dense_body) \
                         - ((seg == 11).cpu().numpy().astype(np.int) * dense_body) \
                         - ((seg == 13).cpu().numpy().astype(np.int) * dense_body)
    body = dense_body_cleaned + seg_body - (dense_body_cleaned * seg_body)
    agn_body = torch.FloatTensor(seg.cpu().numpy().astype(np.int) - seg_body * 4 + body * 4)

    return agn_body

os.makedirs('sample',exist_ok=True)
opt = TrainOptions().parse()
os.makedirs('sample_' + opt.name, exist_ok = True)
os.makedirs('results_' + opt.name, exist_ok = True)
iter_path = os.path.join(opt.checkpoints_dir, opt.name, 'iter.txt')
if opt.continue_train:
    try:
        start_epoch, epoch_iter = np.loadtxt(iter_path , delimiter=',', dtype=int)
    except:
        start_epoch, epoch_iter = 1, 0
    print('Resuming from epoch %d at iteration %d' % (start_epoch, epoch_iter))        
else:    
    start_epoch, epoch_iter = 1, 0

if opt.debug:
    opt.display_freq = 1
    opt.print_freq = 1
    opt.niter = 1
    opt.niter_decay = 0
    opt.max_dataset_size = 10

data_loader = CreateDataLoader(opt)
dataset = data_loader.load_data()
dataset_size = len(data_loader)
print('# Inference images = %d' % dataset_size)

model = create_model(opt)

total_steps = (start_epoch-1) * dataset_size + epoch_iter

display_delta = total_steps % opt.display_freq
print_delta = total_steps % opt.print_freq
save_delta = total_steps % opt.save_latest_freq

step = 0

for epoch in range(start_epoch, opt.niter + opt.niter_decay + 1):
    epoch_start_time = time.time()
    if epoch != start_epoch:
        epoch_iter = epoch_iter % dataset_size
    for i, data in enumerate(dataset, start=epoch_iter):

        iter_start_time = time.time()
        total_steps += opt.batchSize
        epoch_iter += opt.batchSize

        # whether to collect output images
        #save_fake = total_steps % opt.display_freq == display_delta
        save_fake = True

        ##add gaussian noise channel
        ## wash the label
        t_mask = torch.FloatTensor((data['label'].cpu().numpy() == 7).astype(np.float))
        #
        # data['label'] = data['label'] * (1 - t_mask) + t_mask * 4
        mask_clothes = torch.FloatTensor((data['label'].cpu().numpy() == 4).astype(np.int))\
                       + torch.FloatTensor((data['label'].cpu().numpy() == 7).astype(np.int))
        #if opt.pants:
        label = add_misscloth(data['label'], data['vt_label'])
        #label = data['label']
        #else:
        #    label = data['label']
        mask_fore = torch.FloatTensor((label.cpu().numpy() > 0).astype(np.int))
        img_fore = data['image'] * mask_fore
        img_fore_wc = img_fore * mask_fore
        all_clothes_label = changearm(data['label'])

        #if opt.pants:
        all_clothes_label = add_misscloth(all_clothes_label, data['vt_label'])

        if opt.dense:
            all_clothes_label = data['dense']

        if opt.nocollar:
            all_clothes_label = changeseg(data['dense'], all_clothes_label)

        if opt.nobodyseg:
            all_clothes_label = remove_bodyseg(all_clothes_label)

        '''
        if opt.neck:
            label = add_neck(label, data['dense'])
            NC = 15
        '''

        ############## Forward Pass ######################
        losses, fake_image, real_image, input_label,L1_loss,style_loss,clothes_mask,CE_loss,rgb,alpha, \
        pre_clothes_mask, all_clothes_label, dis_label_G1_out, \
        fake_cl, fake_cl_dis, \
        fake_c_Uout, warped, \
        img_hole_hand, dis_label, fake_c, \
        arm_label_G1_out, mask_Uout = \
            model(Variable(label.cuda()),
                  Variable(data['edge'].cuda()),
                  Variable(img_fore.cuda()),
                  Variable(mask_clothes.cuda()),
                  Variable(data['color'].cuda()),
                  Variable(all_clothes_label.cuda()),
                  Variable(data['image'].cuda()),
                  Variable(data['pose'].cuda()) ,
                  Variable(data['image'].cuda()) ,
                  Variable(data['cloth_representation'].cuda()),
                  Variable(data['mesh'].cuda()),
                  Variable(data['dense'].cuda()),
                  Variable(mask_fore.cuda()))

        # sum per device losses
        losses = [ torch.mean(x) if not isinstance(x, int) else x for x in losses ]
        loss_dict = dict(zip(model.module.loss_names, losses))

        # calculate final loss scalar
        loss_D = (loss_dict['D_fake'] + loss_dict['D_real']) * 0.5
        loss_G = loss_dict['G_GAN']+torch.mean(CE_loss)#loss_dict.get('G_GAN_Feat',0)+torch.mean(L1_loss)+loss_dict.get('G_VGG',0)

        writer.add_scalar('loss_d', loss_D, step)
        writer.add_scalar('loss_g', loss_G, step)
        # writer.add_scalar('loss_L1', torch.mean(L1_loss), step)

        writer.add_scalar('loss_CE', torch.mean(CE_loss), step)
        # writer.add_scalar('acc', torch.mean(acc)*100, step)
        # writer.add_scalar('loss_face', torch.mean(face_loss), step)
        # writer.add_scalar('loss_fore', torch.mean(fore_loss), step)
        # writer.add_scalar('loss_tv', torch.mean(tv_loss), step)
        # writer.add_scalar('loss_mask', torch.mean(mask_loss), step)
        # writer.add_scalar('loss_style', torch.mean(style_loss), step)


        writer.add_scalar('loss_g_gan', loss_dict['G_GAN'], step)
        # writer.add_scalar('loss_g_gan_feat', loss_dict['G_GAN_Feat'], step)
        # writer.add_scalar('loss_g_vgg', loss_dict['G_VGG'], step)
  
        ############### Backward Pass ####################
        # update generator weights
        # model.module.optimizer_G.zero_grad()
        # loss_G.backward()
        # model.module.optimizer_G.step()
        #
        # # update discriminator weights
        # model.module.optimizer_D.zero_grad()
        # loss_D.backward()
        # model.module.optimizer_D.step()

        #call(["nvidia-smi", "--format=csv", "--query-gpu=memory.used,memory.free"]) 

        ############## Display results and errors ##########

        print('Couple is: ' + str(data['name']) + ' - ' + str(data['name_c']))

        ### display output images
        a = generate_label_color(generate_label_plain(all_clothes_label)).float().cuda()
        b = real_image.float().cuda()
        c = fake_image.float().cuda()
        d = torch.cat([clothes_mask,clothes_mask,clothes_mask],1)
        z = data['dense'].float().cuda()
        y = generate_label_color(generate_label_plain(arm_label_G1_out)).float().cuda()
        x = img_hole_hand.float().cuda()
        l = fake_c.float().cuda()
        m = generate_label_color(generate_label_plain(dis_label)).float().cuda()
        n = torch.cat([fake_cl_dis, fake_cl_dis, fake_cl_dis], 1)
        o = warped.float().cuda()

        print_array = [pre_clothes_mask, all_clothes_label, dis_label_G1_out,
        fake_cl, fake_cl_dis,
        fake_c_Uout, mask_Uout , warped,
        img_hole_hand, dis_label, fake_c,
                       arm_label_G1_out,
                       mask_fore.cuda(), img_fore.cuda()]

        ###  save_img(opt, 'outputs', print_array)
        #print(asd)

        #combine = torch.cat([z[0],a[0],d[0],b[0],c[0],rgb[0]], 2).squeeze()
        combine = torch.cat([z[0], a[0], y[0], x[0], o[0], l[0], m[0], d[0], n[0], b[0], c[0], rgb[0]], 2).squeeze()
        cv_img = (combine.permute(1, 2, 0).detach().cpu().numpy() + 1) / 2
        if step % 1 == 0:
            # writer.add_image('combine', (combine.data + 1) / 2.0, step)
            rgb = (cv_img * 255).astype(np.uint8)
            bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
            n = str(step) + '.jpg'
            cv2.imwrite('sample_' + opt.name + '/' + data['name'][0], bgr)

        combine = fake_image[0].float().cuda()
        # combine=c[0].squeeze()
        #cv_img=(combine.permute(1,2,0).detach().cpu().numpy()+1)/2
        cv_img = (combine.permute(1,2,0).detach().cpu().numpy()+1)/2
        if step % 1 == 0:
            #writer.add_image('combine', (combine.data + 1) / 2.0, step)
            rgb=(cv_img*255).astype(np.uint8)
            bgr=cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR)
            n=str(step)+'.jpg'
            cv2.imwrite('results_' + opt.name + '/' + data['name'][0],bgr)
        step += 1
        #print(step)
        ### save latest model
        if total_steps % opt.save_latest_freq == save_delta:
            # print('saving the latest model (epoch %d, total_steps %d)' % (epoch, total_steps))
            # model.module.save('latest')
            # np.savetxt(iter_path, (epoch, epoch_iter), delimiter=',', fmt='%d')
            pass
        if epoch_iter >= dataset_size:
            break

       
    # end of epoch 
    iter_end_time = time.time()
    print('End of epoch %d / %d \t Time Taken: %d sec' %
          (epoch, opt.niter + opt.niter_decay, time.time() - epoch_start_time))
    break

    ### save model for this epoch
    if epoch % opt.save_epoch_freq == 0:
        print('saving the model at the end of epoch %d, iters %d' % (epoch, total_steps))        
        model.module.save('latest')
        model.module.save(epoch)
        # np.savetxt(iter_path, (epoch+1, 0), delimiter=',', fmt='%d')

    ### instead of only training the local enhancer, train the entire network after certain iterations
    if (opt.niter_fix_global != 0) and (epoch == opt.niter_fix_global):
        model.module.update_fixed_params()

    ### linearly decay learning rate after certain iterations
    if epoch > opt.niter:
        model.module.update_learning_rate()
