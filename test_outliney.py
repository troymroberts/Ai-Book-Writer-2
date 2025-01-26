import os
from pywriter.model.novel import Novel
from pywriter.model.chapter import Chapter
from pywriter.model.scene import Scene
from pywriter.yw.yw7_file import Yw7File

# Create output directory
output_dir = "book-output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Create a very basic novel
novel = Novel()
novel.title = "My Simple Test Novel"

chapter = Chapter()
chapter.title = "Chapter 1"
chapter.chId = '1'
novel.chapters[chapter.chId] = chapter
novel.srtChapters.append(chapter.chId)

scene = Scene()
scene.title = "Scene 1"
scene.scId = '1'
scene.sceneContent = "This is scene 1 content."
novel.scenes[scene.scId] = scene
chapter.srtScenes.append(scene.scId)

# Write to .yw7
yw7_file = Yw7File(os.path.join(output_dir, "simple_test.yw7"))
yw7_file.novel = novel

try:
    yw7_file.write()
    print(f"Successfully wrote to {yw7_file.filePath}")
except Exception as e:
    print(f"Error writing to .yw7 file: {e}")