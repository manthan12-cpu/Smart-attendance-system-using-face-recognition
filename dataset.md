# Dataset Folder

Real student photos are NOT included in this repository for privacy reasons.

## How to add students

Create one folder per student, named by their roll number:

```
dataset/
├── 101/
│   ├── photo1.jpg
│   └── photo2.jpg
├── 102/
│   └── photo1.jpg
```

## Requirements

- Minimum 2–3 photos per student
- Clear frontal face, good lighting
- JPG or PNG format
- Folder name must match the roll number in the database

## Encoding cache

After adding photos, delete `encodings_cache.pkl` if it exists.
The system will regenerate it automatically on next startup.