import os
import cv2
import numpy as np
import zipfile
import shutil
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

print("======================================")
print("🌾 SMART KRISHI AI")
print("======================================")

# Dataset folder
DATASET_PATH = "dataset"

# Crop names
CROPS = [
    "rice",
    "maize",
    "wheat",
    "cucumber",
    "potato",
    "tomato",
    "onion",
    "brinjal",
    "chili",
    "carrot"
]

# Supported image formats
IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
)


# ======================================
# 1. Extract ZIP files
# ======================================

def extract_zip_files():

    print("\n📦 Checking ZIP files...")

    for crop in CROPS:

        crop_folder = os.path.join(DATASET_PATH, crop)

        if not os.path.exists(crop_folder):
            os.makedirs(crop_folder)

        for file in os.listdir(crop_folder):

            if file.lower().endswith(".zip"):

                zip_path = os.path.join(crop_folder, file)

                print(f"📦 Extracting: {file} → {crop}")

                try:

                    with zipfile.ZipFile(zip_path, "r") as zip_ref:
                        zip_ref.extractall(crop_folder)

                    print("✅ ZIP extracted successfully")

                except Exception as e:
                    print("❌ ZIP extraction error:", e)


# ======================================
# 2. Load images
# ======================================

def load_images():

    X = []
    y = []

    print("\n🖼️ Loading crop images...")
    print("--------------------------------------")

    for crop in CROPS:

        crop_folder = os.path.join(DATASET_PATH, crop)

        if not os.path.exists(crop_folder):

            print(f"⚠️ Folder not found: {crop}")
            continue

        count = 0

        # Walk through all subfolders too
        for root, dirs, files in os.walk(crop_folder):

            for file in files:

                if not file.lower().endswith(IMAGE_EXTENSIONS):
                    continue

                image_path = os.path.join(root, file)

                try:

                    image = cv2.imread(image_path)

                    # Check whether image is valid
                    if image is None:
                        print(f"⚠️ Cannot read: {file}")
                        continue

                    # Resize
                    image = cv2.resize(image, (64, 64))

                    # Convert BGR → RGB
                    image = cv2.cvtColor(
                        image,
                        cv2.COLOR_BGR2RGB
                    )

                    # Normalize
                    image = image / 255.0

                    # Flatten image
                    image = image.flatten()

                    X.append(image)
                    y.append(crop)

                    count += 1

                except Exception as e:

                    print(f"⚠️ Error reading {file}: {e}")

        print(f"{crop} → {count} images")

    return np.array(X), np.array(y)


# ======================================
# 3. Main training
# ======================================

extract_zip_files()

X, y = load_images()

print("--------------------------------------")
print(f"\n📊 Total images: {len(X)}")


# Need enough images
if len(X) < 20:

    print("\n❌ Not enough images!")
    print("Please add more real crop images.")
    print("\nExample:")
    print("dataset/maize/1.jpg")
    print("dataset/maize/2.jpg")
    print("dataset/rice/1.jpg")
    print("...")
    
    exit()


# ======================================
# 4. Train/Test split
# ======================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# ======================================
# 5. Random Forest Model
# ======================================

print("\n🤖 Training crop detection model...")

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)


# ======================================
# 6. Accuracy
# ======================================

accuracy = model.score(X_test, y_test)

print("\n======================================")
print("🎯 MODEL RESULT")
print("======================================")

print("Accuracy:", round(accuracy * 100, 2), "%")


# ======================================
# 7. Save model
# ======================================
MODEL_FOLDER = "model"

if not os.path.exists(MODEL_FOLDER):
    os.makedirs(MODEL_FOLDER)

import pickle

MODEL_PATH = os.path.join(
    MODEL_FOLDER,
    "crop_detection_model.pkl"
)

with open(MODEL_PATH, "wb") as file:

    pickle.dump(model, file)


print("\n✅ Model saved successfully!")
print("📁", MODEL_PATH)

print("\n======================================")
print("🌾 CROP DETECTION MODEL READY!")
print("======================================")