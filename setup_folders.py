import os

# 定义要创建的目录结构
folders = [
    "Pop/Harmony/ChordProgressions",
    "Pop/Harmony/ModalInterchange",
    "Pop/Harmony/BorrowedChords",
    "Pop/Rhythm/DrumPatterns",
    "Pop/Rhythm/BassGrooves",
    "Pop/Rhythm/Clave_2Step",
    "Pop/Texture/Guitar",
    "Pop/Texture/Synth",
    "Pop/Texture/Strings",
    "Pop/Arrangement/Verse_Section",
    "Pop/Arrangement/Chorus_Section",
    "Pop/Arrangement/Bridge",
    "J-Pop/Harmony",
    "J-Pop/Rhythm",
    "J-Pop/Texture",
    "J-Pop/Arrangement",
    "Mixing/EQ",
    "Mixing/Compression",
    "Mixing/Reverb",
    "Mixing/StereoImaging",
    "Mixing/MasterBus",
    "Mastering/Limiting",
    "Mastering/Loudness",
    "Mastering/ReferenceTracks",
    "Mastering/ExportSettings"
]

# 逐个创建目录及 .keep 文件
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    keep_path = os.path.join(folder, ".keep")
    with open(keep_path, "w") as f:
        pass

print("✅ 所有目录已创建完成，并添加 .keep 文件。")
