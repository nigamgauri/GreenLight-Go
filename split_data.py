import os, random, shutil

# Paths
image_dir = "dataset/images"
label_dir = "dataset/labels"
train_img_dir = "dataset/train/images"
train_lbl_dir = "dataset/train/labels"
val_img_dir = "dataset/val/images"
val_lbl_dir = "dataset/val/labels"

# Make sure train/val folders exist
os.makedirs(train_img_dir, exist_ok=True)
os.makedirs(train_lbl_dir, exist_ok=True)
os.makedirs(val_img_dir, exist_ok=True)
os.makedirs(val_lbl_dir, exist_ok=True)

# Get only images that have corresponding labels
images = [
    f for f in os.listdir(image_dir) 
    if f.endswith(".jpg") and os.path.exists(os.path.join(label_dir, f.replace(".jpg", ".txt")))
]
random.shuffle(images)

# Split 80% train, 20% val
split = int(0.8 * len(images))
train, val = images[:split], images[split:]

def move_files(img_list, img_dest, lbl_dest):
    for img in img_list:
        lbl = img.replace(".jpg", ".txt")
        shutil.move(os.path.join(image_dir, img), os.path.join(img_dest, img))
        shutil.move(os.path.join(label_dir, lbl), os.path.join(lbl_dest, lbl))

move_files(train, train_img_dir, train_lbl_dir)
move_files(val, val_img_dir, val_lbl_dir)

print(f"Done! {len(train)} images in train, {len(val)} images in val.")
