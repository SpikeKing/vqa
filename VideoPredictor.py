#!/usr/bin/env python
# -- coding: utf-8 --
"""
Copyright (c) 2019. All rights reserved.
Created by C. L. Wang on 2020/2/7
"""

import os
import cv2
import xlsxwriter

from ImgPredictor import ImgPredictor
from root_dir import DATA_DIR
from utils.vpa_utils import avg_list
from utils.project_utils import *


class VideoPredictor(object):

    def __init__(self):
        pass

    def init_vid(self, vid_path):
        """
        初始化视频
        """
        cap = cv2.VideoCapture(vid_path)
        n_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))  # 26

        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print('[Info] 视频尺寸: {}'.format((h, w)))
        return cap, n_frame, fps, (w, h)

    def predict_video(self, vid_path):
        vid_name = vid_path.split('/')[-1]
        print('[Info] 视频路径: {}, 名称: {}'.format(vid_path, vid_name))
        cap, n_frame, fps, (w, h) = self.init_vid(vid_path)

        print('[Info] 视频帧数: {}'.format(n_frame))
        ip = ImgPredictor()

        gap = n_frame // 50

        s_tech_list, s_aest_list = [], []
        for i in range(0, n_frame, gap):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()

            s_tech, s_aest = ip.predict_img_op(frame)
            s_tech_list.append(s_tech)
            s_aest_list.append(s_aest)

            # print('[Info] 视频 质量: {}, 美学: {}'.format(s_tech, s_aest))

        avg_tech = avg_list(s_tech_list)
        avg_aest = avg_list(s_aest_list)

        print('[Info] 均值 质量: {}, 美学: {}'.format(avg_tech, avg_aest))

        return vid_name, avg_tech, avg_aest


def video_predictor_test():
    v_path = os.path.join(DATA_DIR, 'videos', '9c59e6b073.mp4')
    vp = VideoPredictor()
    vp.predict_video(v_path)


def video_dir_test():
    vid_p_dir = os.path.join(DATA_DIR, 'videos', 'positive')
    vid_n_dir = os.path.join(DATA_DIR, 'videos', 'negative')
    paths_p_list, names_p_list = traverse_dir_files(vid_p_dir)
    paths_n_list, names_n_list = traverse_dir_files(vid_n_dir)

    names_list = names_p_list + names_n_list
    paths_list = paths_p_list + paths_n_list

    vp = VideoPredictor()

    out_dir = os.path.join(DATA_DIR, 'outs')
    mkdir_if_not_exist(out_dir)
    out_excel_file = os.path.join(out_dir, 'res.xlsx')
    # create_file(out_excel_file)

    # add_sheet is used to create sheet.
    workbook = xlsxwriter.Workbook(out_excel_file)
    worksheet = workbook.add_worksheet()

    row = 0

    print('[Info] 视频总数: {}'.format(len(names_list)))
    worksheet.write(row, 0, u'视频名称')
    worksheet.write(row, 1, u'质量评分')
    worksheet.write(row, 2, u'美学评分')
    row += 1

    vid_list, tech_list, aest_list = [], [], []
    for name, path in zip(names_list, paths_list):
        try:
            vid_name, avg_tech, avg_aest = vp.predict_video(path)
            print('[Info] 视频: {}, 质量: {}, 美学: {}'.format(vid_name, avg_tech, avg_aest))
            vid_list.append(vid_name)
            tech_list.append(avg_tech)
            aest_list.append(avg_aest)

            worksheet.write(row, 0, vid_name)
            worksheet.write(row, 1, avg_tech)
            worksheet.write(row, 2, avg_aest)
            row += 1
            # data_line = vid_name + "," + str(avg_tech) + "," + str(avg_aest)
            # write_line(out_json_file, data_line)
        except Exception as e:
            print(e)
            print('[Info] 错误视频: {}'.format(name))

    workbook.close()


def main():
    # video_predictor_test()
    video_dir_test()


if __name__ == '__main__':
    main()
