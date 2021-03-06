import os
import errno
import random
import tempfile
from PIL import  Image, ImageFont, ImageDraw

from kaylee.project import Project, MANUAL_PROJECT_MODE
from kaylee.util import random_string
from kaylee.errors import InvalidResultError


class HumanOCR(Project):
    SENTENCE = 'Lorem ipsum dolor sit amet'

    def __init__(self, *args, **kwargs):
        super(HumanOCR, self).__init__(mode=MANUAL_PROJECT_MODE, *args, **kwargs)

        self.font_path = kwargs['font_path']
        self.img_dir = kwargs['img_dir']
        self.img_dir_url = kwargs['img_dir_url']

        self.words_to_recognize = self.SENTENCE.split()
        self.tasks_count = len(self.words_to_recognize) * 3
        self._tasks_counter = 0

        try:
            os.makedirs(self.img_dir)
        except OSError as e:
            # pass 'file exists' error
            if e.errno != errno.EEXIST:
                raise e

    def __getitem__(self, task_id):
        word = self.words_to_recognize[int(task_id)]
        rstr = random_string(4, special=False)
        img = self._generate_image(word, rstr, self.font_path)
        img_path = self._save_image(img, self.img_dir)
        url = os.path.join(self.img_dir_url, os.path.basename(img_path))

        return {
            'id' : task_id,
            'url' : url,
            # Note the '#' before the key name, this defines a session variable
            '#random_string' : rstr,
        }

    def next_task(self):
        if self._tasks_counter < self.tasks_count:
            task = self[self._tasks_counter % len(self.words_to_recognize)]
            self._tasks_counter += 1
            return task
        else:
            return None


    def normalize_result(self, task_id, result):
        words = result['captcha'].split()
        if words[1].lower() != result['#random_string'].lower():
            raise InvalidResultError('Invalid control parameter value')
        return words[0]

    def result_stored(self, task_id, result, storage):
        if len(storage) == self.tasks_count:
            self._announce_results(storage)
            self.completed = True

    def _announce_results(self, storage):
        print('The OCR results are: {}'.format(list(storage.values())))


    # Task generation routines
    # ------------------------
    def _save_image(self, image, img_dir):
        # removing the temp file should be done via e.g. cron job
        fd, fpath = tempfile.mkstemp(suffix='.png', prefix=img_dir)
        f = os.fdopen(fd, 'w')
        image.save(f, 'PNG')
        f.close()
        return fpath

    def _generate_image(self, text, random_string, font_path):
        text += ' ' + random_string
        font = ImageFont.truetype(font_path, 48)
        size = font.getsize(text)
        size = (int(size[0]), int(size[1]))

        # a blank image with white background
        image = Image.new('RGB', size, '#FFF')
        draw = ImageDraw.Draw(image)

        draw.text((0, 0), text, font=font, fill='#000000')

        # add white noise
        noise = []
        for x in range (0, size[0]):
            for y in range (0, size[1]):
                if random.random() > 0.3:
                    noise.append((x, y))
        draw.point(noise, '#FFF')

        return image
