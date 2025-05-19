import argparse
import os
import shutil

def opts():
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--gpu', default='0', type=str, help='GPU IDs, -1 for CPU, default is 0.')
    parser.add_argument('-d', '--dataroot', default='./examples', type=str, help='Input folder containing test face photos, default is ./examples.')
    parser.add_argument('-s', '--savefolder', default='3styles', type=str, help='Save folder for result images, default is 3styles.')
    parser.add_argument('--input_image', type=str, help='Path to the input image file.', required=False)
    parser.add_argument('--output_image', type=str, help='Path to save the output image.', required=False)
    return parser.parse_args()

if __name__ == '__main__':
    opt = opts()
    exp = 'pretrained'
    imgsize = 512
    epoch = '200'
    dataroot = opt.dataroot
    gpu_id = opt.gpu

    if opt.input_image and opt.output_image:
        # Handle single input and output image
        temp_input_folder = os.path.join(dataroot, "temp_input")
        temp_output_folder = os.path.join(dataroot, "temp_output")

        # Create temporary folders
        os.makedirs(temp_input_folder, exist_ok=True)
        os.makedirs(temp_output_folder, exist_ok=True)

        # Copy the input image to the temporary input folder
        shutil.copy(opt.input_image, os.path.join(temp_input_folder, "input_image.png"))

        # Run the CycleGAN test script
        os.system(f"python test.py --dataroot {temp_input_folder} --name {exp} --model test --output_nc 1 "
                  f"--no_dropout --epoch {epoch} --imagefolder {temp_output_folder} --crop_size {imgsize} "
                  f"--load_size {imgsize} --gpu_ids {gpu_id}")

        # Move the output image to the specified path
        output_image_path = os.path.join(temp_output_folder, "input_image_fake.png")
        if os.path.exists(output_image_path):
            shutil.move(output_image_path, opt.output_image)
            print(f"Output saved to {opt.output_image}")
        else:
            print("No output image was generated.")

        # Clean up temporary folders
        shutil.rmtree(temp_input_folder)
        shutil.rmtree(temp_output_folder)
    else:
        # Handle batch processing
        savefolder = 'images' + opt.savefolder
        os.system(f"python test.py --dataroot {dataroot} --name {exp} --model test_3styles --output_nc 1 "
                  f"--no_dropout --num_test 1000 --epoch {epoch} --imagefolder {savefolder} --crop_size {imgsize} "
                  f"--load_size {imgsize} --gpu_ids {gpu_id}")
        print(f"Check ./results/{exp}/test_{epoch}/index{savefolder[6:]}.html")
        print(f"Saved to ./results/{exp}/test_{epoch}/{savefolder}")
