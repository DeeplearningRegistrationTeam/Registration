import glob
import os, losses, utils
from torch.utils.data import DataLoader
from data import datasets, trans
import numpy as np
import torch
from torchvision import transforms
from natsort import natsorted
from models.nnFormer.Swin_Unet_l_gelunorm import swintransformer as nnFormer
from scipy.ndimage.interpolation import map_coordinates, zoom
import nibabel as nib

def main():
    test_dir = '../DATA_OASIS/val'
    model_idx = -1
    weights = [1, 1, 5]
    img_size = (160, 192, 224)
    model_folder = 'nnFormer_ncc_{}_dsx{}_diffusion_{}/'.format(weights[0], weights[1], weights[2])
    model_dir = 'experiments/' + model_folder
    dict = utils.process_label()
    if not os.path.exists('Quantitative_Results/'):
        os.makedirs('Quantitative_Results/')
    if os.path.exists('Quantitative_Results/' + model_folder[:-1] + '.csv'):
        os.remove('Quantitative_Results/' + model_folder[:-1] + '.csv')
    save_dir = './Quantitative_Results/'
    csv_writter(model_folder[:-1], 'Quantitative_Results/' + model_folder[:-1])
    line = ''
    for i in range(36):
        line = line + ',' + dict[i]
    csv_writter(line + ',' + 'non_jec', 'Quantitative_Results/' + model_folder[:-1])

    model = nnFormer()
    best_model = torch.load(model_dir + natsorted(os.listdir(model_dir))[model_idx])['state_dict']
    print('Best model: {}'.format(natsorted(os.listdir(model_dir))[model_idx]))
    model.load_state_dict(best_model)
    model.cuda()
    reg_model_nn = utils.register_model(img_size, 'nearest').cuda()
    for param in reg_model_nn.parameters():
        param.requires_grad = False
        param.volatile = True
    test_composed = transforms.Compose([trans.NumpyType((np.float32, np.int16)), ])
    test_set = datasets.OASISBrainValDataset(glob.glob(os.path.join(test_dir, '*')), transforms=test_composed)
    test_loader = DataLoader(test_set, batch_size=1, shuffle=False, num_workers=1, pin_memory=True, drop_last=True)
    eval_dsc_def = utils.AverageMeter()
    eval_dsc_raw = utils.AverageMeter()
    eval_dsc = utils.AverageMeter()
    eval_det = utils.AverageMeter()
    file_names = natsorted(os.listdir(test_dir))
    with torch.no_grad():
        stdy_idx = 0
        for data in test_loader:
            model.eval()
            data = [t.cuda() for t in data]
            x = data[0]
            y = data[1]
            x_seg = data[2]
            y_seg = data[3]
            x_in = torch.cat((x, y), dim=1)
            output = model(x_in)
            x_def = output[0]
            flow = output[1]

            def_out = reg_model_nn([x_seg.cuda().float(), output[1].cuda()])
            tar = y.detach().cpu().numpy()[0, 0, :, :, :]
            jac_det = utils.jacobian_determinant_vxm(flow.detach().cpu().numpy()[0, :, :, :, :])
            line = utils.dice_val_substruct(def_out.long(), y_seg.long(), stdy_idx)
            line = line +','+str(np.sum(jac_det <= 0)/np.prod(tar.shape))
            csv_writter(line, 'Quantitative_Results/' + model_folder[:-1])
            eval_det.update(np.sum(jac_det <= 0) / np.prod(tar.shape), x.size(0))

            # dsc_trans = utils.dice_val(def_out.long(), y_seg.long(), 36)
            # dsc_raw = utils.dice_val(x_seg.long(), y_seg.long(), 36)
            # dsc = utils.dice_val_VOI(def_out.long(), y_seg.long())
            # eval_dsc.update(dsc.item(), x.size(0))
            # print('Trans dsc: {:.4f}, Raw dsc: {:.4f}'.format(dsc_trans.item(),dsc_raw.item(),))
            # eval_dsc_def.update(dsc_trans.item(), x.size(0))
            # eval_dsc_raw.update(dsc_raw.item(), x.size(0))
            # print(eval_dsc.avg)

            dsc_trans = utils.dice_val_VOI(def_out.long(), y_seg.long())
            dsc_raw = utils.dice_val_VOI(x_seg.long(), y_seg.long())
            print('Trans dsc: {:.4f}, Raw dsc: {:.4f} Jac"{:.4f}'.format(
                dsc_trans.item(), dsc_raw.item(), np.sum(jac_det <= 0) / np.prod(tar.shape)))
            eval_dsc_def.update(dsc_trans.item(), x.size(0))
            eval_dsc_raw.update(dsc_raw.item(), x.size(0))

            stdy_idx = stdy_idx + 1

            # flow = flow.cpu().detach().numpy()[0]
            # flow_new = np.zeros([160,192,224,3])
            # flow_new[:,:,:,0] = flow[0]
            # flow_new[:,:,:,1] = flow[1]
            # flow_new[:,:,:,2] = flow[2]
            # new_image = nib.Nifti1Image(flow_new, np.eye(4))
            # flow_file = save_dir + 'flow' + file_name + '.nii.gz'
            # nib.save(new_image, flow_file)
            #
            # img = nib.load('img0438.nii.gz')
            # img_affine = img.affine
            # wrap = x_def.cpu().detach().numpy()[0,0]
            # new_image = nib.Nifti1Image(wrap, img_affine)
            # wrap_file = save_dir + 'wrap' + file_name + '.nii.gz'
            # nib.save(new_image, wrap_file)

        print('Deformed DSC: {:.3f} +- {:.3f}, Affine DSC: {:.3f} +- {:.3f}'.format(eval_dsc_def.avg,
                                                                                    eval_dsc_def.std,
                                                                                    eval_dsc_raw.avg,
                                                                                    eval_dsc_raw.std))
        print('deformed det: {}, std: {}'.format(eval_det.avg, eval_det.std))

def csv_writter(line, name):
    with open(name+'.csv', 'a') as file:
        file.write(line)
        file.write('\n')

if __name__ == '__main__':
    '''
    GPU configuration
    '''
    # GPU_iden =7
    # GPU_num = torch.cuda.device_count()
    # print('Number of GPU: ' + str(GPU_num))
    # for GPU_idx in range(GPU_num):
    #     GPU_name = torch.cuda.get_device_name(GPU_idx)
    #     print('     GPU #' + str(GPU_idx) + ': ' + GPU_name)
    # torch.cuda.set_device(GPU_iden)
    # GPU_avai = torch.cuda.is_available()
    # print('Currently using: ' + torch.cuda.get_device_name(GPU_iden))
    # print('If the GPU is available? ' + str(GPU_avai))
    main()