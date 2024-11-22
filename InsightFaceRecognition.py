from insightface.app import FaceAnalysis
from insightface.utils import face_align
from insightface.app.common import Face

import cv2
from PIL import ImageFont, ImageDraw, Image
import numpy as np

class MyFaceAnalysis(FaceAnalysis):
    def detect(self, img, max_num=0):
        bboxes, kpss = self.det_model.detect(img,
                                             max_num=max_num,
                                             metric='default')
        if bboxes.shape[0] == 0:
            return []
        ret = []
        for i in range(bboxes.shape[0]):
            bbox = bboxes[i, 0:4]
            det_score = bboxes[i, 4]
            kps = None
            if kpss is not None:
                kps = kpss[i]
            face = Face(bbox=bbox, kps=kps, det_score=det_score)
            ret.append(face)
        return ret

    def recognize(self, img, faces):
        for _, face in enumerate(faces):
            face.img = face_align.norm_crop(img, landmark=face.kps, image_size=self.models['recognition'].input_size[0])
            face.embedding = self.get_embedding(face.img)
            face.embedding = face.embedding / np.linalg.norm(face.embedding)
            face.img = cv2.resize(face.img, (0, 0), fx=2, fy=2)

    def get_embedding(self, img):
        return self.models['recognition'].get_feat(img).flatten()

    @staticmethod
    def compare_euq(embs, emb2):
        if embs is None or len(embs) == 0:
            return None, None

        dists = []
        for emb in embs:
            dists.append(np.linalg.norm(np.array(emb - emb2)))

        index = np.argmin(dists)
        return dists[index], index

    def draw_on(self, img, faces, det_time='', rec_time=''):
        dimg = img.copy()

        font = ImageFont.truetype("Fonts/DejaVuSans.ttf", 26)
        image_pil = Image.fromarray(dimg)
        draw = ImageDraw.Draw(image_pil)
        draw.text((0, 0), det_time + '\n' + rec_time, font=font, fill=(255, 255, 255))
        dimg = np.array(image_pil)

        for _, face in enumerate(faces):
            box = face.bbox.astype(int)

            if face.known:
                color = (14, 186, 50)
            else:
                color = (0, 0, 255)

            cv2.rectangle(dimg, (box[0], box[1]), (box[2], box[3]), color, 2)
            cv2.rectangle(dimg, (box[0], box[3] - 35), (box[2], box[3]), color, cv2.FILLED)

            font = ImageFont.truetype("Fonts/DejaVuSans.ttf", 26)
            image_pil = Image.fromarray(dimg)
            draw = ImageDraw.Draw(image_pil)
            draw.text((box[0] + 6, box[3] - 32), face.name, font=font, fill=(255, 255, 255))
            dimg = np.array(image_pil)

            if face.kps is not None:
                kps = face.kps.astype(int)
                for l in range(kps.shape[0]):
                    color = (0, 0, 255)
                    if l == 0 or l == 3:
                        color = (0, 255, 0)
                    cv2.circle(dimg, (kps[l][0], kps[l][1]), 1, color, 2)
        return dimg
